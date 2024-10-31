import re
from bs4 import BeautifulSoup, Tag
from typing import Dict, List, Tuple
from collections import defaultdict
from loguru import logger
import asyncio
import aiomysql
import json

logger.add("file_{time}.log")

class XPathHTMLAnalyzer:
    """分析HTML中body下两层深度的元素结构，生成XPath，分析链接和文本比例，以及检测视频播放器"""
    
    def __init__(self):
        self.semantic_tags = {
            'header': '页头',
            'nav': '导航',
            'main': '主要内容',
            'article': '文章',
            'section': '区块',
            'aside': '侧边栏',
            'footer': '页脚'
        }
        
        # 视频播放器特征
        self.video_player_patterns = {
            'tags': {
                'video': '原生视频播放器',
                'iframe': 'iframe嵌入播放器'
            },
            'classes': [
                'video-player',
                'player',
                'video-container',
                'video-wrapper',
                'jwplayer',
                'video-js',
                'plyr',
                'mejs-container'  # MediaElement.js
            ],
            'ids': [
                'player',
                'video-player',
                'videoPlayer',
                'youtube-player',
                'youku-player'
            ],
            'src_patterns': [
                r'youtube\.com/embed',
                r'youku\.com/embed',
                r'bilibili\.com/player',
                r'vimeo\.com/video',
                r'iqiyi\.com/player',
                r'player\.youku\.com',
                r'player\.bilibili\.com'
            ]
        }

    def get_xpath(self, element: Tag) -> str:
        """生成元素的XPath路径"""
        components = []
        current = element
        
        while current and current.name != '[document]':
            siblings = current.find_previous_siblings(current.name) if current.name else []
            index = len(list(siblings)) + 1
            
            tag_part = current.name
            
            attributes = []
            if current.get('class'):
                classes = [c for c in current.get('class') if c]
                if classes:
                    attributes.append(f"contains(@class, '{' '.join(classes)}')")
            
            if current.get('id'):
                attributes.append(f"@id='{current.get('id')}'")
            
            if attributes:
                tag_part = f"{current.name}[{' and '.join(attributes)}]"
            
            # if index > 1 or current.find_next_sibling(current.name):
            #     tag_part = f"{tag_part}[{index}]"
            
            components.append(tag_part)
            current = current.parent

        return '//' + '/'.join(reversed(components))

    def get_video_links(self, content):
        # 发送请求获取网页内容
        # response = requests.get(url)
        # soup = BeautifulSoup(response.content, 'html.parser')

        # 查找视频标签
        video_tags = content.find_all(['video', 'iframe', 'embed'])

        # 提取视频文件的链接
        video_links = []
        for tag in video_tags:
            if tag.has_attr('src'):
                video_links.append(tag['src'])
            elif tag.has_attr('srcdoc'):
                video_links.append(tag['srcdoc'])
            elif tag.has_attr('data-src'):
                video_links.append(tag['data-src'])

        return video_links

    def detect_video_player(self, element: Tag) -> Dict:
        """检测元素是否是视频播放器"""
        result = {
            'is_player': False,
            'player_type': None,
            'source_type': None,
            'details': {}
        }
        
        # 检查标签名
        if element.name in self.video_player_patterns['tags']:
            result['is_player'] = True
            result['player_type'] = self.video_player_patterns['tags'][element.name]
            
            # 收集视频源信息
            if element.name == 'video':
                sources = element.find_all('source')
                if sources:
                    result['details']['sources'] = [
                        {'src': src.get('src', ''), 'type': src.get('type', '')}
                        for src in sources
                    ]
                else:
                    result['details']['src'] = element.get('src', '')
                result['source_type'] = 'native'
                
            elif element.name == 'iframe':
                src = element.get('src', '')
                result['details']['src'] = src
                # 检查是否是已知的视频平台
                for pattern in self.video_player_patterns['src_patterns']:
                    if re.search(pattern, src):
                        result['source_type'] = 'embedded'
                        break
        
        # 检查类名
        classes = element.get('class', [])
        matching_classes = [c for c in classes if any(
            pattern.lower() in c.lower() 
            for pattern in self.video_player_patterns['classes']
        )]
        if matching_classes:
            result['is_player'] = True
            result['player_type'] = f"自定义播放器 (class: {', '.join(matching_classes)})"
        
        # 检查ID
        element_id = element.get('id', '')
        if any(pattern.lower() in element_id.lower() for pattern in self.video_player_patterns['ids']):
            result['is_player'] = True
            result['player_type'] = f"自定义播放器 (id: {element_id})"
            
        # 检查data属性
        data_attrs = {k: v for k, v in element.attrs.items() if k.startswith('data-')}
        video_related_data = {k: v for k, v in data_attrs.items() if 'video' in k.lower()}
        if video_related_data:
            result['is_player'] = True
            result['player_type'] = "数据属性视频播放器"
            result['details']['data_attributes'] = video_related_data
            
        return result

    def analyze_text_and_links(self, element: Tag) -> Dict:
        """分析元素内的文本和链接数量及内容"""
        texts = []
        links = []
        
        for text in element.stripped_strings:
            if not any(parent.name == 'a' for parent in element.parents):
                texts.append(text)
        
        for link in element.find_all('a'):
            links.append({
                'text': link.get_text(strip=True),
                'href': link.get('href', ''),
                'xpath': self.get_xpath(link)
            })
            
        pure_text = ' '.join(texts)
        
        text_links = [item['text'] for item in links]
        text_links = ' '.join(text_links)
        
        return {
            'text_content': pure_text,
            'text_length': len(pure_text),
            'link_count': len(links),
            'links': links,
            'text_to_link_ratio': len(pure_text) / (len(text_links) if len(text_links)>0 else 1)
        }

    def analyze_structure(self, html_content: str) -> Dict:
        """分析HTML结构并返回带XPath的结果，包含文本、链接和视频播放器分析"""
        soup = BeautifulSoup(html_content, 'html.parser')
        body = soup.find('body')
        
        if not body:
            return {"error": "No body tag found"}
        
        # video_links = None
        first_level = self._analyze_first_level(body)
        second_level = self._analyze_second_level(body)
        video_links = self.get_video_links(body)

        return {
            "first_level": first_level,
            "second_level": second_level,
            "summary": self._generate_summary(first_level, second_level),
            "video_links": video_links
        }

    def _analyze_first_level(self, body: Tag) -> List[Dict]:
        """分析第一层元素，包含文本、链接和视频播放器分析"""
        first_level = []
        
        for element in body.children:
            if not isinstance(element, Tag):
                continue
                
            if element.name in ['script', 'style', 'link']:
                continue
            
            text_link_analysis = self.analyze_text_and_links(element)
            video_analysis = self.detect_video_player(element)
            
            element_info = {
                "xpath": self.get_xpath(element),
                "tag": element.name,
                "classes": element.get('class', []),
                "id": element.get('id', ''),
                "child_count": len([c for c in element.children if isinstance(c, Tag)]),
                "role": self._get_element_role(element),
                "text_analysis": text_link_analysis,
                "video_player": video_analysis
            }
            
            first_level.append(element_info)
            
        return first_level

    def _analyze_second_level(self, body: Tag) -> List[Dict]:
        """分析第二层元素，包含文本、链接和视频播放器分析"""
        second_level = []
        
        for parent in body.children:
            if not isinstance(parent, Tag):
                continue
                
            if parent.name in ['script', 'style', 'link']:
                continue
                
            for child in parent.children:
                if not isinstance(child, Tag):
                    continue
                    
                if child.name in ['script', 'style', 'link']:
                    continue
                
                text_link_analysis = self.analyze_text_and_links(child)
                video_analysis = self.detect_video_player(child)
                
                child_info = {
                    "xpath": self.get_xpath(child),
                    "tag": child.name,
                    "classes": child.get('class', []),
                    "id": child.get('id', ''),
                    "role": self._get_element_role(child),
                    "parent_tag": parent.name,
                    "parent_xpath": self.get_xpath(parent),
                    "text_analysis": text_link_analysis,
                    "video_player": video_analysis
                }
                
                second_level.append(child_info)
                
        return second_level

    def _get_element_role(self, element: Tag) -> str:
        """获取元素的语义角色"""
        if element.name in self.semantic_tags:
            return self.semantic_tags[element.name]
            
        classes = ' '.join(element.get('class', [])).lower()
        element_id = (element.get('id', '') or '').lower()
        
        for key, value in self.semantic_tags.items():
            if key in classes or key in element_id:
                return value
                
        return '普通元素'

    def _generate_summary(self, first_level: List[Dict], second_level: List[Dict]) -> Dict:
        """生成分析摘要，包含文本、链接和视频播放器统计"""
        total_text_length = 0
        total_links = 0
        video_players = []
        
        # 统计第一层
        for elem in first_level:
            total_text_length += elem['text_analysis']['text_length']
            total_links += elem['text_analysis']['link_count']
            if elem['video_player']['is_player']:
                video_players.append({
                    'xpath': elem['xpath'],
                    'type': elem['video_player']['player_type'],
                    'source_type': elem['video_player']['source_type']
                })
            
        # 统计第二层
        for elem in second_level:
            total_text_length += elem['text_analysis']['text_length']
            total_links += elem['text_analysis']['link_count']
            if elem['video_player']['is_player']:
                video_players.append({
                    'xpath': elem['xpath'],
                    'type': elem['video_player']['player_type'],
                    'source_type': elem['video_player']['source_type']
                })
            
        return {
            "first_level_count": len(first_level),
            "second_level_count": len(second_level),
            "total_elements": len(first_level) + len(second_level),
            "total_text_length": total_text_length,
            "total_links": total_links,
            "overall_text_to_link_ratio": total_text_length / (total_links if total_links else 1),
            "video_players": video_players,
            "video_player_count": len(video_players)
        }

