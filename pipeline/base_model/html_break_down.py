import re
from bs4 import BeautifulSoup, Tag
from typing import Dict, List, Tuple
from collections import defaultdict
from loguru import logger

logger.add("file_{time}.log")


# ----------------------- clean page ---------------
# (REMOVE <SCRIPT> to </script> and variations)
SCRIPT_PATTERN = r'<[ ]*script.*?\/[ ]*script[ ]*>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML <STYLE> to </style> and variations)
STYLE_PATTERN = r'<[ ]*style.*?\/[ ]*style[ ]*>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML <META> to </meta> and variations)
META_PATTERN = r'<[ ]*meta.*?>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML COMMENTS <!-- to --> and variations)
COMMENT_PATTERN = r'<[ ]*!--.*?--[ ]*>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML LINK <LINK> to </link> and variations)
LINK_PATTERN = r'<[ ]*link.*?>'  # mach any char zero or more times

# (REPLACE base64 images)
BASE64_IMG_PATTERN = r'<img[^>]+src="data:image/[^;]+;base64,[^"]+"[^>]*>'

# (REPLACE <svg> to </svg> and variations)
SVG_PATTERN = r'(<svg[^>]*>)(.*?)(<\/svg>)'


def replace_svg(html: str, new_content: str = "this is a placeholder") -> str:
    return re.sub(
        SVG_PATTERN,
        lambda match: f"{match.group(1)}{new_content}{match.group(3)}",
        html,
        flags=re.DOTALL,
    )


def replace_base64_images(html: str, new_image_src: str = "#") -> str:
    return re.sub(BASE64_IMG_PATTERN, f'<img src="{new_image_src}"/>', html)


def has_base64_images(text: str) -> bool:
    base64_content_pattern = r'data:image/[^;]+;base64,[^"]+'
    return bool(re.search(base64_content_pattern, text, flags=re.DOTALL))


def has_svg_components(text: str) -> bool:
    return bool(re.search(SVG_PATTERN, text, flags=re.DOTALL))


