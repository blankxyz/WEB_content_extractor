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
    # HTML清理相关的正则表达式模式
    PATTERNS = {
        'script': r'<[ ]*script.*?\/[ ]*script[ ]*>',  # 移除脚本标签
        'style': r'<[ ]*style.*?\/[ ]*style[ ]*>',    # 移除样式标签
        'meta': r'<[ ]*meta.*?>',                      # 移除meta标签
        'comment': r'<[ ]*!--.*?--[ ]*>',             # 移除HTML注释
        'link': r'<[ ]*link.*?>',                     # 移除link标签
        'base64_img': r'<img[^>]+src="data:image/[^;]+;base64,[^"]+"[^>]*>',  # 替换base64图片
        'svg': r'(<svg[^>]*>)(.*?)(<\/svg>)',         # 替换SVG内容
        'base64_content': r'data:image/[^;]+;base64,[^"]+'  # 检测base64内容
    }
    
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
        # 添加可见性检查的配置
        self.invisible_tags = {'script', 'style', 'link', 'meta'}
        self.invisible_classes = {'hide', 'hidden'}

    def is_visible(self, tag: Tag) -> bool:
        """统一的可见性检查方法"""
        if not isinstance(tag, Tag):
            return False
            
        if tag.name in self.invisible_tags:
            return False
            
        style = tag.get('style', '').lower()
        if 'display:none' in style or 'visibility:hidden' in style:
            return False
            
        classes = {cls.lower() for cls in tag.get('class', [])}
        if classes & self.invisible_classes:  # 使用集合交集判断
            return False
            
        return True

    def get_xpath_x(self, element: Tag) -> str:
        """获取元素的XPath路径"""
        components = []
        child = element
        
        while child and child.parent:
            # 获取当前元素在同类型兄弟节点中的位置
            siblings = child.parent.find_all(child.name, recursive=False)
            if len(siblings) > 1:
                # 处理可能的非闭合标签，使用更可靠的方式计算位置
                position = 0
                for sibling in siblings:
                    if sibling is child:
                        break
                    position += 1
                components.append(f'{child.name}[{position + 1}]')
            else:
                components.append(child.name)
            
            child = child.parent
            # 如果父元素是[document]，停止遍历
            if isinstance(child, BeautifulSoup):
                break
        
        # 反转路径并组合
        xpath = '//' + '/'.join(reversed(components))
        return xpath

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
        """简化的视频播放器检测"""
        if not self.is_visible(element):
            return {'is_player': False}
            
        result = {
            'is_player': False,
            'player_type': None,
            'source_type': None,
            'details': {}
        }
        
        # 检查标签名
        if element.name in self.video_player_patterns['tags']:
            result.update(self._check_video_tag(element))
            
        # 检查类名和ID
        if not result['is_player']:
            result.update(self._check_video_attributes(element))
            
        return result

    def _check_video_tag(self, element: Tag) -> Dict:
        """检查视频相关标签"""
        result = {
            'is_player': True,
            'player_type': self.video_player_patterns['tags'].get(element.name),
            'source_type': None,
            'details': {}
        }
        
        src = element.get('src') or element.get('data-src', '')
        if src:
            result['details']['src'] = src
            result['source_type'] = next(
                (p for p in self.video_player_patterns['src_patterns'] 
                 if re.search(p, src)), 'native'
            )
            
        return result

    def _check_video_attributes(self, element: Tag) -> Dict:
        """检查视频相关属性"""
        classes = set(element.get('class', []))
        element_id = element.get('id', '').lower()
        
        video_classes = {c for c in classes 
                        if any(p.lower() in c.lower() 
                              for p in self.video_player_patterns['classes'])}
                              
        is_video = bool(video_classes) or any(
            p.lower() in element_id 
            for p in self.video_player_patterns['ids']
        )
        
        return {
            'is_player': is_video,
            'player_type': '自定义播放器' if is_video else None,
            'details': {'classes': list(video_classes)} if video_classes else {}
        }

    def analyze_text_and_links(self, element: Tag) -> Dict:
        """分析元素内的文本和链接数量及内容"""
        texts = []
        links = []
        
        # 检查元素是否可见
        def is_visible(tag):
            if not isinstance(tag, Tag):
                return True
            
            style = tag.get('style', '').lower()
            if 'display:none' in style or 'visibility:hidden' in style:
                return False
                
            classes = tag.get('class', [])
            if any('hide' in cls.lower() or 'hidden' in cls.lower() for cls in classes):
                return False
                
            return True
        
        # 只处理可见元素
        if is_visible(element):
            for text in element.stripped_strings:
                if not any(parent.name == 'a' for parent in element.parents):
                    texts.append(text)
            
            for link in element.find_all('a'):
                if is_visible(link):
                    links.append({
                        'text': link.get_text(strip=True),
                        'href': link.get('href', ''),
                        'xpath': self.get_xpath_x(link)
                    })
        
            
        pure_text = ' '.join(texts)
        
        lnks_words_count = sum(len(d['text']) for d in links) 
        word_counts_without_lnks = len(pure_text) - lnks_words_count  
        
        return {
            'text_content': pure_text,
            'text_length': len(pure_text),
            'link_count': len(links),
            'links': links,
            'text_to_link_ratio': len(pure_text) / (lnks_words_count if lnks_words_count>0 else 1),
            'word_counts_without_lnks': word_counts_without_lnks
        }

    def clean_html(self, html: str, clean_svg: bool = False, clean_base64: bool = False) -> str:
        """清理HTML内容，移除不需要的标签和内容"""
        flags = (re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        # 移除不需要的标签
        for pattern_name in ['script', 'style', 'meta', 'comment', 'link']:
            html = re.sub(self.PATTERNS[pattern_name], '', html, flags=flags)
        
        # 处理SVG
        if clean_svg:
            html = self._replace_svg(html)
        
        # 处理base64图片
        if clean_base64:
            html = self._replace_base64_images(html)
        
        return html
    
    def _replace_svg(self, html: str, new_content: str = "this is a placeholder") -> str:
        """替换SVG内容为占位符"""
        return re.sub(
            self.PATTERNS['svg'],
            lambda match: f"{match.group(1)}{new_content}{match.group(3)}",
            html,
            flags=re.DOTALL
        )
    
    def _replace_base64_images(self, html: str, new_image_src: str = "#") -> str:
        """替换base64编码的图片为普通图片链接"""
        return re.sub(
            self.PATTERNS['base64_img'], 
            f'<img src="{new_image_src}"/>', 
            html
        )
    
    def has_base64_images(self, text: str) -> bool:
        """检查文本是否包含base64编码的图片"""
        return bool(re.search(
            self.PATTERNS['base64_content'], 
            text, 
            flags=re.DOTALL
        ))
    
    def has_svg_components(self, text: str) -> bool:
        """检查文本是否包含SVG组件"""
        return bool(re.search(
            self.PATTERNS['svg'], 
            text, 
            flags=re.DOTALL
        ))

    def analyze_structure(self, html_content: str) -> Dict:
        """分析HTML结构并返回带XPath的结果，包含文本、链接和视频播放器分析"""
        html_content = self.clean_html(html_content)
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
            if not self.is_visible(element):
                continue
            
            
            text_link_analysis = self.analyze_text_and_links(element)
            video_analysis = self.detect_video_player(element)
            
            element_info = {
                "xpath": self.get_xpath_x(element),
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

            if not self.is_visible(parent):
                continue
                
            for child in parent.children:
                if not self.is_visible(child):
                    continue
                
                text_link_analysis = self.analyze_text_and_links(child)
                video_analysis = self.detect_video_player(child)
                
                child_info = {
                    "xpath": self.get_xpath_x(child),
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
        if elem['role'] in ['主要内容', '文章', '区块', '普通元素'] and elem['text_analysis']['text_length'] > 0:
            if elem['text_analysis']['link_count'] > 0 and  elem['text_analysis']['word_counts_without_lnks'] >=0 and elem['text_analysis']['word_counts_without_lnks'] < 10:
                # 可能是列表元素
                tag_level1['tags_xpath'].add(elem['xpath'])
            else: 
                # 可能是正文元素
                tag_level1['contents_xpath'].add(elem['xpath'])
                

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
                if elem['text_analysis']['word_counts_without_lnks'] > 10:
                    logger.debug(f"\n ☆☆ 内容元素 ☆☆")
                    
                    # 使用XPath提取当前元素的所有文本节点，排除<a>标签内的文本
                    try:
                        # 获取当前元素
                        element = selector.xpath(elem['xpath'])[0]
                        
                        # 获取所有直接文本节点和非链接元素的文本
                        texts = []
                        for text in element.xpath('.//text()[not(parent::a)]'):
                            text = text.strip()
                            if text:  # 只保留非空文本
                                texts.append(text)
                        
                        pure_text = ' '.join(texts)
                        logger.debug(f"   - XPath: {elem['xpath']}")
                        logger.debug(f"   - 文本内容: {pure_text}")
                        final_report['contents'].add(pure_text)
                    except Exception as e:
                        logger.error(f"XPath提取失败: {e}")
                        final_report['contents'].add(f"XPath提取失败: {e}")
                        continue
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
        logger.error(f"Failed to connect to MySQL: {e}")
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