async def print_analysis(data: str) :
    html_content = data['result_text']
    """打印分析结果，包含文本、链接和视频播放器分析"""
    analyzer = XPathHTMLAnalyzer()
    results = analyzer.analyze_structure(html_content)
    from lxml import etree

    selector=etree.HTML(html_content)   # 将源码转化为能被XPath匹配的格式
    # <Element html at 0x29b7fdb6708>
    
    final_report = {
        'videos': set(),
        'links': set(),
        'contents': set()
    }
    
    logger.debug(f"\n=== {data['id']}     HTML结构分析报告（带文本、链接和视频播放器分析） ===\n")
    
    logger.debug("1. 整体统计:")
    logger.debug(f"   - 总文本长度: {results['summary']['total_text_length']} 字符")
    logger.debug(f"   - 总链接数量: {results['summary']['total_links']} 个")
    logger.debug(f"   - 文本/链接比例: {results['summary']['overall_text_to_link_ratio']:.2f}")
    logger.debug(f"   - 视频播放器数量: {results['summary']['video_player_count']} 个")
    
    if results['video_links']:
        logger.debug("\n   检测到的视频链接:")
        # final_report['videos'] = results['video_links']
        for link in results['video_links']:
            final_report['videos'].add(link)
            logger.debug(f"     * 链接: {link}")

    
    logger.debug("\n2. 第一层元素:")
    ret = selector.xpath('/html/body')     # 返回为一列表
    tag_level1 = {'tags_xpath':set(), 'contents_xpath':set()}
    for i, elem in enumerate(results['first_level'], 1):
        if elem['role'] in ['主要内容', '文章', '区块', '普通元素'] and elem['text_analysis']['text_length'] > 50:
            if elem['text_analysis']['link_count'] > 0 and elem['text_analysis']['text_to_link_ratio'] >0.5 and elem['text_analysis']['text_to_link_ratio'] < 2.0:
                # 可能是列表元素
                tag_level1['tags_xpath'].add(elem['xpath'])
            else: 
                # 可能是正文元素
                tag_level1['contents_xpath'].add(elem['xpath'])
                
        logger.debug(f"\n   元素 {i}:")
        logger.debug(f"   - XPath: {elem['xpath']}")
        logger.debug(f"   - 标签: {elem['tag']}")
        logger.debug(f"   - 角色: {elem['role']}")
        logger.debug(f"   - 文本长度: {elem['text_analysis']['text_length']} 字符")
        logger.debug(f"   - 链接数量: {elem['text_analysis']['link_count']} 个")
        logger.debug(f"   - 文本/链接比例: {elem['text_analysis']['text_to_link_ratio']:.2f}")
        # element = html.xpath(elem['xpath'])


    logger.debug("\n3. 第二层元素:")
    for i, elem in enumerate(results['second_level'], 1):
        # if i == 26:
        #     logger.debug('i am here')
        for l1_path in tag_level1['tags_xpath']:
            if l1_path in elem['xpath']:
                if len(elem['text_analysis']['links']) > 0:
                    logger.debug(f"\n  列表 元素 {i}:")
                    logger.debug(f"   - XPath: {elem['xpath']}")
                    final_report['links'].add(elem['xpath'])
                    for link in elem['text_analysis']['links']:
                        logger.debug(f"     * {link['text']} ({link['href']})")
                    
        for l1_path in tag_level1['contents_xpath']:
            if l1_path in elem['xpath']:
                logger.debug(f"\n  内容 元素 {i}:")
                if elem['text_analysis']['text_length'] > 20:
                    final_report['contents'].add(elem['xpath'])
                    logger.debug(f" {elem['text_analysis']['text_length']}")
                    logger.debug(f"   - XPath: {elem['xpath']}")
                
    logger.debug("\n=== L结构分析报告 (结论)===\n")
    return {
        'id': data['id'],
        'videos': list(final_report['videos']),
        # 'links': list(final_report['links']),
        'contents': list(final_report['contents'])
                      
    }
    