def clean_html(html: str, clean_svg: bool = False, clean_base64: bool = False):
    html = re.sub(SCRIPT_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(STYLE_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(META_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(COMMENT_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(LINK_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

    if clean_svg:
        html = replace_svg(html)

    if clean_base64:
        html = replace_base64_images(html)

    return html


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
        """检测元素是否是视频播放器"""
        result = {
            'is_player': False,
            'player_type': None,
            'source_type': None,
            'details': {}
        }
        
        # 检查标签名和视频相关属性
        if element.name in ['video', 'iframe', 'embed', 'object']:
            result['is_player'] = True
            result['player_type'] = self.video_player_patterns['tags'].get(element.name, '其他播放器')
            
            # 收集视频源信息
            src = element.get('src', '')
            data_src = element.get('data-src', '')
            source_url = src or data_src
            
            if source_url:
                result['details']['src'] = source_url
                # 检查是否是已知的视频平台
                for pattern in self.video_player_patterns['src_patterns']:
                    if re.search(pattern, source_url):
                        result['source_type'] = 'embedded'
                        break
                if not result['source_type']:
                    result['source_type'] = 'native'
                    
            # 检查video标签的source子元素
            if element.name == 'video':
                sources = element.find_all('source')
                if sources:
                    result['details']['sources'] = [
                        {'src': src.get('src', ''), 'type': src.get('type', '')}
                        for src in sources if src.get('src')
                    ]
        
        # 检查类名和ID
        classes = element.get('class', [])
        element_id = element.get('id', '').lower()
        
        video_related_classes = [c for c in classes if any(
            pattern.lower() in c.lower() for pattern in 
            self.video_player_patterns['classes'] + ['video', 'player', 'media']
        )]
        
        video_related_id = any(
            pattern.lower() in element_id for pattern in 
            self.video_player_patterns['ids'] + ['video', 'player', 'media']
        )
        
        if video_related_classes or video_related_id:
            result['is_player'] = True
            if not result['player_type']:
                result['player_type'] = '自定义播放器'
                if video_related_classes:
                    result['details']['classes'] = video_related_classes
                if video_related_id:
                    result['details']['id'] = element_id
        
        # 检查data属性
        data_attrs = {k: v for k, v in element.attrs.items() if k.startswith('data-')}
        video_related_data = {k: v for k, v in data_attrs.items() if any(
            term in k.lower() for term in ['video', 'player', 'media']
        )}
        
        if video_related_data:
            result['is_player'] = True
            if not result['player_type']:
                result['player_type'] = "数据属性视频播放器"
            result['details']['data_attributes'] = video_related_data
                
        return result

    def analyze_text_and_links(self, element: Tag) -> Dict:
        """分析元素内的文本和链接数量及内容"""
        texts = []
        links = []
        
        # for text in element.stripped_strings:
        #     if not any(parent.name == 'a' for parent in element.parents):
        #         texts.append(text)
        
        # for link in element.find_all('a'):
        #     links.append({
        #         'text': link.get_text(strip=True),
        #         'href': link.get('href', ''),
        #         'xpath': self.get_xpath_x(link)
        #     })
        
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
        html_content = clean_html(html_content)
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
        
        def is_visible(tag):
            if not isinstance(tag, Tag):
                return False
                
            if tag.name in ['script', 'style', 'link', 'meta']:
                return False
                
            style = tag.get('style', '').lower()
            if 'display:none' in style or 'visibility:hidden' in style:
                return False
                
            classes = tag.get('class', [])
            if any('hide' in cls.lower() or 'hidden' in cls.lower() for cls in classes):
                return False
                
            return True
        
        for element in body.children:
            # if not isinstance(element, Tag):
            #     continue
                
            # if element.name in ['script', 'style', 'link', 'meta']:
            #     continue
            if not is_visible(element):
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
        
        def is_visible(tag):
            if not isinstance(tag, Tag):
                return False
                
            if tag.name in ['script', 'style', 'link', 'meta']:
                return False
                
            style = tag.get('style', '').lower()
            if 'display:none' in style or 'visibility:hidden' in style:
                return False
                
            classes = tag.get('class', [])
            if any('hide' in cls.lower() or 'hidden' in cls.lower() for cls in classes):
                return False
                
            return True
        
        for parent in body.children:
            # if not isinstance(parent, Tag):
            #     continue
                
            # if parent.name in ['script', 'style', 'link']:
            #     continue
                
            # for child in parent.children:
            #     if not isinstance(child, Tag):
            #         continue
                    
            #     if child.name in ['script', 'style', 'link']:
            #         continue
            if not is_visible(parent):
                continue
                
            for child in parent.children:
                if not is_visible(child):
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



def print_analysis(html_content: str) -> None:
    """打印分析结果，包含文本、链接和视频播放器分析"""
    analyzer = XPathHTMLAnalyzer()
    results = analyzer.analyze_structure(html_content)
    from lxml import etree

    selector=etree.HTML(html_content)   # 将源码转化为能被XPath匹配的格式
    # <Element html at 0x29b7fdb6708>
    
    
    logger.debug("\n=== HTML结构分析报告（带文本、链接和视频播放器分析） ===\n")
    
    logger.debug("1. 整体统计:")
    logger.debug(f"   - 总文本长度: {results['summary']['total_text_length']} 字符")
    logger.debug(f"   - 总链接数量: {results['summary']['total_links']} 个")
    logger.debug(f"   - 文本/链接比例: {results['summary']['overall_text_to_link_ratio']:.2f}")
    logger.debug(f"   - 视频播放器数量: {results['summary']['video_player_count']} 个")
    
    # if results['summary']['video_players']:
    #     logger.debug("\n   检测到的视频播放器:")
    #     for player in results['summary']['video_players']:
    #         logger.debug(f"     * 类型: {player['type']}")
    #         logger.debug(f"       XPath: {player['xpath']}")
    #         if player['source_type']:
    #             logger.debug(f"       来源类型: {player['source_type']}")
    if results['video_links']:
        logger.debug("\n   检测到的视频链接:")
        for link in results['video_links']:
            logger.debug(f"     * 链接: {link}")
            # logger.debug(f"       XPath: {link['xpath']}")
            # logger.debug(f"       来源类型: {link['source_type']}")
            
    
    logger.debug("\n2. 第一层元素:=====================================================")
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
        logger.debug(f"   - 文本: {elem['text_analysis']['text_content']} ")
        logger.debug(f"   - 链接数量: {elem['text_analysis']['link_count']} 个")
        logger.debug(f"   - 文本/链接比例: {elem['text_analysis']['text_to_link_ratio']:.2f}")
        # element = html.xpath(elem['xpath'])

        
        # logger.debug(len(element))
        # logger.debug(ret[0].xpath(elem['xpath'])[0])
        
        if elem['video_player']['is_player']:
            logger.debug(f"   - 视频播放器: {elem['video_player']['player_type']}")
            if elem['video_player']['details']:
                logger.debug("     详情:")
                for k, v in elem['video_player']['details'].items():
                    logger.debug(f"     * {k}: {v}")
        
        # if elem['text_analysis']['links']:
        #     logger.debug("   - 链接列表:")
        #     for link in elem['text_analysis']['links']:
        #         logger.debug(f"     * {link['text']} ({link['href']})")
    
    logger.debug("\n3. 第二层元素:#########################################################")
    for i, elem in enumerate(results['second_level'], 1):
        for l1_path in tag_level1['tags_xpath']:
            if l1_path in elem['xpath']:
                if len(elem['text_analysis']['links']) > 0:
                    for link in elem['text_analysis']['links']:
                        logger.debug(f"     * {link['text']} ({link['href']})")
                    
        for l1_path in tag_level1['contents_xpath']:
            if l1_path in elem['xpath']:
                
                if elem['text_analysis']['text_length'] > 20 and elem['text_analysis']['text_to_link_ratio'] > 10:
                    logger.debug(f"\n ☆☆ 内容元素 ☆☆")
                    logger.debug(f"   - XPath: {elem['xpath']}")
                    logger.debug(f"   - 文本: {elem['text_analysis']['text_content']} ")
                    # logger.debug(f" {elem['text_analysis']['text_length']}")
                # for link in elem['text_analysis']['links']:
                #     logger.debug(f"     * {link['text']} ({link['href']})")
        
        
        # logger.debug(f"\n   元素 {i}:")
        # logger.debug(f"   - 标签: {elem['tag']}")
        # logger.debug(f"   - 角色: {elem['role']}")
        # logger.debug(f"   - 文本/链接比例: {elem['text_analysis']['text_to_link_ratio']:.2f}")
        
        # logger.debug(ret[0].xpath(elem['xpath']+'/*/text()'))
        
        # if elem['video_player']['is_player']:
        #     logger.debug(f"   - 视频播放器: {elem['video_player']['player_type']}")
        #     if elem['video_player']['details']:
        #         logger.debug("     详情:")
        #         for k, v in elem['video_player']['details'].items():
        #             logger.debug(f"     * {k}: {v}")
        
        # if elem['text_analysis']['links']:
        #     logger.debug("   - 链接列表:")
        #     for link in elem['text_analysis']['links']:
        #         logger.debug(f"     * {link['text']} ({link['href']})")
                
    logger.debug("\n=== L结构分析报告 (结论)===\n")
    # for i, elem in enumerate(results['first_level'], 1):
        # if elem['role'] == 'header':
    
    
                
# 使用示例
if __name__ == "__main__":
    sample_html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="renderer" content="webkit">
<title>最高检：1-9月检察机关共起诉组织、领导传销活动罪4627人_河北新闻网</title>
<link rel="shortcut icon" type="image/ico" href="https://www.hebnews.cn/index.ico" />
<meta name="viewport" content="width=device-width, initial-scale=1">

<meta name="author" content="ypp,zj">
<meta name="contentid" content="9254045">
<meta name="publishdate" content="2024-10-28 10:25:36">
<meta name="author" content="张宇晴">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<meta name="description" content="2024年1月至9月，全国检察机关起诉组织、领导传销活动罪4627人。检察办案发现，近年来，随着依法惩治传销犯罪力度不断加大，一些犯罪分子为躲避监管打击，将传销由线下转移至线上。有的直接将传统传销活动“搬到”网上。截至2023年7月，该平台共吸引会员9万余人，形成多达245层的传销网络。">
<meta name="keyword" content="检察机关,法制,社会万象,违法犯罪,诈骗">
<meta property="og:type" content="acticle">
<meta property="og:title" content="最高检：1-9月检察机关共起诉组织、领导传销活动罪4627人">
<meta property="og:site_name " content="河北新闻网">
<meta property="og:url" content="https://world.hebnews.cn/2024-10/28/content_9254045.htm" />
<meta property="og:image" content="https://img.hebnews.cn/2024-10/28/959d9fcc-7664-42d9-bce8-742e881aca1b.jpg">
<meta property="og:description" content="2024年1月至9月，全国检察机关起诉组织、领导传销活动罪4627人。检察办案发现，近年来，随着依法惩治传销犯罪力度不断加大，一些犯罪分子为躲避监管打击，将传销由线下转移至线上。有的直接将传统传销活动“搬到”网上。截至2023年7月，该平台共吸引会员9万余人，形成多达245层的传销网络。">
<link rel="canonical" href="https://world.hebnews.cn/2024-10/28/content_9254045.htm" />
<link rel="next" title="各地陆续进入最美赏秋季" href="https://world.hebnews.cn/2024-10/28/content_9254034.htm" />
<!-- 页面匹配手机1:1 需要设置响应式 -->
<link href="https://img.hebnews.cn/templateRes/201612/15/88932/88932/images/default.css?20230907y" rel="stylesheet" type="text/css" />
<!--<script type="text/javascript" src='https://apps.hebnews.cn/h5share/common/closewxmenu.js'></script>加载完之前禁止分享-->
<script type="text/javascript" src='https://img.hebnews.cn/jquery-1.8.3.min.js'></script>
<script type="text/javascript" src="https://img.hebnews.cn/templateRes/201612/15/88932/88932/images/QRCode.js"></script>
<!--<script type="text/javascript" src="https://img.hebnews.cn/templateRes/201612/15/88932/88932/images/ResizeSensor.min.js"></script>
<script type="text/javascript" src="https://img.hebnews.cn/templateRes/201612/15/88932/88932/images/theia-sticky-sidebar.min.js"></script>-->

<script src="https://res.wx.qq.com/open/js/jweixin-1.6.0.js"></script>
<script src="https://qzonestyle.gtimg.cn/qzone/qzact/common/share/share.js"></script>
<script type="text/javascript" src='https://apps.hebnews.cn/h5share/js_jjb/h5Share1.4.0.js?1'></script>

<!-- 统计代码 -->
<script language="javascript">
var	_yfx_videoplayerid = "videoplayer";
var _yfx_nodeid = "138";
var _yfx_contentid = "9254045";
var _yfx_title = "最高检：1-9月检察机关共起诉组织、领导传销活动罪4627人";
var _yfx_editor = "张宇晴";
var _yfx_pubtime = "2024-10-28 10:25:36";
var _yfx_website = "10000001";
(function() {
    var yfxjs = document.createElement("script");
    yfxjs.charset = "utf-8";
    yfxjs.src = "//counter.hebnews.cn/count/yeefxcount.js";
    var yfxjs_t = document.getElementsByTagName("script")[0];
    yfxjs_t.parentNode.insertBefore(yfxjs, yfxjs_t);
})();
	
var _yfx_trackdata= _yfx_trackdata || [];

</script>
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?fc19c432c6dd37e78d6593b2756fb674";
  var s = document.getElementsByTagName("script")[0]; 
  s.parentNode.insertBefore(hm, s);
})();
</script>
</head>

<body>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style>
.hp2017_g_width{ width:1400px; margin: 0 auto; overflow:hidden}
.hp2017_navigation{ height: 52px; background:#f2f2f2;  font-size: 14px; line-height:52px;}
.hp2017_navigation li{ padding:0 10px; float: left ;overflow: visible; white-space: nowrap;}
.hp2017_navigation li img{ vertical-align:middle}
.hp2017_navigation a{ color:#333; text-decoration: none}
.hp2017_navigation a:hover{text-decoration: underline;}
li.hp2017_navigation_jia{border:0; float:right; width:50px; height: 50px; text-align: center;padding-bottom:40px; overflow: visible;}
li.hp2017_navigation_jia:hover .hp2017_navigation_more{ display: block; position: absolute; z-index: 999}
.hp2017_navigation_more{ display: none ; width: 800px;height:50px; margin-left: -740px; margin-top: 10px;*margin-top:30px;box-shadow: 0px 0 5px #d0d0d0;border:#dbdbdb solid 1px;background:#fff; position:relative}
.hp2017_navigation_more li{ padding:0 10px 0 13px; border-right: 0}
.hp2017_navigation_more a{color:#333; position: relative; z-index: 99999 }

</style>
<div class="hp2017_navigation">
	<div class="hp2017_g_width">
		<ul>
<li ><a target="_blank" href="https://www.hebnews.cn"><img src="https://img.hebnews.cn/templateRes/202105/19/307398/307398/logo.png" width="104" style=""/></a></li>
<li><a target="_blank" href="https://hebei.hebnews.cn">河北要闻</a></li>
<li><a target="_blank" href="https://tousu.hebnews.cn">阳光理政</a></li>
<li><a target="_blank" href="https://zhuanti.hebnews.cn/node_353620.htm">京津冀</a></li>
<li><a target="_blank" href="https://xiongan.hebnews.cn">雄安新区</a></li>
<li><a target="_blank" href="https://zhuanti.hebnews.cn/node_353473.htm">后冬奥</a></li>
<li><a target="_blank" href="https://dahezhibei.hebnews.cn/sy.htm">大河之北</a></li>
<li><a target="_blank" href="https://comment.hebnews.cn">慷慨歌</a></li>
<li><a target="_blank" href="https://theory.hebnews.cn">理论</a></li>
<li><a target="_blank" href="https://gov.hebnews.cn">政务</a></li>
<li><a target="_blank" href="https://sxbgt.hebnews.cn/">阳光执信</a></li>
<li><a target="_blank" href="https://hebei.hebnews.cn/node_357312.htm">直播</a></li>

<li><a target="_blank" href="https://xczx.hebnews.cn">乡村振兴</a></li>
<li><a target="_blank" href="https://shengtaihuanbao.hebnews.cn/">生态环保</a></li>
<li><a target="_blank" href="https://yxhb.hebnews.cn">影像河北</a></li>
<li><a target="_blank" href="https://gongyi.hebnews.cn">公益</a></li>
<li><a target="_blank" href="https://travel.hebnews.cn">文旅</a></li>
<li><a target="_blank" href="https://yuqing.hebnews.cn">舆情</a></li>
<li><a target="_blank" href="https://finance.hebnews.cn">财经</a></li>
<li><a target="_blank" href="https://guoqi.hebnews.cn">国企</a></li>

			<li class="hp2017_navigation_jia"><img src="https://img.hebnews.cn/templateRes/202105/19/307398/307398/jia.png" alt="">
				<ul class="hp2017_navigation_more">
<li><a target="_blank" href="https://house.hebnews.cn">房产</a></li>
<li><a target="_blank" href="https://tc.hebnews.cn">体彩</a></li>
<li><a target="_blank" href="https://sports.hebnews.cn">体育</a></li>
<li><a target="_blank" href="https://jingji.hebnews.cn">产经</a></li>
<li><a target="_blank" href="https://edu.hebnews.cn">教育</a></li>
<li><a target="_blank" href="https://health.hebnews.cn">健康</a></li>
<li><a target="_blank" href="https://power.hebnews.cn">电力</a></li>
<li><a target="_blank" href="https://jt.hebnews.cn">交通</a></li>
<li><a target="_blank" href="https://zhuanti.hebnews.cn">专题</a></li>
<li><a target="_blank" href="https://zhongyiyao.hebnews.cn">中医中药</a></li>
<li><a target="_blank" href="https://shangmao.hebnews.cn/">商贸</a></li>
<li><a target="_blank" href="https://shuhua.hebnews.cn/">书画</a></li>
<li><a target="_blank" href="https://auto.hebnews.cn/">汽车</a></li>
<li><a target="_blank" href="https://digi.hebnews.cn/">数码</a></li>
<li><a target="_blank" href="https://design.hebnews.cn">视觉</a></li>
					<span class="hp2017_navigation_more_bg"></span>
				</ul>
			</li>
		</ul>

	</div>
</div>
<!-- 专题分享代码，不要更换id名称 -->
<div id="content" style="display:none">
<!-- 专题缩略图 -->
<!--<img src="https://img.hebnews.cn/templateRes/201612/15/88932/88932/20230327_4.png" alt="">-->

<img src="https://img.hebnews.cn/2024-10/28/959d9fcc-7664-42d9-bce8-742e881aca1b.jpg">

<!-- 专题标题 -->
<p id="shareTitle">最高检：1-9月检察机关共起诉组织、领导传销活动罪4627人</p>
<!-- 专题摘要 -->
<!--<p id="shareDesc">最高检：1-9月检察机关共起诉组织、领导传销活动罪4627人</p>-->
<p id="shareDesc">来自河北新闻网</p>
</div>
<div class="bc_nav">
    	<div class="bc_main"><div class="n_logo"><a href="http://www.hebnews.cn" target="_blank"><img src="https://img.hebnews.cn/templateRes/201702/14/92410/92410/images/logo.png" alt="河北新闻网" title="河北新闻网"></a></div>
        <a href="https://world.hebnews.cn/index.htm" target="_blank" class="" >国内国际</a><a href="https://world.hebnews.cn/node_138.htm" target="_blank" class="" >国内</a></div>
    	<div class="bc_search">
<!--
            <form onsubmit="per_submit();" method="post" name="form1" target="_blank" action="https://search.hebnews.cn/servlet/SearchServlet.do">
            <input name="op" value="single" type="hidden">
            <input name="sort" value="date" type="hidden">
            <input name="siteID" type="hidden">
            <input class="bc_search_text" name="contentKey" id="contentKey" value="请输入关键字" onfocus="if(this.value=='请输入关键字')this.value='';" onblur="if(this.value=='')this.value='请输入关键字';">
            <input class="bc_search_buttom" name="submit" value="搜索" type="submit">
            </form>
-->
			
		
			<input class="bc_search_text" name="contentKey" id="contentKey" value="请输入关键字" onfocus="if(this.value=='请输入关键字')this.value='';" onblur="if(this.value=='')this.value='请输入关键字';">
            <input class="bc_search_buttom" name="submit" value="搜索" type="submit" onclick="_yfx_trackdata.push(['event', '文章页搜索', '搜索按钮']);">
			
		<script>

		(function(){
    $(".bc_search_buttom").on("click",function(){
        var keyWord = $(".bc_search_text").val();
        var url = 'https://hebnewssearch.wes2.com/?pageNow=1&pageSize=10&keyWord='+ keyWord 
        window.open(url);

    })
})()
		</script>
			
        </div>
    </div>
<div class="y_width">
	
    <div class="content">
        <h1>最高检：1-9月检察机关共起诉组织、领导传销活动罪4627人</h1>
        <div class="min_cont"><div class="post_source">
		2024-10-28 10:25:36　来源：人民日报客户端
    </div>
        <div class="post_wz">
        <input id="Btn2" type="button" value="A-" name=""/>
        <input id="Btn1" type="button" value="A+" name=""/>
    <script>
        window.onload= function(){
            var oPtxt=document.getElementById("p1");
            var oBtn1=document.getElementById("Btn1");
            var oBtn2=document.getElementById("Btn2");
            var num = 20; /*定义一个初始变量*/
            oBtn1.onclick = function(){
                num++;
                oPtxt.style.fontSize=num+'px';
            };
            oBtn2.onclick = function(){
                num--;
                oPtxt.style.fontSize=num+'px';
            }
        }
    </script>
        </div>
        </div>
    </div>
</div>

<div class="y_width sidefixedline">
    <div class="min_left">
    	<div class="min_left_share">
            <div class="share_box">
                <div id="ops_share"></div>
                <script src="https://img.hebnews.cn/templateRes/201612/15/88932/88932/images/share.min.js" charset="utf-8"></script>
            </div>
            <div class="min_qrcode"><div id="qrcode"></div><p>扫码阅读手机版</p></div>
<script type="text/javascript">
new QRCode(document.getElementById("qrcode"), "https://world.hebnews.cn/2024-10/28/content_9254045.htm");  // 设置要生成二维码的链接
</script>
        </div>
        <div class="min_con_text" id="p1">

<!--enpcontent--><p style="text-align: left;">2024年1月至9月，全国检察机关起诉组织、领导传销活动罪4627人。检察办案发现，近年来，随着依法惩治传销犯罪力度不断加大，<strong>一些犯罪分子为躲避监管打击，将传销由线下转移至线上。相较于传统传销，网络传销不受时空限制，传播更灵活、活动更隐蔽、资金转移更方便，更易给群众造成重大财产损失，需综合施策、深化治理。</strong></p><p style="text-align: left;"><strong>一、编造各种“骗局”引诱群众参加。</strong>不法分子利用互联网的虚拟性和便捷性，编造花样众多、真假难辨的“致富骗局”，引诱群众参与其中。有的直接将传统传销活动“搬到”网上。如刘某某等人组织、领导传销活动案。刘某某等人注册成立生物科技公司，开设专门网站，组织团队线上线下推广“兴中天互助平台”，以“投资返利”“拉人返利”的形式发展会员，5个月内吸收会员59级、42万余人，涉及全国31个省份和港澳台地区等。有的蹭虚拟货币、区块链、金融创新、慈善互助等新的概念和社会热点开展网络传销。如盛某某等人组织、领导传销活动案。盛某某等人虚构谷歌公司“谷歌币”区块链项目，通过网络媒体公开宣传炒作，对外发布认筹购买“谷歌币”，以ETH（以太币）作为结算币种，共发展会员6万余人，非法获利2000余万元。一些地方还出现了诸如“抢购转售”“网络拍卖”“传播国学”等网络传销新名目，需高度警惕。</p><p style="text-align: left;"><strong>二、打着官方旗号骗取群众信任。</strong>为打消群众疑虑，更好推销所谓“项目”，吸引更多人参加，有的不法分子甚至直接打着“国家项目”“政府支持”等旗号，谎称项目有“国家”“政府”“央企”等背景，并以此开展网络传销活动。如汪某等人组织、领导传销活动案。汪某假冒国家乡村振兴局副主任身份，伙同他人以其实际控制的“掌心集团”的名义，宣称与地方政府合作，通过在多地召开项目发布会、邀请影视明星站台等方式，推广“销销乐”网络平台。截至2023年7月，该平台共吸引会员9万余人，形成多达245层的传销网络。</p><p style="text-align: left;"><strong>三、扩充传销层级规避责任追究。</strong>为尽可能多地骗取群众钱款并规避法律责任，不法分子利用网络便利扩充传销层级，试图以此让自己隐身幕后，并让资金来源和流向难以追踪。如章某某等人组织、领导传销活动案。章某某等人开发“拼拼有礼”APP，以“拼团购物”为噱头，宣称拼团失败的会员可获得返现，吸引群众加入会员并在该APP平台充值下单拼团，并制定不同等级的晋升条件和奖励制度，4个月内即吸引379万余人注册会员，形成多达178个层级的传销网络。</p><p style="text-align: left;">面对花样翻新的“致富秘籍”“投资捷径”等网络宣传，检察机关提醒广大群众要提高警惕，不信“大饼”、不贪“小利”，自觉抵制看似唾手可得的“高额回报”诱惑，避免误入网络传销“陷阱”。</p><p style="text-align: left;"><br/></p><p><span id="cnki_grabber" data-id="1730082259000" style="visibility: hidden;"></span></p><!--/enpcontent--><!--enpproperty <articleid>9254045</articleid><date>2024-10-28 10:25:36:0</date><author>张宇晴</author><title>最高检：1-9月检察机关共起诉组织、领导传销活动罪4627人</title><keyword>检察机关,法制,社会万象,违法犯罪,诈骗</keyword><subtitle></subtitle><introtitle></introtitle><siteid>2</siteid><nodeid>138</nodeid><nodename>国内</nodename><nodesearchname>国内</nodesearchname><picurl>https://img.hebnews.cn/2024-10/28/959d9fcc-7664-42d9-bce8-742e881aca1b.jpg</picurl><url>https://world.hebnews.cn/2024-10/28/content_9254045.htm</url><urlpad>https://m.hebnews.cn/world/2024-10/28/content_9254045.htm</urlpad><sourcename>人民日报客户端</sourcename><abstract>2024年1月至9月，全国检察机关起诉组织、领导传销活动罪4627人。检察办案发现，近年来，随着依法惩治传销犯罪力度不断加大，一些犯罪分子为躲避监管打击，将传销由线下转移至线上。有的直接将传统传销活动“搬到”网上。截至2023年7月，该平台共吸引会员9万余人，形成多达245层的传销网络。</abstract><channel>1</channel>/enpproperty-->
        </div>
        <div class="editor">责任编辑：张宇晴</div>
        <div class="next-page"> 下一篇：<a href="https://world.hebnews.cn/2024-10/28/content_9254034.htm" target="_blank">各地陆续进入最美赏秋季</a> </div>
<!--
        <div class="relnews">
		<h3>相关新闻：</h3>
		<ul>
			
		</ul>
		</div>
-->
    
    </div>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style>

@media screen and (max-width: 640px) {
.min_right{ width:100%; float: none;}
	
}

.min_right{ width:335px; float:right; padding-top:20px}

.ce{background: #fafafa;padding: 16px 13px 10px 12px; margin-bottom:15px}
.side_title{height: 22px;line-height: 22px;font-size: 18px; border-left:5px #e61d27 solid;padding: 0 15px;position: relative; margin-bottom:16px}
.side_title a{ color:#010101}
.side_img img{ width:100%; height:auto}
ul.f32d16 li{ line-height:32px; border-bottom:1px #ddd dotted}
ul.f32d16 li:nth-child(2){ border:none}
ul.f32d16 a{ display:block; line-height: 42px;height: 42px;overflow: hidden;font-size: 16px;white-space: nowrap;text-overflow: ellipsis; color:#000; font-weight:bold}
ul.f32d16 span{ color:#8d8f8c}

.min_pix{ width:45%; height:auto; float:left; margin:0 3% 15px 2%}
.min_pix img{ width:100%; height:80px; max-height:100px}
.min_pix span{ line-height:24px; font-size:14px; color:#646464;text-overflow: -o-ellipsis-lastline;overflow: hidden;text-overflow: ellipsis;display: -webkit-box;-webkit-line-clamp: 2;line-clamp: 2;
-webkit-box-orient: vertical; height:48px }
.min_pix span a{ color:#646464}

ul.f62d16{ background:url(https://img.hebnews.cn/templateRes/201612/15/88931/88931/xi.png) repeat-y 4px 15px}
ul.f62d16 li{display: flex;align-items: center; height:62px; line-height:24px; font-size:16px; padding-left:20px; background:url(https://img.hebnews.cn/templateRes/201612/15/88931/88931/to.png) no-repeat left center}
ul.f62d16 li a{ color:#000}

.side_dubao {text-align: center;padding-bottom: 12px;}
.side_dubao img{width: 260px;height: 400px;}

.min_sider_pic{ position:relative; width:310px; height:175px;}
.min_sider_pic img{ width:310px; height:175px;}
.min_sider_hover{ width:100%; height:40px; position:absolute; left:0; bottom:0; opacity:0.5; filter:alpha(opacity=50); background:#000;}
.min_sider_text{width:calc(100% - 20px); height:40px; position:absolute; left:0; bottom:0; line-height:40px; text-align:center; font-size:16px; padding:0 10px;white-space: nowrap;text-overflow: ellipsis;overflow: hidden;word-break: break-all; color:#fff}
.min_sider_text a{ color:#fff}

ul.f50d14 li{ line-height:50px; font-size:14px;white-space: nowrap;text-overflow: ellipsis;overflow: hidden;word-break: break-all; color:#020202; border-bottom:1px #e1e1e1 solid}
ul.f50d14 li:last-child{ border:none}
ul.f50d14 li a{color:#020202}
ul.f50d14 cite{ float:none;}


</style>









<div class="min_right">
	<div class="min_pic yuqing" style="margin-bottom:10px"><img src="https://img.hebnews.cn/templateRes/202105/24/307406/307406/240120zonglan.jpg" /></div>
    <!--<div class="min_pic yuqing" style="margin-bottom:10px"><img src="https://img.hebnews.cn/templateRes/202105/24/307406/307406/yzdsb3.jpg" /></div>-->
	<div class="min_pic yuqing" style="margin-bottom:10px"><a href="https://shop134167982.youzan.com/v2/showcase/homepage?alias=80eaIFt1zd" rel="nofollow" target="_blank"><img src="https://img.hebnews.cn/templateRes/202105/24/307406/307406/zlyp.jpg" /></a></div>
    	<div class="min_pic ce" style="display:none">
        	<div class="side_title"><span><a href="https://hebei.hebnews.cn/node_357312.htm" target="_blank">纵览直播</a></span></div>
            <div class="side_img"><a href="https://live.hebnews.cn/livestream/websocket/getlivestream?liveid=24780"  target="_blank"><img src="https://img.hebnews.cn/2024-04/09/5631fdae-e687-48e0-a7c2-f777870df3a4.png"></a></div>
            <ul class="f32d16">
            	
                <li><a href="http://live.hebnews.cn/livestream/websocket/getlivestream?liveid=24779"  target="_blank">回放｜"河北省扎实推进医疗卫生事业高质量发展"新闻发布会</a><span>2024-04-08 10:02:38</span></li><li><a href="https://live.hebnews.cn/livestream/websocket/getlivestream?liveid=24777"  target="_blank">直播结束丨杏花映长城·杏韵金山岭——金山岭长城第十二届杏花节</a><span>2024-04-05 09:15:40</span></li>
            </ul>
        </div>
        <div class="min_pic ce">
        	<div class="side_title"><span><a href="https://hebei.hebnews.cn/node_116.htm" target="_blank">热点推荐</a></span></div>
            
<div class="min_sider_pic"><a href="https://hebei.hebnews.cn/2024-10/28/content_9254102.htm"><img src="https://img.hebnews.cn/2024-10/28/85e36b8c-7f4f-41c7-8a58-69f80912d27b.jpg" /></a><div class="min_sider_hover"></div><div class="min_sider_text"><a href="https://hebei.hebnews.cn/2024-10/28/content_9254102.htm">百姓看日报｜竞技？也是经济！</a></div></div><!--焦点图第一张图片稿-->

            <ul class="f50d14">
            	
<li><a href="https://hebei.hebnews.cn/2024-10/28/content_9253932.htm"><cite style="color:#dd0000">数博会现场直击</cite>｜享受数字里的美好“食”光</a></li><li><a href="https://hebei.hebnews.cn/2024-10/28/content_9253933.htm"><cite style="color:#dd0000">我的手机存照</cite>｜我用创业修补人生“缺憾”</a></li><li><a href="https://hebei.hebnews.cn/2024-10/28/content_9253927.htm"><cite style="color:#dd0000">记者走基层</cite>｜供热管理有了“智慧大脑”</a></li><li><a href="https://hebei.hebnews.cn/2024-10/28/content_9253926.htm"><cite style="color:#dd0000">记者走基层</cite>｜政务服务大厅“搬到”居民家门口</a></li><li><a href="https://hebei.hebnews.cn/2024-10/28/content_9253928.htm"><cite style="color:#dd0000">一线追“新”记</cite>｜食用菌“微型农场”迎新变</a></li><li><a href="https://hebei.hebnews.cn/2024-10/28/content_9253929.htm"><cite style="color:#dd0000">文化快评</cite>｜低级别文物也需要用心呵护</a></li><!--独家-->

            	
            </ul>
        </div>
            <div class="min_pic ce sidefixed">
                <div class="side_title"><span><a >电子报</a></span><select name="selectsz3 " style=" position: absolute;top: 0; right:10px; border-radius:10px; height:24px; padding-left:10px" onchange="if(this.selectedIndex!=0) window.open(this.options[this.selectedIndex].value,'_blank')">
    <option selected="selected">河北日报报系</option>
    <option value="http://hbrb.hebnews.cn/?">河北日报</option>
    <option value="http://yzdsb.hebnews.cn/">燕赵都市报</option>
    <option value="http://szbz.hbfzb.com/">河北法制报</option>
    <option value="http://hbnw.hebnews.cn/index.htm">河北农民报</option>
    <option value="http://jk.hebnews.cn">医院管理论坛报</option>
    <option value="http://zhuanti.hebnews.cn/node_138104.htm">河北旅游杂志</option>
    <option value="http://caixiebian.hebnews.cn/">采写编</option>
    <option value="http://zw.hebnews.cn/index.htm">杂文月刊</option>
    </select></div>
                <div class="side_dubao"><a href="https://hbrb.hebnews.cn?" target="_blank"><img src="https://img.hebnews.cn/2021-04/30/e5ec7212-e824-4bae-be4a-fd41217ea27b.png"    border="0"> </a></div>
            </div>
            
            
            
            <div class="min_pic yuqing" style="margin-bottom:10px"><a href="https://yuqing.hebnews.cn/node_356524.htm" target="_blank"><img src="https://img.hebnews.cn/templateRes/202105/24/307406/307406/20210528.jpg" /></a></div>
            
			
        </div>


    <div class="cl"></div>
</div>
<div class="y_width" style=" margin-top:50px">
    <div class="qrcode">
        <p>凡注有“河北新闻网”电头或标明“来源：河北新闻网”的所有作品，版权均为本网站与河北日报报业集团所有（本网为河北日报报业集团独家授权版权管理机构）。未经许可不得转载、摘编、复制、链接、镜像或以其它方式使用上述作品，违者将依法追究法律责任。</p>
    </div>
</div>
<div class="desktop-side-tool CCC-float-bar-right">
	<!--<div class="min_ewm"><img src="https://img.hebnews.cn/templateRes/201612/15/88932/88932/images/ewm.jpg"><p>关注河北新闻网</p></div>-->
    <a class="min_top" onClick="window.scrollTo(0,1); window.location.hash=''; return false;" id="CCCFBRScrollToTop" href="javascript:void(0);"></a>
</div>

<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

<style>

.am-weixin {
    text-align: center;
    clear: both;
    width: 100%;
    overflow: hidden;
    padding-top: 25px;
    font-size: 1.2em;
	margin-bottom:2em; display:none
}
.am-weixin a{ color:#000}

.am-avg-sm-4>li {
    width: 25%; float:left; text-align:center
}
.am-thumbnail {
    display: inline-block;
    padding: 2px;
    border: 1px solid #ddd;
    border-radius: 0;
    background-color: #fff;
    -webkit-transition: all .2s ease-in-out;
    transition: all .2s ease-in-out;
}
.nb{ display:none}
@media screen and (max-width: 640px) {
	.am-weixin { display:block}

}
</style>
<ul class="am-avg-sm-4 am-thumbnails am-weixin">
<li><img class="am-thumbnail am-thumbnail-weixin" src="https://img.hebnews.cn/92410.files/assets/images/weixin_hbrb.jpg"><p>河北日报<br>微信公众号</p></li>
<li><img class="am-thumbnail am-thumbnail-weixin" src="https://img.hebnews.cn/templateRes/201612/13/88730/88730/hebnews.jpg"><p>河北新闻网<br>微信公众号</p></li>
<li><img class="am-thumbnail am-thumbnail-weixin" src="https://img.hebnews.cn/templateRes/201612/13/88730/88730/zonglan.jpg"><p>纵览新闻<br>微信公众号</p></li>
<li><a href="https://zhuanti.hebnews.cn/hbrbapk.htm?m-page"><img class="am-thumbnail am-thumbnail-weixin" src="https://img.hebnews.cn/templateRes/202104/28/307358/307358/images/2022qr2.jpg"><p>河北日报<br>客户端</p></a></li>
</ul>


<style>
.h2017_g_width{ width:1200px; margin: 0 auto}
.h2017_footer{ height: 215px; border-top: 1px #e1e1e1 solid; clear:both; padding-top:20px; overflow:hidden; margin:0 auto; width:1200px}
.h2017_footer_in{ text-align: center;color:#6c6c6c; font-size: 14px; }
.h2017_footer_in a{color:#6c6c6c; text-decoration:none}
.h2017_footer_in p{  padding-bottom: 10px}
.h2017_footer_in span{ padding:0 6px; }
.padding-fix span{ padding:0 10px; }


.h2017_about{ height: 40px;  font-size: 16px; text-align:center; overflow:hidden}
.h2017_about ul{ display: block;margin:0 auto; width:800px; text-align: center; padding:0}
.h2017_about li{ padding:0 ; margin-top: 8px; display:inline}
.h2017_about li a{color:#6c6c6c;}

#_ideConac{ padding:0!important; vertical-align:middle; position:relative; margin-top:-35px; display:inline-block}
#imgConac{ width:60px; }
.h2017_footer p{ text-indent:0}
.fix3 { padding-bottom:0}
.fix3 span{ padding:0 5px}
</style>


<div class='h2017_footer'>
<div class='h2017_about'>
	<div class='h2017_g_width'>
		<ul>
			<!--<li><a href='https://group.hebnews.cn/index.html' rel='nofollow' target="_blank">河北日报报业集团</a> - </li>-->
			<li><a href='https://help.hebnews.cn/index.html' rel='nofollow'  target="_blank">河北新闻网</a> - </li>
			<li><a href='https://help.hebnews.cn/bqsm.html' rel='nofollow'  target="_blank">版权声明</a> - </li>
			<li><a href='https://help.hebnews.cn/fwtk.html' rel='nofollow'  target="_blank">服务条款</a> - </li>
			<li><a href='https://help.hebnews.cn/ggyw.html' rel='nofollow'  target="_blank">广告业务</a> - </li>
			<li><a href='https://help.hebnews.cn/sxsq.html' rel='nofollow'  target="_blank">实习申请</a> - </li>
			<li><a href='https://help.hebnews.cn/wstg.html'  rel='nofollow'  target="_blank">网上投稿</a> - </li>
			<li ><a href='https://help.hebnews.cn/xwrx.html'  rel='nofollow'  target="_blank">新闻热线</a> - </li>
			<li  style='border:0; ' ><a href='https://www.hebnews.cn/sitemap.htm'>网站地图</a></li>
		</ul>

	</div>
</div>
	<div class='h2017_g_width'>
		<div class='h2017_footer_in'>
			<p class='padding-fix' style="display:none">
				<span>新闻热线:0311-67563366</span>
				<span>广告热线:0311-67563019</span>
				<span>新闻投诉:0311-67562994</span>
				<span>违法和不良信息举报电话：0311-67563366 邮箱：hbrbwgk@126.com</span>   
			</p>
			<p  style="display:none">
				<span>河北日报广告热线（刊登声明）:0311-67562168</span>
				<span>燕赵都市报广告热线:0311-86056666</span>
			</p>
			<p>
				<span><a href='http://beian.miit.gov.cn' target='_blank' rel="nofollow">冀ICP备 09047539号-1</a></span> 
				<span>互联网新闻信息服务许可证编号:13120170002</span> 
				<span>冀公网安备 13010802000309号</span>
			</p>
			<p>
				<span>广播电视节目制作经营许可证（冀）字第101号</span> |
				<span>信息网络传播视听节目许可证0311618号</span> |
              <span><!--<a href='http://sq.ccm.gov.cn/ccnt/sczr/service/business/emark/toDetail/9748adc7a536495b888b73a1eac20cc2' target='_blank' rel='nofollow'>-->冀网文【2021】1825-001号<!--</a>--></span>

			</p>
			
			<p>河北新闻网版权所有 本站点信息未经允许不得复制或镜像</p>
			<p>www.hebnews.cn copyright © 2000 - 2024</p>
            <p class="fix3">
				<span><a href='http://www.hbjbzx.gov.cn/' target='_blank' rel='nofollow'><img style="border:1px #ccc solid" src="https://img.hebnews.cn/templateRes/201612/13/88730/88730/20200720.jpg" alt="河北互联网违法和不良信息举报"></a></span>
				<span><a href='http://beian.miit.gov.cn' target='_blank' rel='nofollow'><img src='https://img.hebnews.cn/attachement/gif/site2/20120823/001aa0c3d91f119fcd371f.gif' alt='经营性备案信息'></a></span>


<span><script src='https://dcs.conac.cn/js/05/000/0000/60850566/CA050000000608505660002.js'></script></span>


                                
                                <span><!--<a href='http://sq.ccm.gov.cn:80/ccnt/sczr/service/business/emark/toDetail/9748adc7a536495b888b73a1eac20cc2' rel='nofollow' target='_blank'>--><img src=' https://img.hebnews.cn/88730.files/wenhua.jpg' alt='网络文化经营单位'><!--</a>--></span>

<span><a href='http://www.12377.cn' target='_blank' rel='nofollow'><img src=' https://img.hebnews.cn/86150.files/images/12377_2.jpg' alt='中国互联网举报中心'></a></span>
  				<span><a href='http://press.gapp.gov.cn/' target='_blank' rel='nofollow'><img src='https://img.hebnews.cn/attachement/gif/site2/20120823/001aa0c3d91f119fcd3721.gif' alt='新闻记者证管核系统'></a></span>
              
                
               
			</p>
		</div>
	</div>
</div>

<!--纵览分享-->
<script>



function isInApp(){

return navigator.userAgent.indexOf("zonglan6756") > -1
}


function isAndroid() {
var u = navigator.userAgent;
var isAndroid = u.indexOf('Android') > -1 || u.indexOf('Adr') > -1; //android终端
var isiOS = !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/); //ios终端
if (isAndroid) {
 return true;
} else if (isiOS) {
 return false;
}
}

// 交互
function connectWebViewJavascriptBridge(callback) {
// android
if (window.WebViewJavascriptBridge) {
 return callback(WebViewJavascriptBridge);
} else {
 document.addEventListener('WebViewJavascriptBridgeReady', function () {
     callback(WebViewJavascriptBridge);
 }, false);
}
// ios
if (window.WVJBCallbacks) {
 return window.WVJBCallbacks.push(callback);
}
window.WVJBCallbacks = [callback];
var WVJBIframe = document.createElement('iframe');
WVJBIframe.style.display = 'none';
WVJBIframe.src = 'wvjbscheme://__BRIDGE_LOADED__';
document.documentElement.appendChild(WVJBIframe);
setTimeout(function () {
 document.documentElement.removeChild(WVJBIframe);
}, 10);
}






connectWebViewJavascriptBridge(function (bridge) {
    console.log('isAndroid');
    // Initialize for Android
    if (isAndroid()) {
        bridge.init(function (message, responseCallback) {});
    }

    if (isInApp()) {
        // Fetch content from the HTML elements
        var shareTitle = document.getElementById('shareTitle').innerText;
        var shareContent = document.getElementById('shareDesc').innerText;
        var shareImg = document.querySelector('#content img').src; // Assuming there's only one image inside the #content div

        let tempJson = {
            "enableShare": "0",
            "shareTitle": shareTitle,
            "shareContent": shareContent,
            "shareImg": shareImg,
            "shareUrl": '' // You can set this if there's a specific URL to share
        };

        // Trigger the appropriate bridge call
        if (isAndroid()) {
            // Android
            bridge.callHandler('setShareMsg', JSON.stringify(tempJson), function (str) {});
        } else {
            // iOS
            bridge.callHandler('setShareMsg', tempJson, function (str) {});
        }
    }
});


</script>
<!--纵览分享-->


	
	
	
	
<!--视频浮动-->
	  <script type="text/javascript">
    // 获取所有audios
    var audios = document.getElementsByTagName("video");
    // 暂停函数
    function pauseAll() {
        var self = this;
        [].forEach.call(audios, function(i) {
            // 将audios中其他的audio全部暂停
            i !== self && i.pause();
        })
    }
    // 给play事件绑定暂停函数
    [].forEach.call(audios, function(i) {
        i.addEventListener("play", pauseAll.bind(i));
    })


var videoElement = document.getElementById("videofloat");
videoElement.addEventListener('loadedmetadata', function(e){
$("#videobox").css("height",videoElement.offsetHeight);
$("#videobox").css("width",videoElement.offsetWidth);

});
		
		  
		  
	</script>	
	<script type="text/javascript" src="https://img.hebnews.cn/templateRes/201612/15/88932/88932/videofloat.js"></script>

<!--视频浮动-->
	
	
<!--新闻网自己的统计 -->


<script type="text/javascript" src="https://img.hebnews.cn/amucsite/stat/WebClick.js"></script>
<input  type="hidden" id="DocIDforCount" name="DocIDforCount" value="9254045">

<!--
<script type="text/javascript">
  jQuery(document).ready(function() {
    jQuery('.sidefixed').theiaStickySidebar({
      additionalMarginTop: 10,
	  containerSelector:'.sidefixedline',
      additionalMarginBottom:450,
	  
    });
  });
</script>
-->
</body>
</html>


    """
    
    print_analysis(sample_html)