import re
from bs4 import BeautifulSoup, Tag
from typing import Dict, List, Tuple
from collections import defaultdict
from loguru import logger
from lxml import etree
from collections import deque

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
            'footer': '页脚',
            'logo': '头部',
            'top': '头部'
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
        """获取body下元素的XPath路径"""
        if not element or not element.parent:
            return ""
            
        # 跳过 html 标签和其他不合理的标签
        if element.name in ['html', 'head', 'body']:
            return ""
            
        components = []
        current = element
        
        # 从当前元素向上遍历，直到body
        while current and current.parent:
            if current.parent.name == 'body':
                # 获取在body下的位置
                previous_siblings = current.find_previous_siblings(current.name)
                position = len(list(previous_siblings))
                if position > 0:
                    components.append(f"{current.name}[{position + 1}]")
                else:
                    components.append(current.name)
                break
            elif current.parent.name not in ['html', 'head']:
                # 获取在父元素下的位置
                previous_siblings = current.find_previous_siblings(current.name)
                position = len(list(previous_siblings))
                if position > 0:
                    components.append(f"{current.name}[{position + 1}]")
                else:
                    components.append(current.name)
            
            current = current.parent
        
        # 如果没有找到有效的路径，返回空字符串
        if not components:
            return ""
        
        # 反转组件列表并组合成XPath
        components.reverse()
        return "//body/" + "/".join(components)

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
        
        # text_links = [item['text'] for item in links]
        # text_links = ' '.join(text_links)
        # lnks_text_len = 
        lnks_words_count = sum(len(d['text']) for d in links) 
        word_counts_without_lnks = len(pure_text) - lnks_words_count  
        
        return {
            'text_content': pure_text,
            'text_length': len(pure_text),
            'link_count': len(links),
            'links': links,
            'text_to_link_ratio': len(pure_text) / (lnks_words_count if lnks_words_count >0 else 1),
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
        # html_content = self.clean_html(html_content).replace('\n','').replace('\t','')
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
    # ret = selector.xpath('/html/body')     # 返回为一列表
    tag_level1 = {'tags_xpath':deque(), 'contents_xpath':deque()}
    for i, elem in enumerate(results['first_level'], 1):
        if elem['role'] in ['主要内容', '文章', '区块', '普通元素'] and elem['text_analysis']['text_length'] > 0:
            if elem['text_analysis']['link_count'] > 0 and elem['text_analysis']['text_to_link_ratio'] >0.5 and elem['text_analysis']['word_counts_without_lnks'] < 10:
                # 可能是列表元素
                # tag_level1['tags_xpath'].add(elem['xpath'])
                if len(elem['xpath'])>1:
                    tag_level1['tags_xpath'].append(elem['xpath'])
            else:
                # 可能是正文元素
                if len(elem['xpath'])>1:
                    tag_level1['contents_xpath'].append(elem['xpath'])
                
        logger.debug(f"\n   元素 {i}:")
        logger.debug(f"   - XPath: {elem['xpath']}")
        logger.debug(f"   - 标签: {elem['tag']}")
        logger.debug(f"   - 角色: {elem['role']}")
        logger.debug(f"   - 文本: {elem['text_analysis']['text_content']} ")
        logger.debug(f"   - 纯文本字数: {elem['text_analysis']['word_counts_without_lnks']} ")
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
    
    # tag_level1['contents_xpath'].discard('')
    # tag_level1['tags_xpath'].discard()
    # tag_level1['contents_xpath'] = list(tag_level1['contents_xpath'])[::-1]
    
    for i, elem in enumerate(results['second_level'], 1):
        if elem['role'] not in ['主要内容', '文章', '区块', '普通元素'] or len(elem['xpath'])<1:
            continue
        # for l1_path in tag_level1['tags_xpath']:
        #     if l1_path in elem['xpath']:
        #         if len(elem['text_analysis']['links']) > 0:
        #             for link in elem['text_analysis']['links']:
        #                 logger.debug(f"     * {link['text']} ({link['href']})")
                    
        # for l1_path in tag_level1['contents_xpath']:
        #     if l1_path in elem['xpath']:
        #         if  elem['text_analysis']['word_counts_without_lnks'] > 10:
        #             logger.debug(f"\n ☆☆ 内容元素 ☆☆")
        #             pure_text = elem['text_analysis']['text_content']
        #             logger.debug(f"   xxxxxxxxxx- XPath: {elem['xpath']}")
        #             for link in elem['text_analysis']['links']:
        #                 logger.debug(f"   - XPath: {link['xpath']}")
        #                 pure_text = pure_text.replace(link['text'], '')
        #             # final_report['contents'].add(pure_text)
        #             # logger.debug(f"   - XPath: {elem['xpath']}")
        #             logger.debug(f"   - 文本: {pure_text} ")
        index = next((i for i, prefix in enumerate(tag_level1['contents_xpath']) if elem['xpath'].startswith(prefix)), None)
        
        if index is None:
            continue

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
                
                # 如果需要，也可以单独列出链接
                # links = element.xpath('.//a')
                # for link in links:
                #     link_text = link.text.strip() if link.text else ''
                #     link_xpath = elem['xpath'] + link.getroottree().getpath(link)[len(element.getroottree().getpath(element)):]
                    # logger.debug(f"   - 排除的链接文本: {link_text} (XPath: {link_xpath})")
                    
            except Exception as e:
                logger.error(f"XPath提取失败: {e}")
                continue
                
    logger.debug("\n=== L结构分析报告 (结论)===\n")
    # for i, elem in enumerate(results['first_level'], 1):
        # if elem['role'] == 'header':
    
    
                
# 使用示例
if __name__ == "__main__":
    sample_html = """
<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <meta http-equiv="pragma" content="no-cache">
                <meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
                <meta http-equiv="expires" content="0">
		<meta name="viewport" content="width=1200">
<meta name="viewport" content="width=device-width,height=device-height, user-scalable=no,initial-scale=1, minimum-scale=1, maximum-scale=1,target-densitydpi=device-dpi">
		<meta name="apple-mobile-web-app-capable" content="yes">
		<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
                <meta name="keywords" content="">
		<title>辽宁省2024年高素质农民培育省级重点班开班-东北新闻网</title>
		<meta name="keywords" content="辽宁东北新闻门户">
		<meta itemprop="name" content="辽宁东北新闻门户">
		<link href="/channel-home/nen/css/index.css" rel="stylesheet" type="text/css">
		<link href="/channel-home/nen/css/content_bd_sz.css?v=1.0.2" rel="stylesheet" type="text/css">
<link rel="icon" type="image/png" sizes="16x16" href="/channel-home/nen/images/logoico.png"/>
<link rel="icon" type="image/png" sizes="32x32" href="/channel-home/nen/images/logoico32.png">
<link rel="icon" type="image/png" sizes="48x48" href="/channel-home/nen/images/logoico48.png">
<link rel="icon" type="image/png" sizes="96x96" href="/channel-home/nen/images/logoico96.png">
<link rel="apple-touch-icon-precomposed" sizes="180x180" href="/channel-home/nen/images/logoico180cir.png">
                <script type="text/javascript" src="/channel-home/nen/js/index20210608.js"></script>
		<style type="text/css">
* {
		box-sizing:border-box;
	}
	html {
	    font-size: calc(100vw / 18.75);
	}
	body {
	  -webkit-text-size-adjust: none;
	  color: #000;
	  font: 0.14rem/1.8 "Microsoft Yahei", -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", STHeiti, "Microsoft Yahei", Tahoma, Simsun, sans-serif;
	}
html {background:none;}
   video { width:700px;}
.list_h_wx {
			position: relative;
			width: 100px;
			line-height: 40px;
			height: 40px;
			top: -50px;
			left: 1100px;
			z-index: 9;
			display: flex;
		}

		.list_h_wx p {
			line-height: 30px;
			float: left;
		}

		.list_h_wx img {
			height: 35px;
			float: left;
			margin-top: 5px;
		}
		
		.ct {
                        width:100%;
			position: relative;
                        background:#ffffff;
		}
		
#qrcode {
             width: 120px;
    height: 120px;
    position: absolute;
    right: -132px;
    top: -70px;
}
.list_h h4 {
    width: 100%;
    line-height: 36px;
    float: left;
    text-align: center;
    margin: 0px !important;
    border-bottom: 1px solid #0052B2;
    padding-bottom:5px;}

.list_h {
    width: 100%;
        border-bottom: 0px solid #0052B2;
}	



.bg_topbg {
    width: 100%;
    height: 65px;
    background: url(http://ln.nen.com.cn/channel-home/nen/images/bg_bg.jpg) left top repeat-x;
    overflow: hidden;
}
 .redbg {
   
  margin:0px auto !important;
    font-size:0px;
   
}  
.list {
    width: 100%;
    padding-top: 80px;
    padding-bottom: 20px;
}
.list ul li {
    width: 100%;
    position: relative;
    overflow: hidden;
    margin-bottom: 20px;
    padding-bottom: 10px;
    padding-left:20px;
    border-bottom: 1px solid #eeeeee;
}
.list ul li::before {
    content: "";
    width: 5px;
    height: 5px;
    background: #050505;
    border-radius: 50%;
    position: absolute;
    left: 0;
    top: 14px;
    -webkit-transform: translateY(-50%);
    -moz-transform: translateY(-50%);
    -ms-transform: translateY(-50%);
    -o-transform: translateY(-50%);
    transform: translateY(-50%);
}
.list ul li a {
    max-width: 680px;
    letter-spacing: 2px;
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 0;
    color:#050505;
    display: block;
    float: left;
}
.list ul li span {
    font-size: 16px;
    color: #888;
    line-height: 36px;
    display: block;
    float: right;
    width:200px;
}
.list h4 {
    color: #0052b2;
    font-size: 24px;
    border-bottom: 4px solid #d5d5d5;
    padding-left: 5px;
    padding-bottom: 10px;
}
.list h4 span {
    border-left: solid 2px #5252b2;
    padding-left: 15px;
}
 @media (min-device-width:320px) and (max-width:1023px), (max-device-width:480px)
 {

  .redbg {
    text-align: left;
    color: rgb(255, 255, 255);
    width:1000px;
    height: 2.3em;
    font: 2.3em/230% 微软雅黑;
    background: #cc0000;
    margin: 0px auto !important;
}  
body {
	background:none;
	margin:0 auto;
	color:#000;
}
.w1280 {
    width: 100vw;
}
.t_fbh_snr {
		    margin: 1px auto 0px;
			padding:1rem;
		}
		.xwzw_t3 {
		    padding: 30px 0 40px 0;
		    margin: 70px 0 0 0;
		}
		.xwzw_title {
		    font-size: 1.2rem;
		    padding: 0;
		}
.ph-body .main, .ct {
    width: 100%;
    margin: 0 auto;
    clear: both;
}

.list_sz {
    width: 98%;padding-left: 20px;
  
 
}
.list_sz p {
   font: normal 2.2em/200% 微软雅黑;
    margin: 8px 0;width: 900px;padding-left: 25px;text-align: justify;
}

.footer {
    width: 1000px;
    margin: 0 auto;
    border-top: none;
    clear: both;
    overflow: hidden;
}



.biaoz2 {
    width: 1000px;
    float: left;
    color: red;
    text-align: center;
    padding-bottom: 10px;
    border-bottom: 1px solid #0052B2;
}

.list_sz span {
     text-align: right;
    padding-right:50px;  font: bold 2em/150% 微软雅黑;
 width: 1000px;
}


.bd h2 {
     font: bold 1.3em/150% 微软雅黑;
    font-weight: bold;
    color: #7d7d7d;
    padding-bottom: 25px;
    border-bottom: 1px solid #0052B2;
 padding-left: 35px

}



.bd {
    width: 1000px;
    float: left;
    padding: 0 !important;
}

.list_h 

{
    width: 100%;
    border-bottom:0px solid #0052B2;
}

.list_h h2 {
   
     text-align: left;
   font: bold 1.8em/150% 微软雅黑;
    color: #18559f;
    width:100%;
border-bottom:0px solid #0052B2;

padding-bottom:20px;
}



    
 .logoh{ display:none;}
.head{ display:none;}   
  .bg_topbg { display:none;} 
 .ph-bd { display:none;}  
   .c { width:1000px; } 
.info  { display:none;}
.w1200 { display:none;}
.list_h h4{ line-height: 36px;
    float: left; font: 1em/150% 微软雅黑;letter-spacing:1px;
    text-align: center;
    margin: 0px !important;
    border-bottom: 1px solid #0052B2;
    padding-bottom: 20px;}

 .list_h h3{  
        font: 0.9em/150% 微软雅黑;
    float: left;
    width: 100%;
    line-height: 55px;
    text-align:justify;
    text-indent: 2em;
    color: #504b4b;
    padding-bottom: 20px;
}
.list_h_wx,.sharewx { display:none;}
}
@media screen and (min-width:0px) and (max-width: 915px) {
.list ul li a {
    display: block;
    float: none;
}
.list ul li span {
    display: block;
    float: none;
}
iframe {width:100%;max-height:220px;margin:0 auto;}
}
@media screen and (orientation:landscape) and (max-width: 1023px){
        .xwzw_title {
            font-size: 0.8rem;
        }
        .xwzw_t2 {
            font-size:0.5rem;
            line-height: 2;
        }
        .t_fbh_st,.xwzw_t1 .fontSize {font-size:0.4rem;}
}
  </style>
	</head>
	<body style="background:#f4f4f4;">
		
	<!DOCTYPE html>
<html>
	<head>
                <meta http-equiv="pragma" content="no-cache">
                <meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
                <meta http-equiv="expires" content="0">
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<meta name="apple-mobile-web-app-capable" content="yes">
		<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
                
		<title>${channel_name!""}</title>
		<meta name="keywords" content="东北新闻网">
		<meta itemprop="name" content="东北新闻网">
		<style type="text/css">
.ph-bd {
    background: #f4f4f4;
    padding: 15px 0;    
}
.ph-bd-top {
    background: #fcfcfc;
    padding: 15px 0;
}
.logoh {
    width: 1280px;
    height: auto;
    clear: both;
    overflow: hidden;
    margin: 0 auto 0;
    position: relative;
    background:none;
    
}
.logow{width:310px;float:left;}
.logow img{width:310px;height:74px;}
.logo {
    width: 315px;
    height: 85px;
    background: url(/channel-home/nen/images/logo.png) left 3px no-repeat;
    float: left;
}
.nav {
    width: 1200px;
    height: 113px;
    clear: both;
    margin: 0 auto 10px;
    position: relative; 
}

.navBox {
    width:800px;
    height:auto;
    line-height:25px;
    float:left;
    font-size:18px;
    margin-top: 10px;
    display:flex;
    flex-wrap:wrap;
    margin-left: 10px;
}
.navBox a {
    flex-grow:0;
    flex-shrink:0;
    flex-basis:auto;
    font-size: 18px;
    text-align:left;
}
.navBox a:nth-of-type(1),.navBox a:nth-of-type(4),.navBox a:nth-of-type(5),.navBox a:nth-of-type(6),.navBox a:nth-of-type(7),.navBox a:nth-of-type(8) {
    flex-basis:66px;
}
.navBox a:nth-of-type(2) {
    flex-basis:107px;
}
.navBox a:nth-of-type(3) {
    flex-basis:105px;
}
.navBox a:nth-of-type(9) {
    flex-basis:90px;
}
.navBox a, .navBox span {
    float:left;
    margin-top:0px;
    margin-right:5px;
}
.navBox span {
    float:none;
    margin-top:0px;
    margin-right:6.8px;
    margin-left:6.8px;
}
.navBox .in{padding-right:12px;}
.navBox .it{padding-right:12px;}
.navBox .tjy {padding-right: 14px;}
.navthreen {
    width: 760px;
    height: auto;
    float: left;
    margin-left: 5px;
}
.top_listone {
    width: 970px;
    height:auto;
    background:#f3f3f3;
    float: right;
    margin-left: 0;
}
.navrightjb {
    width: 200px;
    height: auto;
    float: right;
}
.w300 {width: 290px;margin-top: 10px;}
.search {
    width: 20%;
}

.search .search-name {
    float: left;
    display: block;
    font-size: 14px;
    line-height: 30px;
    color: #083b90;
}

.search .search-box {
    float: none;
    width: 100%;
    height: 28px;
    padding-left: 12px;
    -webkit-box-sizing: border-box;
    -moz-box-sizing: border-box;
    box-sizing: border-box;
    -webkit-border-radius: 15px;
    -moz-border-radius: 15px;
    border-radius: 15px;
    border: none;
    background: #fff;
    box-sizing: border-box;
}

.search .search-box .search-input {
    display: block;
    float: left;
    line-height: 26px;
    width: 150px;
    height: 26px;
    font-size: 14px;
    outline: 0;
    border: 0;
    color: #8d9fab;
}

.search .search-box .search-btn {
    float: right;
    width: 55px;
    height: 28px;
    -webkit-border-radius: 15px;
    -moz-border-radius: 15px;
    border-radius: 15px;
    background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTM4IDc5LjE1OTgyNCwgMjAxNi8wOS8xNC0wMTowOTowMSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTcgKFdpbmRvd3MpIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOkUzNDJDMTUzQzFFQjExRUJBODk4RkQ5MTlBMzBDMUVBIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOkUzNDJDMTU0QzFFQjExRUJBODk4RkQ5MTlBMzBDMUVBIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6RTM0MkMxNTFDMUVCMTFFQkE4OThGRDkxOUEzMEMxRUEiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6RTM0MkMxNTJDMUVCMTFFQkE4OThGRDkxOUEzMEMxRUEiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz71eop8AAABsElEQVR42mL8//8/Aww8ePjY8fDhk7UgGiYmLS1x0trKrF1dTXkjAxJghGncsXP/5NNnLuSA2Jqaqmv4+fgeff78Rfra9VuhQDVM2lrqK4MCvSLgOkEat27bM72ppe///gNHm0B8dHzk6MlKkPzylRs2w8QYnj59bgYS3LvvSBs2TQjNpypA6q5euxkG4jMBbZvJyMj4z8nRuooBD7C2Mu1gY2P7vG373ukgPtOLl68NNDVU1zAQAXR1NZd8//5D6MePnwJMIAEREaHrxGgUEuS/A6K/fPkqCdb4EmgrMRrfvHmnBaK5ubleMklIiJ2/eeuuPzEar1y9GcHOzvaJk5PjHZOnh1M2SBAUSPg07dl7uOv379/cnh7OWSA+i4y05HEjQ93Z585fTgMlCBdnuxKQqTANIMV79x9pP336Qi6Iz8vL/Qwl5QBtnAXUnApiy8pKH+Hn4330+csXqYcPnzgg28zBwf4hKyNBgxE5rd6799Dt6PHT5Q8ePHZCpFXJEzbWZm2g5AeLQ2FhwZsoGpHT8I8fPwSAEf6FiYnpN0wQmMostu3YN+3Dh08KAAEGAMAv85XozbtPAAAAAElFTkSuQmCC) center center no-repeat;
    cursor: pointer;
}
.search_icon1{background:url(/channel-home/nen/images/w40.png) no-repeat left center;padding:0 0 0 20px;margin:0 0 0 10px;}
.search_icon2{color: #ff0000;background:url(/channel-home/nen/images/w41.png) no-repeat left center;padding:0 0 0 20px;margin:0 0 0 10px;}
.gsgg {color: #ff0000;background:url(/channel-home/nen/images/w47.png) no-repeat left center;padding:0 0 0 20px;margin:0;}

.left {
    float: left;
}
.right {
    float: right;
}
.clearfix {
    display: block;
}
.weather {
    width: 80px;
    height: 26px;
    line-height: 26px;
    margin: 0 10px;
    text-align: center;
}
.emall {
    margin-left: 40px;
    width: 30px;
    height: 30px;
    float: left;
    border: 0;
}
.emall img {
    border: 0;
}
.telephone {
    width: 150px;
    height: 30px;
    float: left;
    margin-left: 20px;
}
.logow {width:auto;}
.logow img {width:auto;}


		</style>
	</head>
	<body>
<div class="ph-bd-top">
<div class="logoh">
    <div class="clearfix">
						<div class="tb_text left"><p style="width:100px;float:left;margin:0px"><span id="localtime"></span></p><a href="http://www.nen.com.cn/channel-home/tgyx/tg.shtml" class="search_icon2">投稿邮箱</a></div>
						<div class="tb_text left" style="padding:0 0 0 30px;">
                                                    <span style="display:inline-block;">新闻热线 024-23187042</span> 
                                                    <span style="display:inline-block; padding-left:6px;">值班电话 024-23186204</span>
                                                </div>
                                                <div class="tb_text left" style="padding:0 0 0 30px;">
                                                    <span style="display:inline-block;"><a href="http://gsgg.nen.com.cn" target="_blank" class="gsgg">公示公告频道招商：</a>  024-23186593</span>
                                                </div>
						<div class="search right clearfix searchPos ">
							<div class="clearfix form search-box" id="f1">
								<input class="search-input" id="inputwd" type="text"
								onmouseoff="this.className='input_off'" autocomplete="off" maxlength="255"
								value="" name="wd" placeholder="搜索" data-inputcolor="#9c9c9c" />
								<a href="/channel-home/search/search.shtml"><div class="search-btn" id="searchSubmit" type="submit" name="btn" value=""></div></a>
							</div>
						</div>
					</div>
</div>
</div>
<div class="ph-bd">
			<!--顶部导航-->
			<div class="logoh">
			  <div class="logow">
                                
                                <div style="float:left;"><a href="http://www.nen.com.cn/"><img src="/channel-home/nen/images/w37nen.png" alt="东北新闻网" /></a></div>
                            <div style="float:left;"><a href="http://www.nen.com.cn/channel-home/bdrm/bdrm.shtml" target="_blank"><img src="/channel-home/nen/images/w37bd.png" alt="北斗融媒" /></a></div>
                          </div>
			  <div class="top_listone">
			  <div class="navthreen fwryh">
				<div class="navBox">
			    	    <a href="http://liaoning.nen.com.cn" target="_blank">辽宁</a>
                                    <a href="http://review.nen.com.cn" target="_blank">北斗时评</a>
                                    <a href="http://ms.nen.com.cn" target="_blank"><span style="float:none;margin:0;letter-spacing:4px;margin-left:4px;">民生帮</span></a>
                                    <a href="http://zt.nen.com.cn/" target="_blank">专题</a>
                                    <a href="http://health.nen.com.cn/" target="_blank">健康</a>
                                    <a href="http://finance.nen.com.cn" target="_blank">财经</a>
                                    <a href="http://job.nen.com.cn/" target="_blank">人才</a>
                                    <a href="http://piyao.nen.com.cn/" target="_blank">辟谣</a>
                                    <a href="http://wmln.nen.com.cn" target="_blank">文明辽宁</a>
    			    </div>
                                <div class="navBox">
                                    <a href="http://news.nen.com.cn" target="_blank">新闻</a>
                                    <a href="http://video.nen.com.cn/" target="_blank">融<span>·</span>视频</a>
                                    <a href="http://xiaofei.nen.com.cn" target="_blank">消费维权</a>
                                    <a href="http://nongye.nen.com.cn/" target="_blank">农业</a>
                                    <a href="http://liaoning.nen.com.cn/network/liaoningnews/lnnewskejiao/list/indexHome.shtml" target="_blank">科技</a>
                                    <a href="http://edu.nen.com.cn/" target="_blank" style="flex-basis: 62px;">教育</a>
                                    <a href="http://zfcg.nen.com.cn/" target="_blank" style="flex-basis: 141px;">政府采购/拍卖</a>
                                    <a href="http://gsgg.nen.com.cn/" target="_blank" style="flex-basis: 90px;">公示公告</a>
    			    </div>
			  </div>
                          <div class="navrightjb">

					

					<div class="clearfix phoneNone" style="float:right;"><a href="http://piyao.nen.com.cn/" target="_blank"><img src="/channel-home/nen/images/w38-syr-2.jpg"></a></div>
				</div>
			</div>
			</div>
			<!--顶部导航结束-->
			</div>
	</body>
<script type="text/javascript">
function showLocale(objD){
	var str,colorhead,colorfoot;
	var yy = objD.getYear();
	if(yy<1900) yy = yy+1900;
	var MM = objD.getMonth()+1;
	if(MM<10) MM = '0' + MM;
	var dd = objD.getDate();
	if(dd<10) dd = '0' + dd;
	var hh = objD.getHours();
	if(hh<10) hh = '0' + hh;
	var mm = objD.getMinutes();
	if(mm<10) mm = '0' + mm;
	var ss = objD.getSeconds();
	if(ss<10) ss = '0' + ss;
	var ww = objD.getDay();
	if  ( ww==0 )  colorhead="<font color=\"#000000\">";
	if  ( ww > 0 && ww < 6 )  colorhead="<font color=\"#000000\">";
	if  ( ww==6 )  colorhead="<font color=\"#000000\">";
	if  (ww==0)  ww="星期日";
	if  (ww==1)  ww="星期一";
	if  (ww==2)  ww="星期二";
	if  (ww==3)  ww="星期三";
	if  (ww==4)  ww="星期四";
	if  (ww==5)  ww="星期五";
	if  (ww==6)  ww="星期六";
	colorfoot="</font>"
	str = colorhead + yy + "." + MM + "." + dd + " " + colorfoot;
	return(str);
}

function tick(){
	var today;
	today = new Date();
	document.getElementById("localtime").innerHTML = showLocale(today);
	window.setTimeout("tick()", 1000);
}

tick();

</script>
</html>

			
		
		
		
            <div class="t_fbh_st_bg">
			<div class="w1280 t_fbh_st">您当前的位置 ：<a href='http://www.nen.com.cn'>东北新闻网</a>>><a href='http://nongye.nen.com.cn/network/nypd/index.shtml'>农业频道</a>>><a href='http://nongye.nen.com.cn//network/nypd/nyyw/index.shtml'>农业要闻</a></div>
		</div>
        
        <div class="w1280 t_fbh_snr">
            <div class="list_h">
         <div class="xwzw_title">辽宁省2024年高素质农民培育省级重点班开班</div>

   <h2></h2>
   <h3></h3>
         <div class="xwzw_t1">
            <span class="fontSize">2024-10-28 09:54:09</span>
            <span class="fontSize">&nbsp;&nbsp;&nbsp;来源：辽宁日报</span>
            <span class="sharewx" style="position:relative;">
                    分享到:<img src="/channel-home/nen/images/weixin.png" id="share">
                    <input type="hidden" id="url" value="" />
                    <div id="qrcode" style="display: none;">
			<span style="font-size: 12px;text-align: center;">
				用微信扫码二维码<br/>
				分享至好友和朋友圈
			</span>
		    </div>
                </span>
        </div>
        </div>
         
		
            
                <div class="xwzw_t2">
                    
                    <p>
                        <p>　　近日，辽宁省2024年高素质农民培育省级重点班——辽宁省畜牧特色产业农业经理人班在鞍山市正式开班。</p><p>　　今年，我省高素质农民培育省级重点班重点面向承担粮油种植、农机作业及畜牧、食用菌等产业的种养大户、农机大户、家庭农场主、农业社会化服务主体负责人，返乡创业创新人员以及农业国际贸易与投资经纪人等开展培育。全省培育各类经营管理型高层次人才1000名，其中围绕粮油单产提升专题培训行动培育粮油生产高层次人才800人;围绕畜牧、食用菌和农业国际贸易与投资培训需求培育相关高层次人才200人。</p><p>　　为确保培训取得实效，此次省级重点班创新培育模式，全程抓培育过程监管，以便发挥好省级重点班的示范引领作用。在班型模块设置上，构建起综合素养、专业技能、能力拓展3个培训模块，线上线下融合培训;在课程内容设置上，紧紧围绕农业发展主导产业、优势特色产业人才需求，坚持课堂培训与实习实训并举，遴选并深入现代农业园区、农业龙头企业、新型农业经营主体等，提高培训质量和效果。</p><p>　　(记者 胡海林)</p><p><br/></p>
                    </p>
                    <div style="text-align:right;">责任编辑：宋军</div>
                </div>
                
                <div class="list">
                    
                    <ul>
                     </ul>
                </div>

                <div class="erweima" style="width:100%;margin:80px auto -40px auto;float:none;overflow:hidden;">
			<div style="width:50%;float:left;">
                            <p><img src="/channel-home/nen/images/w15.jpg"></p>
                            <p>东北新闻网微博</p>
                        </div>
			<div style="width:50%;float:left;">
                            <p><img src="/channel-home/nen/images/w16.jpg"></p>
                            <p>北斗融媒</p>
                        </div>
		</div>
                <div class="xwzw_t3">
                    <p>*本网站有关内容转载自合法授权网站，如果您认为转载内容侵犯了您的权益，<br>
                       请您来信来电(024-23187042)声明，本网站将在收到信息核实后24小时内删除相关内容。
                       </p>
               </div>
              
            
        </div>
		<div class="ct">
			 <!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<meta name="apple-mobile-web-app-capable" content="yes">
		<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
              
                <meta http-equiv="pragma" content="no-cache">
                <meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
                <meta http-equiv="expires" content="0">
		<title>${channel_name!""}</title>
		<meta name="keywords" content="东北新闻网">
		<meta itemprop="name" content="东北新闻网">
		<style type="text/css">
			
			/**************** footer *************/
			.footer {
    width: 1280px;
    margin: 0 auto;
    border-top: none;
    clear: both;
    overflow: hidden;
}
			/* fNav */
			.fNav_Box {
				width:1200px;
				margin:15px auto 10px;
				border-bottom:1px dashed #ccc;
				clear:both;
				overflow:hidden;
			}
			.fNav, .fNav_info {
				float:left;
				_display:inline;
				width:150px;
				height:75px;
				margin-left:14px;
				margin-bottom:15px;
				font-size:12px;
				padding:10px 0;
			}
			.fNav {
				line-height:25px;
				background:#E8E8E8;
			}
			.fNav:hover {
				background:#033266;
				color:#fff;
			}
			.fNav:hover a{
				color:#fff;
			}
			.fNav strong {
				display:block;
				margin:0 0 0 15px;
			}
			.fNav strong a {
				width:auto;
				margin-left:0;
			}
			.fNav a {
				display:inline-block;
				width:52px;
				margin-left:15px;
				white-space:nowrap;
			}
			.fLinks {
				margin:0 auto 10px;
				clear:both;
				overflow:hidden;
				padding-bottom:10px;
				font-size:14px;
			}
			.fLinks h3 {
				width:100%;
				height:30px;
				font-size:16px;
				font-weight:bold;
				color: #2e5389;
				
			}
			.fLinks a {
				margin-right:13px;
			        line-height: 30px;
			}
			.info {
				border-bottom:1px dashed #ccc;
				padding:15px 0;
			}
			.fnav {text-align:center;}
			.crBox {
				width:100%;
				height:25px;
				line-height:25px;
				background:#303030;
			}
			.cR {
				width:1000px;
				height:25px;
				line-height:25px;
				color:#fff;
				text-align:center;
				margin:0 auto;
			}
			.focus {
				width:320px; 
				height:220px; 
				margin-bottom:10px;
			}
			/*底部*/
			.footernew{color:#515151;font-size:12px;margin: 30px auto;overflow:hidden;text-align:center;}
			.footheight{width:80%;display: flex;
    overflow: hidden;
    align-items: center;
    justify-content: space-around;}
.fnav a {padding:0 5px; font-size:14px;}
			.footernew a{color:#515151;text-decoration:none;}
			.footernew a.lchot{color:#BD0A01;}
			.footernew a:hover{color:#BD0A01;text-decoration:underline;}
			.footernew a:visited{color:#515151;}
			.footernew div{margin:0 auto;}
			.footernew p{width:170px;border:1px solid #D2D2D2;float:left;font-size:12px;margin:6px;padding:0;text-align:center;overflow:hidden;}
			.footernew .fl{width:24%;float:left;padding:10px 0 0 0;}
                        .footernew p:nth-of-type(6) .fl{padding:5px 0 0 0;}
			.footernew .fr{width:74%;float:right;padding:5px 0px 0 0;}
.footernew .fr .lcblack{line-height:40px;}
.footernew p:nth-of-type(1) img,.footernew p:nth-of-type(2) img,.footernew p:nth-of-type(3) img {width: 100%;height: 100%;}
.footernew p:nth-of-type(4) img,.footernew p:nth-of-type(5) img {width: 80%;}
.footernew p:nth-of-type(6) img {width: 70%;}
	



		
		@media screen and (max-device-width :960px)  {
html {font-size: calc(100vw / 18.75);}
.footer {
    width: 100%;
}
.footernew p {width:49%;height:2rem;font-size:0.6rem;margin:0.1rem 0;line-height: 1rem;}
    .footernew .fl{width:25%; padding:0; margin-left:0.2rem;}

    .footernew p:nth-of-type(1) img,.footernew p:nth-of-type(2) img,.footernew p:nth-of-type(3) img {width:100%;height:100%;}
    .footernew p:nth-of-type(4) img,.footernew p:nth-of-type(5) img {width:60%;}
    .footernew p:nth-of-type(6) img {width:50%;}
    .footernew p:nth-of-type(4) .fl{margin-top:0.2rem;}
    .footernew p:nth-of-type(5) .fl{margin-top:0.2rem;}
    .footernew p:nth-of-type(6) .fl{margin-top:0rem;}
    .footernew .fr{padding:0;margin-top:0rem;margin-right:0.2rem;}
    .footernew .fr .lcblack{line-height:2rem;}
    .footernew p:nth-of-type(4) .fr{width: 67%;margin-top:0rem;}
    .footernew p:nth-of-type(5) .fr{width: 60%;margin-top:0rem;margin-right:0.6rem;}
    .footernew p:nth-of-type(6) .fr{width: 60%;margin-top:0rem;margin-right:0.6rem;}
    .footheight{width: 98%;display: flex;flex-wrap: wrap;overflow: hidden;align-items: center;justify-content: space-around;}


}
	
		</style>
	</head>
	<body>
			<!-- footer -->
			<div class="footer">
<div class="fbg">
			<div class="info fnav" style="text-align:center;background: none !important;">
<a href="http://www.nen.com.cn/channel-home/gywm/gywm.shtml" target="_blank">关于我们</a>
<a href="http://www.nen.com.cn/channel-home/tgyx/tg.shtml" target="_blank">投稿邮箱</a>
<a href="http://www.nen.com.cn/channel-home/ggbj/ggbj.shtml" target="_blank">广告报价</a>
<a href="http://www.nen.com.cn/channel-home/lianxiwomen/lianxi.shtml" target="_blank">联系我们</a>

			</div>
<div class="fnav" style="background: none !important;">—  辽宁北斗云数字科技技术支持  —</div>
			<div class="fnav" style="background: none !important;">
<span class="spanBlock "><a href="https://beian.miit.gov.cn/" target="_blank">辽ICP备2021005258号-1</a></span>
<!-- <span class="spanBlock ">增值电信业务经营许可证</span> --> 
<!-- <span class="spanBlock ">辽B1.B2-20150111 </span> --> 
<span class="spanBlock ">互联网新闻信息服务许可证</span>
<span class="spanBlock ">21120170001</span>
<span class="spanBlock ">信息网络传播视听节目许可证 0603017</span>
<p style="text-align:center;margin:0 10px;">东北新闻网(www.nen.com.cn)版权所有，未经授权禁止复制或建立镜像</p>
</div>
<div class="cb"></div>
</div>
			<div class="footernew footheight">
                                        <p>
                                                <a href="https://www.12377.cn/" target="_blank"><img src="/channel-home/nen/images/w30.jpg?v=20210906" alt="" /></a>
                                        </p>
                                        <p>
                                                <a href="https://www.lnjubao.cn/" target="_blank"><img src="/channel-home/nen/images/w30-1.jpg" alt="" /></a>
                                        </p>
				        <p>
					<a href="http://www.12377.cn/node_548446.htm" target="_blank">
						<img border="0" alt="举报专区" src="/channel-home/nen/images/newjubao20150205.jpg"></a>
					</p>
					<p>
						<span class="fl"><img border="0" alt="辽公网安备21010202000026号" src="/channel-home/nen/images/jd.gif"></span>
						<span class="fr"><a href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=21010202000026" target="_blank">辽公网安备<br>21010202000026号</a></span>
					</p>
					<p>
						<span class="fl"><img border="0" alt="沈网警备案20040314号" src="/channel-home/nen/images/jd.gif"></span>
						<span class="fr">沈网警备案<br>20040314号</span>
					</p>
					<p>
						<span class="fl"><a href="http://ln.cyberpolice.cn/alertPawsAction.do?method=LOUT" target="_blank"><img border="0" alt="辽宁网警" src="/channel-home/nen/images/sywj.gif"></a></span>
						<span class="fr"><a class="lcblack" href="http://ln.cyberpolice.cn/alertPawsAction.do?method=LOUT" target="_blank" rel="nofollow">辽宁网警</a></span>
					</p>
				</div>
			</div>
			<!-- footer end --> 
	
	</body>
</html>

		</div>
<script src="/channel-home/nen/js/jquery.min.js"></script>
	<script src="/channel-home/nen/js/qrcode.js"></script>
<script src="/channel-home/nen/js/nrimg.js?v=1.0.3"></script>
	<script type="text/javascript">
		$(function(){
                        $('iframe').attr('scrolling','no');
			$('#url').val(window.location.href);
			
			var qrcode = new QRCode("qrcode");
			// 生成二维码的方法
			function makeCode () {
				// 二维码地址 
				var Url = document.getElementById("url");
				if (!Url.value) {
					alert("请输入生成二维码的地址");
					Url.focus();
					return;
				}
				qrcode.makeCode(Url.value);
			}
			makeCode();
			
			$('#share').on('click',function(){
				let temp = $('#qrcode').css('display');
				if(temp=='block') {$('#qrcode').hide()};
				if(temp=='none') {$('#qrcode').show()};
			});
		});
	</script>
	</body>
</html>

    """
    
    print_analysis(sample_html)