async def process_batch(batch):
    return await asyncio.gather(*[print_analysis(data) for data in batch])
async def get_mysql_connection():
    return await aiomysql.connect(
        host='60.205.251.23',  # Replace with your MySQL host
        port=3306,             # Default MySQL port
        user='pom',  # Replace with your MySQL username
        password='Bohui#123', # Replace with your MySQL password
        db='spider_test',
        charset='utf8mb4',
        cursorclass=aiomysql.DictCursor
    )

async def main(concurrency):
    
    try:
        # Connect to MySQL
        conn = await get_mysql_connection()
        async with conn.cursor() as cursor:
            # Fetch data from MySQL - adjust table name as needed
            await cursor.execute('select id, result_text from spider_test.details_test_table dtt')
            mysql_data = await cursor.fetchall()
    except Exception as e:
        logging.error(f"Failed to connect to MySQL: {e}")
        return
    finally:
        conn.close()

    queue = asyncio.Queue()

    # Put data into queue
    for data in mysql_data:
        await queue.put(data)

    finally_rs = []
    tasks = []

    while not queue.empty():
        batch = []
        for _ in range(concurrency):
            if queue.empty():
                break
            batch.append(await queue.get())
        
        if batch:
            task = asyncio.create_task(process_batch(batch))
            tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for batch_result in results:
        if isinstance(batch_result, Exception):
            logger.debug(f"Batch processing error: {batch_result}")
        else:
            finally_rs.extend(batch_result)


        # 将列表保存为 JSON 文件
    with open('data.json', 'w', encoding='utf8') as f:
        json.dump(finally_rs, f, ensure_ascii=False)


if __name__ == '__main__':
    concurrency = 4  # 调整此值以更改并发级别
    asyncio.run(main(concurrency))

                
# 使用示例
# if __name__ == "__main__":
#     sample_html = """
#     """
    
#     print_analysis(sample_html)