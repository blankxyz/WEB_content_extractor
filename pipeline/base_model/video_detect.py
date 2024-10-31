import re
from bs4 import BeautifulSoup, Tag
from typing import Dict, List, Tuple
from collections import defaultdict

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
            
            if index > 1 or current.find_next_sibling(current.name):
                tag_part = f"{tag_part}[{index}]"
            
            components.append(tag_part)
            current = current.parent
        
        return '//' + '/'.join(reversed(components))

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

    # def analyze_text_and_links(self, element: Tag) -> Dict:
    #     """分析元素内的文本和链接数量及内容"""
    #     texts = []
    #     links = []
        
    #     for text in element.stripped_strings:
    #         if not any(parent.name == 'a' for parent in element.parents):
    #             texts.append(text)
        
    #     for link in element.find_all('a'):
    #         links.append({
    #             'text': link.get_text(strip=True),
    #             'href': link.get('href', ''),
    #             'xpath': self.get_xpath(link)
    #         })
            
    #     pure_text = ' '.join(texts)
        
    #     return {
    #         'text_content': pure_text,
    #         'text_length': len(pure_text),
    #         'link_count': len(links),
    #         'links': links,
    #         'text_to_link_ratio': len(pure_text) / (len(links) if links else 1)
    #     }

    def analyze_structure(self, html_content: str) -> Dict:
        """分析HTML结构并返回带XPath的结果，包含文本、链接和视频播放器分析"""
        soup = BeautifulSoup(html_content, 'html.parser')
        body = soup.find('body')
        
        if not body:
            return {"error": "No body tag found"}

        first_level = self._analyze_first_level(body)
        second_level = self._analyze_second_level(body)
        

        
        return {
            "first_level": first_level,
            "second_level": second_level,
            "summary": self._generate_summary(first_level, second_level)
        }

    def _analyze_first_level(self, body: Tag) -> List[Dict]:
        """分析第一层元素，包含文本、链接和视频播放器分析"""
        first_level = []
        
        for element in body.children:
            if not isinstance(element, Tag):
                continue
                
            if element.name in ['script', 'style', 'link']:
                continue
            
            # text_link_analysis = self.analyze_text_and_links(element)
            video_analysis = self.detect_video_player(element)
            
            element_info = {
                "xpath": self.get_xpath(element),
                "tag": element.name,
                "classes": element.get('class', []),
                "id": element.get('id', ''),
                "child_count": len([c for c in element.children if isinstance(c, Tag)]),
                "role": self._get_element_role(element),
                # "text_analysis": text_link_analysis,
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
                
                # text_link_analysis = self.analyze_text_and_links(child)
                video_analysis = self.detect_video_player(child)
                
                child_info = {
                    "xpath": self.get_xpath(child),
                    "tag": child.name,
                    "classes": child.get('class', []),
                    "id": child.get('id', ''),
                    "role": self._get_element_role(child),
                    "parent_tag": parent.name,
                    "parent_xpath": self.get_xpath(parent),
                    # "text_analysis": text_link_analysis,
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
            # total_text_length += elem['text_analysis']['text_length']
            # total_links += elem['text_analysis']['link_count']
            if elem['video_player']['is_player']:
                video_players.append({
                    'xpath': elem['xpath'],
                    'type': elem['video_player']['player_type'],
                    'source_type': elem['video_player']['source_type']
                })
            
        # 统计第二层
        for elem in second_level:
            # total_text_length += elem['text_analysis']['text_length']
            # total_links += elem['text_analysis']['link_count']
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
            # "total_text_length": total_text_length,
            # "total_links": total_links,
            # "overall_text_to_link_ratio": total_text_length / (total_links if total_links else 1),
            "video_players": video_players,
            "video_player_count": len(video_players)
        }

    def contains_video_player(self, html_content):
        """分析HTML结构并返回带XPath的结果，包含文本、链接和视频播放器分析"""
        soup = BeautifulSoup(html_content, 'html.parser')
        body = soup.find('body')

        # 查找所有video和iframe标签
        video_elements = soup.find_all(['video', 'iframe'])

        for element in video_elements:
            if element.name == 'video':
                xpath = self.get_xpath(element)
                return True, xpath
            elif element.name == 'iframe':
                src = element.get('src', '')
                # 判断是否为视频播放器的iframe
                if 'youtube.com' in src or 'vimeo.com' in src:  # 可添加其他视频平台
                    xpath = self.get_xpath(element)
                    return True, xpath

def print_analysis(html_content: str) -> None:
    """打印分析结果，包含文本、链接和视频播放器分析"""
    analyzer = XPathHTMLAnalyzer()
    results = analyzer.analyze_structure(html_content)
    # has_v , video_path = analyzer.contains_video_player(html_content)
    import lxml.html
    print("\n=== HTML结构分析报告（视频播放器分析） ===\n")
    html = lxml.html.fromstring(html_content)
    
    print("\n=== HTML结构分析报告（带文本、链接和视频播放器分析） ===\n")
    
    print("1. 整体统计:")
    # print(f"   - 总文本长度: {results['summary']['total_text_length']} 字符")
    # print(f"   - 总链接数量: {results['summary']['total_links']} 个")
    # print(f"   - 文本/链接比例: {results['summary']['overall_text_to_link_ratio']:.2f}")
    print(f"   - 视频播放器数量: {results['summary']['video_player_count']} 个")
    
    if results['summary']['video_players']:
        print("\n   检测到的视频播放器:")
        for player in results['summary']['video_players']:
            print(f"     * 类型: {player['type']}")
            print(f"       XPath: {player['xpath']}")
            if player['source_type']:
                print(f"       来源类型: {player['source_type']}")
    
    
    
    # print("\n2. 第一层元素:")
    # for i, elem in enumerate(results['first_level'], 1):
    #     print(f"\n   元素 {i}:")
    #     print(f"   - XPath: {elem['xpath']}")
    #     print(f"   - 标签: {elem['tag']}")
    #     print(f"   - 角色: {elem['role']}")
    #     print(f"   - 文本长度: {elem['text_analysis']['text_length']} 字符")
    #     print(f"   - 链接数量: {elem['text_analysis']['link_count']} 个")
    #     print(f"   - 文本/链接比例: {elem['text_analysis']['text_to_link_ratio']:.2f}")
        
    #     if elem['video_player']['is_player']:
    #         print(f"   - 视频播放器: {elem['video_player']['player_type']}")
    #         if elem['video_player']['details']:
    #             print("     详情:")
    #             for k, v in elem['video_player']['details'].items():
    #                 print(f"     * {k}: {v}")
        
    #     if elem['text_analysis']['links']:
    #         print("   - 链接列表:")
    #         for link in elem['text_analysis']['links']:
    #             print(f"     * {link['text']} ({link['href']})")
    
    # print("\n3. 第二层元素:")
    # for i, elem in enumerate(results['second_level'], 1):
    #     print(f"\n   元素 {i}:")
    #     print(f"   - XPath: {elem['xpath']}")
    #     print(f"   - 标签: {elem['tag']}")
    #     print(f"   - 角色: {elem['role']}")
    #     print(f"   - 文本长度: {elem['text_analysis']['text_length']} 字符")
    #     print(f"   - 链接数量: {elem
    
    
    
# def get_xpath(element):
#     """返回元素的XPath"""
#     components = []
#     while element and element.name:
#         # 获取当前元素的标签名
#         tag = element.name
#         # 获取同级元素
#         siblings = element.find_all(tag, recursive=False)
#         # index = 1 if len(siblings) == 1 else siblings.index(element) + 1
#         index = 1
#         components.append(f"{tag}[{index}]")
#         element = element.parent
#     return '/' + '/'.join(reversed(components))


# 使用示例
if __name__ == "__main__":
    sample_html = """
<html><head>

   <meta name="baidu-site-verification" content="code-wIFPjGCeav">
<meta http-equiv="Content-Type" content="text/html; charset=gb2312">
<meta name="baidu-site-verification" content="rrE1i8A5bX">
<meta name="360-site-verification" content="fbbc5bcc044a082aeced717ba4a29939">
<meta name="filetype" content="0">   
<meta name="publishedtype" content="1">   
<meta name="pagetype" content="2"> 
<meta name="catalogs" content="0"> 
<base target="_blank">
<title>东北网-东北网</title>
<meta name="keywords" content="">
<meta name="description" content="">
<link href="//www.dbw.cn/css/stylenew.css" rel="stylesheet" type="text/css">
<script type="text/javascript" src="//heilongjiang.dbw.cn/zt/js/terminator2.2.min.js" async="true"></script><script type="text/javascript" src="https://heilongjiang.dbw.cn/js/jquery3.5.1.js"></script><input type="hidden" id="_o_dbjbempljhcmhlfpfacalomonjpalpko" data-inspect-config="3"><script type="text/javascript" src="chrome-extension://dbjbempljhcmhlfpfacalomonjpalpko/scripts/inspector.js"></script>
<script type="text/javascript" src="//heilongjiang.dbw.cn/zt/js/koala.min.1.5.js"></script>
 <script type="text/javascript" src="//www.dbw.cn/js/script.js"></script>   
<script type="text/javascript" src="//www.dbw.cn/js/2018sy/zzsc-2024.js"></script>
 <script type="text/javascript">
window.onerror=function(){return true;}
$(document).ready(function(){
	$.focus("#focus001");getBg68();
});	
</script> 
<!--原创end-->

<style type="text/css">

</style>

</head>


<!--背景-->
<!--背景end-->


    <body><div class="top">
        <div class="logo fl"><img src="//www.dbw.cn/images/2024/img01.jpg" width="274" height="56" alt=""></div>
       <!-- <div class="bdcs fl">
<div class="bdcs-container">
<input type="text" name="q" class="bdcs-search-form-input" id="baidutxt" value="请输入关键字" onfocus="if (value =='请输入关键字'){value =''}" onblur="if (value ==''){value='请输入关键字'}" placeholder="">
        <div class="bdcs-search-form-submit " id="bdcs-search-form-submit2" onclick="bt();"></div>
<script src="//www.dbw.cn/js/so.js"></script>
    </div>
</div>-->
        <div class="sjb fr"><a href="https://m.dbw.cn/" target="_blank">手机版</a></div>
        <div class="clear"></div>
        </div>
     <!--导航条-->  

<div class="nav">
     <div class="nav_a">
        <div class="nav_a1"><a href="https://ljktx.dbw.cn/index.shtml" target="_blank"><img src="//www.dbw.cn/images/2024/img02.jpg" width="184" height="71" alt=""></a>
         <div class="nav_bt"><ul><li><a href="https://ljktx.dbw.cn/ljtime/kanlj/index.shtml" target="_blank">龙江时间</a></li> <li><a href="https://ljktx.dbw.cn/wmlbo/index.shtml" target="_blank">网媒联播</a></li> <li><a href="https://ljktx.dbw.cn/redjj/index.shtml" target="_blank">热点</a></li><li><a href="https://ljktx.dbw.cn/gjixw/index.shtml" target="_blank">国际</a></li><li><a href="//ljktx.dbw.cn/zti/xwzt/index.shtml" target="_blank">专题</a></li><li><a href="https://tour.dbw.cn/" target="_blank">旅游</a></li>   </ul></div>
         </div>
         <div class="nav_t"><img src="//www.dbw.cn/images/2024/img24.png" width="6" height="139" alt="">
         </div>
        <div class="nav_a2"><img src="//www.dbw.cn/images/2024/img03.jpg" width="240" height="71" alt="">
         <div class="nav_bt"><ul><li><a href="https://ljktx.dbw.cn/lgdrmjz/" target="_blank">微博矩阵</a></li> <li><a href="https://ljktx.dbw.cn/lgdrmjz/" target="_blank">微信矩阵</a></li> <li><a href="https://ljktx.dbw.cn/lgdrmjz/" target="_blank">微视频矩阵</a></li><li><a href="https://ljktx.dbw.cn/lgdrmjz/" target="_blank">看电视听广播</a></li>   </ul></div>
         </div>
          <div class="nav_t"><img src="//www.dbw.cn/images/2024/img24.png" width="6" height="139" alt=""></div>
         <div class="nav_a3"><img src="//www.dbw.cn/images/2024/img04.jpg" width="207" height="71" alt="">
           <div class="nav_bt"><ul><li><a href="//russian.dbw.cn/" target="_blank">Pусский</a></li> <li><a href="//english.dbw.cn/" target="_blank">English</a></li> <li><a href="//hljxinwen.dbw.cn/" target="_blank">조선어</a></li><li><a href="https://www.big5.dbw.cn/" target="_blank">繁体</a></li>   </ul></div>
         </div>
      </div>
    
    </div>

<!--enorth cms page [ enorth parse_date="2024/09/09 09:17:17.017", cost="5", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->
    <!--导航条end-->
 <!-- 广告开始 --> 
<div class="ggt">
    <!--<div class="ggt1"><div class="ggt3_a fl mr5"><a href="#" target="_blank"><img src="//www.dbw.cn/images/2024/img06.jpg" width="460" height="60" alt=""/></a></div><div class="ggt3_a fl mr5"><a href="#" target="_blank"><img src="//www.dbw.cn/images/2024/img07.jpg" width="460" height="60" alt=""/></a></div><div class="ggt3_a fr"><a href="#" target="_blank"><img src="//www.dbw.cn/images/2024/img08.jpg" width="460" height="60" alt=""/></a></div></div>-->
     <div class="ggt1">
         <div class="ggt4_a fl mr12"><a href="https://internal.dbw.cn/system/2022/05/12/058887748.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/855/00301585570_f316d340.jpg" alt="" width="340" height="60" border="0"></a></div>
		 <div class="ggt4_a fl mr12"><a href="https://www.12377.cn/jbxzxq/64d38691937611ebb858c9da04cf59d3_web.html?smallHarmType=64d38691937611ebb858c9da04cf59d3" target="_blank"><img src="//pic.dbw.cn/003/015/855/00301585559_f3a2b57b.jpg" alt="" width="340" height="60" border="0"></a></div>

         <div class="ggt4_a fl mr12"><img src="//pic.dbw.cn/003/015/855/00301585595_b1a83622.jpg" alt="" width="340" height="60" border="0"></div>
         <div class="ggt4_a fr"><a href="https://jydt.harbin.gov.cn/" target="_blank"><img src="//pic.dbw.cn/003/015/869/00301586957_aa4bedcb.jpg" alt="" width="340" height="60" border="0"></a></div>
  </div> 
        <div class="ggt2"><a href="https://internal.dbw.cn/system/2024/07/10/059339347.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/855/00301585596_950396fc.jpg" alt="" width="1400" height="60" border="0"></a></div> 
      <div class="ggt2"><a href="https://heilongjiang.dbw.cn/system/2023/09/08/059203148.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/855/00301585597_8ce55dca.jpg" alt="" width="1400" height="60" border="0"></a></div> 
      <div class="ggt2"><img src="//pic.dbw.cn/003/015/856/00301585613_07a1b383.jpg" alt="" width="1400" height="60" border="0"></div>  
    <div class="ggt3"><ul><li><a href="https://palj.dbw.cn/" target="_blank">平安龙江网</a></li><li><a href="https://zy.dbw.cn/" target="_blank">志愿者服务网</a></li> <li><a href="https://heilongjiang.dbw.cn/system/2017/11/21/057843965.shtml" target="_blank">省法院</a></li><li><a href="https://www.suifenhe.gov.cn/" target="_blank">绥芬河</a></li> <li><a href="https://special.dbw.cn/system/2022/09/02/058967128.shtml" target="_blank">黑龙江省新促会</a></li> <li><a href="https://www.hljtycp.org.cn/newsList/1302" target="_blank"> 黑龙江体彩“6+1”玩法开奖视频</a></li></ul></div>
    <div class="clear"> </div>
</div>

<!--enorth cms page [ enorth parse_date="2024/10/12 09:41:57.057", cost="8", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->  
     <!-- 广告结束 -->  
     <!-- 头条新闻 -->  
<div class="tt">
    <span> <a href="//ljktx.dbw.cn/system/2024/10/30/059380665.shtml" target="_blank">要登绝顶莫辞劳</a></span>

  <div class="list_tt">
<div class="list_tt1"><a href="//ljktx.dbw.cn/system/2024/10/30/059380663.shtml" target="_blank">学习新语｜“中国人探索太空的脚步会迈得更大、更远”</a></div>
<div class="list_tt1"><a href="//ljktx.dbw.cn/system/2024/10/30/059380664.shtml" target="_blank">【讲习所·中国与世界】习近平：中芬树立了国与国平等交往的典范</a></div>
<div class="list_tt1"><a href="//ljktx.dbw.cn/system/2024/10/30/059380662.shtml" target="_blank">看图学习丨筑牢强国建设、民族复兴的文化根基 总书记作出最新部署</a></div>
<div class="list_tt1"><a href="//ljktx.dbw.cn/system/2024/10/30/059380610.shtml" target="_blank">学习卡丨锚定建成文化强国战略目标，总书记这样阐释→</a></div>    </div>
</div>
    <div class="tt2">
        <div class="tt2_1"><a href="//ljktx.dbw.cn/system/2024/10/29/059380393.shtml" target="_blank">习近平在省部级主要领导干部学习贯彻党的二十届三中全会精神专题研讨班开班式上发表重要讲话</a></div>
       <div class="tt2_2"><a href="//special.dbw.cn/system/2021/10/19/058745027.shtml" target="_blank"><img src="//www.dbw.cn/images/2024/img21.jpg" width="200" height="65" alt=""></a></div>
<!--enorth cms page [ enorth parse_date="2024/06/07 14:26:30.030", cost="4", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->  
    <div class="clear"></div>
    </div>
    <!-- 第一屏新闻 --> 
    <div class="box1">
	<div class="box1_l">
 <div class="lht">
		
		 <!-- 代码 开始 -->
<div id="fsD1" class="lunh">  
    <div id="D1pic1" class="fPic">      
<div class="fcon" style="display: block;">
<a target="_blank" href="//ljktx.dbw.cn/system/2024/10/30/059380432.shtml"><img src="//pic.dbw.cn/003/016/000/00301600079_a5ba0b1e.jpg" style="opacity: 0.92;"></a>
<span class="shadow"><a target="_blank" href="//ljktx.dbw.cn/system/2024/10/30/059380432.shtml">亚雪公路改扩建工程交工通车</a></span>
</div>
<div class="fcon" style="display: none;">
<a target="_blank" href="//ljktx.dbw.cn/system/2024/10/30/059380440.shtml"><img src="//pic.dbw.cn/003/016/000/00301600081_ef9e4591.jpg" style="opacity: 1;"></a>
<span class="shadow"><a target="_blank" href="//ljktx.dbw.cn/system/2024/10/30/059380440.shtml">“智”绘“丰”景 穰穰满家 科技赋能为希望的田野绘就稻香金秋</a></span>
</div>
<div class="fcon" style="display: none;">
<a target="_blank" href="//ljktx.dbw.cn/system/2024/10/29/059380356.shtml"><img src="//pic.dbw.cn/003/016/000/00301600074_0b769793.jpg" style="opacity: 1;"></a>
<span class="shadow"><a target="_blank" href="//ljktx.dbw.cn/system/2024/10/29/059380356.shtml">全景式展现出海实力，伊利打造中国乳业首部国际化发展微纪录片</a></span>
</div>
    </div>
    <div class="fbg">  
    <div class="D1fBt" id="D1fBt">  
        <a href="javascript:void(0)" hidelunh="true" target="_self" class="current"><i>1</i></a>  
        <a href="javascript:void(0)" hidelunh="true" target="_self" class=""><i>2</i></a>  
        <a href="javascript:void(0)" hidelunh="true" target="_self" class=""><i>3</i></a>  

   
    </div>  
    </div>  
    <span class="prev"></span>   
    <span class="next"></span>    
</div>  
<script type="text/javascript">
	Qfast.add('widgets', { path: "//heilongjiang.dbw.cn/zt/js/terminator2.2.min.js", type: "js", requires: ['fx'] });  
	Qfast(false, 'widgets', function () {
		K.tabs({
			id: 'fsD1',   //焦点图包裹id  
			conId: "D1pic1",  //** 大图域包裹id  
			tabId:"D1fBt",  
			tabTn:"a",
			conCn: '.fcon', //** 大图域配置class       
			auto: 1,   //自动播放 1或0
			effect: 'fade',   //效果配置
			eType: 'click', //** 鼠标事件
			pageBt:true,//是否有按钮切换页码
			bns: ['.prev', '.next'],//** 前后按钮配置class                          
			interval: 3000  //** 停顿时间  
		}) 
	})  
</script>
<!-- 代码 结束 -->
	  </div>
	</div>

	<div class=" box1_r fr">
		<div class="list1">
			<ul>
			<li class="list_w"><a href="//ljktx.dbw.cn/system/2024/10/30/059380438.shtml" target="_blank">收获在金秋丨育良种 保丰收</a></li>
			<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380436.shtml" target="_blank">国债项目惠民生丨兴修水利润良田</a></li>
			<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380437.shtml" target="_blank">冲刺四季度丨冰雪装备走俏市场</a></li>	
			<li class="list_w list_k"><a href="//ljktx.dbw.cn/system/2024/10/30/059380602.shtml" target="_blank">哈尔滨亚冬会倒计时100天 冰雪同梦 亚洲同心</a></li>
			<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380439.shtml" target="_blank">身在最北方 心向党中央丨王昕欣：乡村孩子的筑梦人</a></li>
			<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380433.shtml" target="_blank">新龙江 新故事丨突破，在99次失败之后</a></li>	
			<li class="list_w list_k"><a href="//ljktx.dbw.cn/system/2024/10/30/059380428.shtml" target="_blank">大庆发布“信用征信助企融资15条”</a></li>
            <li><a href="//ljktx.dbw.cn/system/2024/10/30/059380435.shtml" target="_blank">从百废待兴到百业兴旺生态宜居</a></li>
			<li><a href="//ljktx.dbw.cn/system/2024/10/29/059380356.shtml" target="_blank">全景式展现出海实力，伊利打造中国乳业首部国际化发展微纪录片</a></li>
			</ul>
	  </div>
  </div>
	<div class="cl"></div>
</div>
    <!-- 新闻开始 -->
<div class="box2">
    <div class="box2_a">
    <div class="news-title">
      <h3 class="fl bt-ls"><a href="https://ljktx.dbw.cn/ljtime/ljdis/" target="_blank">地方新闻</a></h3>
        <span class="hui fr"><a href="https://hhrb.dbw.cn/">黑河日报</a> <a href="https://sysrb.dbw.cn/" class="p_l20">双鸭山日报</a></span>
<!--enorth cms page [ enorth parse_date="2024/07/08 14:32:30.030", cost="4", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->
        <div class="clear"></div>
        </div>
        <div class="title_df hui">
        <em><a href="https://story.dbw.cn/" target="_blank">哈尔滨</a></em>
        <em><a href="https://shuangyashan.dbw.cn/" target="_blank">双鸭山</a></em>
        <em><a href="https://suihua.dbw.cn/" target="_blank">绥化</a></em>
         <em><a href="https://heihe.dbw.cn/" target="_blank">黑河</a></em> 
<!--enorth cms page [ enorth parse_date="2024/08/30 16:19:50.050", cost="5", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->
        </div>
        <ul class="titlelist" style="margin-top:5px; ">
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380435.shtml" target="_blank">从百废待兴到百业兴旺生态宜居</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380434.shtml" target="_blank">黑河市爱辉区：打造“老兵驿站”提供家的体验</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380431.shtml" target="_blank">着力打造向北开放战略平台城市 访黑河市委书记李锡文</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380428.shtml" target="_blank">大庆发布“信用征信助企融资15条”</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380426.shtml" target="_blank">国新办举行哈尔滨2025年第九届亚冬会新闻发布会</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/29/059380133.shtml" target="_blank">齐齐哈尔：新街路，完工通车！</a></li>
</ul>
    </div>
    <div class="box2_a m_l25">
    <div class="news-title"><h3 class="fl bt-ls"><a href="//tour.dbw.cn/system/2024/07/03/059336414.shtml" target="_blank">东北网小记者</a></h3><span class="hui fl m_l25"><a href="//tour.dbw.cn/system/2024/07/05/059337384.shtml" target="_blank">加入我们</a></span></div>
        <div class="pic_bgh-k">
<div class="pic_threezu"><a href="//tour.dbw.cn/system/2024/10/18/059376435.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/976/00301597677_75973dba.png" width="210" height="120"></a>
<div class="titbg"></div>
<a href="//tour.dbw.cn/system/2024/10/18/059376435.shtml" target="_blank" class="tit">丰富的一天</a>
</div>
<div class="pic_threezu"><a href="//tour.dbw.cn/system/2024/10/02/059371375.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/942/00301594210_b0162cf5.png" width="210" height="120"></a>
<div class="titbg"></div>
<a href="//tour.dbw.cn/system/2024/10/02/059371375.shtml" target="_blank" class="tit">东北网小记者职业体验营开营</a>
</div>
        <div class="clear"></div>
        </div>
        <ul class="titlelist" style="margin-top:5px; ">
<li><a href="//tour.dbw.cn/system/2024/10/17/059376141.shtml" target="_blank"></a><a href="//tour.dbw.cn/system/2024/10/17/059376141.shtml" target="_blank">中国工农红军哈尔滨李兆麟红军小学东北网小记者校园实践基地成立</a></li>
<li><a href="//tour.dbw.cn/system/2024/10/20/059376962.shtml" target="_blank"></a><a href="//tour.dbw.cn/system/2024/10/20/059376962.shtml" target="_blank">小小消防员 东北网小记者职业体验营第三节课纪实</a></li>
<li><a href="//tour.dbw.cn/system/2024/10/13/059374602.shtml" target="_blank"></a><a href="//tour.dbw.cn/system/2024/10/13/059374602.shtml" target="_blank">东北网小记者职业体验营第二节课：化身“小小气象播报员” 探索气象奥秘</a></li>
<li><a href="//tour.dbw.cn/system/2024/10/01/059371121.shtml" target="_blank"></a><a href="//tour.dbw.cn/system/2024/10/01/059371121.shtml" target="_blank">东北网小记者职业体验营正式启动 第一节课开启小小农艺师探索之旅</a></li>
</ul>
    </div>
    <div class="box2_a m_l25">
    <div class="news-title"><h3 class="fl bt-ls"><a href="https://tour.dbw.cn" target="_blank">文旅</a></h3><span class="hui fl m_l25"><a href="https://auto.dbw.cn/">汽车</a></span>
        <div class="clear"></div>
        </div>
    <div class="pic_bgh-k">
<div class="pic_threezu"><a href="//tour.dbw.cn/system/2024/10/28/059379737.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/995/00301599585_22afa6e9.png" width="210" height="120"></a>
<div class="titbg"></div>
<a href="//tour.dbw.cn/system/2024/10/28/059379737.shtml" target="_blank" class="tit">黑河口岸开通冬季气垫船旅客运输</a>
</div>
<div class="pic_threezu"><a href="//tour.dbw.cn/system/2024/10/24/059378551.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/989/00301598963_5149c3f9.png" width="210" height="120"></a>
<div class="titbg"></div>
<a href="//tour.dbw.cn/system/2024/10/24/059378551.shtml" target="_blank" class="tit">“组团”去南方过冬啦！</a>
</div>        <div class="clear"></div>
        </div>
        <ul class="titlelist" style="margin-top:5px; ">
<li><a href="//tour.dbw.cn/system/2024/10/28/059379869.shtml" target="_blank"></a><a href="//tour.dbw.cn/system/2024/10/28/059379869.shtml" target="_blank">来打卡吧！“冰雪之冠”亮相哈尔滨市颐园广场</a></li>
<li><a href="//tour.dbw.cn/system/2024/10/28/059379874.shtml" target="_blank"></a><a href="//tour.dbw.cn/system/2024/10/28/059379874.shtml" target="_blank">通过验收！哈尔滨地铁3号线安通街车辆基地单位工程竣工</a></li>
<li><a href="//tour.dbw.cn/system/2024/10/24/059378552.shtml" target="_blank"></a><a href="//tour.dbw.cn/system/2024/10/24/059378552.shtml" target="_blank">方正：希望秋天吹来的风 不仅有温柔 还有好运</a></li>
<li><a href="//tour.dbw.cn/system/2024/10/22/059377753.shtml" target="_blank"></a><a href="//tour.dbw.cn/system/2024/10/22/059377753.shtml" target="_blank">创新高！黑河瑷珲机场提前刷新旅客吞吐量历年最高纪录</a></li></ul>
    </div>
    </div>
    <!-- 新闻结束 -->
      <div class="clear"></div>
    <!-- 品宣区开始 -->
    <div class="box3">
    <div class="yuanc-bg">
<div class="yuanc-box">
<div class="bg68comad-n">
 <div class="tmb"></div>
 <div class="focus" id="focus001">
		<ul style="width: 3486.18px;">
        <li style="width: 1743.09px; display: none;">
            <div class="banclj">
                <a href="#" onfocus="this.blur();" target="_blank"></a>
                
<div class="msgj">
    <div class="msgj_1"> <a href="//ljktx.dbw.cn/system/2024/09/13/059364172.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/890/00301589006_ec0d9319.jpg" width="515" height="317"></a></div>
    <div class="msgj_2">
    <div class="msgj_2a"> <a href="//heilongjiang.dbw.cn/system/2022/03/04/058836560.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/865/00301586529_7e895052.jpg" width="370" height="210"></a></div>
   <div class="msgj_2b m_t10"> <a href="//ljktx.dbw.cn/system/2024/10/10/059373461.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/976/00301597633_ec0e07ef.jpg" width="180" height="99"></a></div>
        <div class="msgj_2b m_t10 m_l10"><a href="//heilongjiang.dbw.cn/system/2020/07/03/058451934.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/106/00301510617_ca639e89.jpg" width="180" height="99"></a></div> 
        <div class="clear"></div>
    </div>
     <div class="msgj_3">
   <div class="msgj_2b"><a href="//heilongjiang.dbw.cn/system/2023/04/23/059116480.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/878/00301587872_e51c3e8c.jpg" width="180" height="99"></a></div>
        <div class="msgj_2b m_l10"><a href="//internal.dbw.cn/system/2024/07/08/059338537.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/734/00301573402_3e224210.png" width="180" height="99"></a></div> 
        <div class="clear"></div>
          <div class="msgj_2a m_t10"><a href="//ljktx.dbw.cn/system/2024/09/18/059365810.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/904/00301590436_eb61b042.jpg" width="370" height="210"></a>&gt;</div>
    </div>
</div>
            
            </div>
            </li>
        
      
        <li style="width: 1743.09px;"> 
            
            <div class="banclj">
                <a href="#" onfocus="this.blur();" target="_blank"></a>
                
<div class="msgj">
    <div class="msgj_1"> <a href="//ljktx.dbw.cn/system/2024/10/16/059375552.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/999/00301599996_545ef2e3.png" width="515" height="317"></a></div>
    <div class="msgj_2">
    <div class="msgj_2a"> <a href="//heilongjiang.dbw.cn/system/2024/04/26/059307681.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/878/00301587873_b18668f4.jpg" width="370" height="210"></a></div>
   <div class="msgj_2b m_t10"> <a href="//heilongjiang.dbw.cn/system/2022/12/08/059033022.shtml" target="_blank"> <img src="//pic.dbw.cn/003/014/446/00301444640_ed2fd8a0.jpg" width="180" height="99"></a></div>
        <div class="msgj_2b m_t10 m_l10"><a href="//ljktx.dbw.cn/system/2024/09/03/059360174.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/864/00301586494_bdf97b61.jpg" width="180" height="99"></a></div> 
        <div class="clear"></div>
    </div>
     <div class="msgj_3">
   <div class="msgj_2b"><a href="//ljktx.dbw.cn/system/2024/09/03/059360232.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/864/00301586495_73f92328.jpg" width="180" height="99"></a></div>
        <div class="msgj_2b m_l10"><a href="//heilongjiang.dbw.cn/system/2024/08/07/059350086.shtml" target="_blank"> <img src="//pic.dbw.cn/003/015/814/00301581482_1d3a7975.jpg" width="180" height="99"></a></div> 
        <div class="clear"></div>
          <div class="msgj_2a m_t10"><a href="//heilongjiang.dbw.cn/system/2023/03/31/059102296.shtml" target="_blank"> <img src="//pic.dbw.cn/003/014/705/00301470521_d59968c5.jpg" width="370" height="210"></a></div>
    </div>
</div>
            
            </div>
        </li>
        
		</ul>
     <div class="clear"></div>

    <div class="btnBg" style="opacity: 0.5;"></div><div class="btn"><span style="opacity: 0.4;">?</span><span style="opacity: 0.4;">?</span></div><div class="preNext pre" style="opacity: 0.2;"></div><div class="preNext next" style="opacity: 0.2;"></div></div>
     <div class="yuanc-wz-four bai">
<div class="four1"><a href="//heilongjiang.dbw.cn/system/2024/04/29/059308825.shtml" target="_blank"></a><a href="//heilongjiang.dbw.cn/system/2024/04/29/059308825.shtml" target="_blank">新时代推动高质量发展</a> </div>
<div class="four1"><a href="//ljktx.dbw.cn/system/2024/09/19/059366374.shtml" target="_blank"></a><a href="//ljktx.dbw.cn/system/2024/09/19/059366374.shtml" target="_blank">时代楷模杨士莪</a> </div>
<div class="four1"><a href="//ljktx.dbw.cn/system/2024/09/03/059360162.shtml" target="_blank"></a><a href="//ljktx.dbw.cn/system/2024/09/03/059360162.shtml" target="_blank">能力作风建言献策</a> </div>
<div class="four1"><a href="//heilongjiang.dbw.cn/system/2023/10/17/059224358.shtml" target="_blank"></a><a href="//heilongjiang.dbw.cn/system/2023/10/17/059224358.shtml" target="_blank">创意至上 创新龙江 云展馆</a> </div> <div class="clear"></div> 
 </div>  
  <div class="box3_gg"><a href="//heilongjiang.dbw.cn/system/2024/01/20/059268785.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/865/00301586505_282b36cb.jpg" width="1400" height="80" alt=""></a>

<!--enorth cms page [ enorth parse_date="2024/09/03 14:39:04.004", cost="4", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]--></div>  
 </div>

</div>
</div>
 
    </div>
    
    <!-- 新闻开始 -->
    <div class="box2">
    <div class="box2_a">
    <div class="news-title"><h3 class="fl bt-ls"><a href="https://ljktx.dbw.cn/wmlbo/index.shtml" target="_blank">网媒联播</a></h3>
        <div class="clear"></div>
        </div>
     
        <ul class="titlelist" style="margin-top:5px; ">
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380664.shtml" target="_blank">【讲习所·中国与世界】习近平：中芬树立了国与国平等交往的典范</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380663.shtml" target="_blank">学习新语｜“中国人探索太空的脚步会迈得更大、更远”</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380662.shtml" target="_blank">看图学习丨筑牢强国建设、民族复兴的文化根基 总书记作出最新...</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380655.shtml" target="_blank">【小新的Vlog】布达拉宫迎来“美颜季” 小新带你了解涂料中的...</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380653.shtml" target="_blank">川藏线日记|一碗藏茶见证古道之变</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380652.shtml" target="_blank">“硬核”科技力量助力新疆棉“七十二变” 为幸福生活增光添彩</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380636.shtml" target="_blank">都是航天员 有啥不一样？什么是航天飞行工程师？一文了解</a></li></ul>
    </div>
    <div class="box2_a m_l25">
    <div class="news-title"><h3 class="fl bt-ls"><a href="https://ljktx.dbw.cn/gjixw/index.shtml" target="_blank">国际新闻</a></h3></div>
       
        <ul class="titlelist" style="margin-top:5px; ">
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380650.shtml" target="_blank">从五指山唱到国外！中法童声合唱团相约海南唱响“友谊合声”</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380647.shtml" target="_blank">一名澳大利亚汉学家的“滚石”生活</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380645.shtml" target="_blank">海外话中国｜澳大利亚港口小城与中国的共赢故事</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380643.shtml" target="_blank">赞比亚驻华大使：建交60年，中赞合作为应对地区与全球挑战提...</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380641.shtml" target="_blank">马来西亚拿督翁忠义：中国方案助力东盟提升全球竞争力｜世界观</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380640.shtml" target="_blank">俄专家：金砖机制在世界上的地位将逐年提升</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380639.shtml" target="_blank">“中文热”折射“人文金砖”活力（环球热点）</a></li></ul>
    </div>
    <div class="box2_a m_l25">
    <div class="news-title"><h3 class="fl bt-ls"><a href="https://ljktx.dbw.cn/redjj/index.shtml" target="_blank">热点聚焦</a></h3>
        <div class="clear"></div>
        </div>
    
        <ul class="titlelist" style="margin-top:5px; ">
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380661.shtml" target="_blank">挥拍运动“避险”指南 | 运动是良医</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380628.shtml" target="_blank">产业兴旺促增收 希望的田野上唱响“丰收民歌”</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380619.shtml" target="_blank">全过程精彩回顾 走进神舟十九号载人飞行任务纪实</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380618.shtml" target="_blank">从今年前三季度外贸数据透视经济活力 长三角和粤港澳大湾区亮...</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380615.shtml" target="_blank">跟着总书记探寻中华文明·非遗篇｜把工夫做在光阴里</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380572.shtml" target="_blank">“芝麻团子”憨态可掬 “落日飞天”美景再现 绿水青山间唱响...</a></li>
<li><a href="//ljktx.dbw.cn/system/2024/10/30/059380571.shtml" target="_blank">飞阅中国丨重庆国际物流枢纽园区活力十足</a></li></ul>
    </div>
    </div>
    <!-- 新闻结束 -->
     <!-- 融媒报道 -->
    <div class="box4"> 
   <div class="pro-center">
			<div class="container">
				<div class="pro-content">
					<div class="pro-left">
						<div class="left-title">
					    <img src="//www.dbw.cn/images/2024/img25.png" width="180" height="177" alt=""> </div>
						<!--分类，on状态为当前高亮-->
						<div class="left-category">
							<ul>
								<li class="on">微博矩阵</li>
								<li>微信矩阵</li>
								<li>微视频矩阵</li>
								<li>看电视听广播</li>
								
							</ul>
							
						</div>
					</div>
					<!--对应分类的内容，active状态为显示-->
					<div class="pro-right active" style="margin-top: -30px;">
                        <div class="company_b2b2 clearfix">
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/660/00301566047_f71d5450.jpg" alt="龙广官方微博"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/660/00301566048_716ff67e.png"></dt>
<dd>龙广官方微博</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/660/00301566043_1b7f9385.jpg" alt="黑龙江广播电视台"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/660/00301566044_8a224322.png"></dt>
<dd>黑龙江广播电视台</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/660/00301566045_1996032b.jpg" alt="黑龙江卫视"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/660/00301566046_29c60abd.png"></dt>
<dd>黑龙江卫视</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/660/00301566049_819dd2a2.jpg" alt="新闻夜航"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/660/00301566050_0fe174f5.png"></dt>
<dd>新闻夜航</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/660/00301566037_8ad52981.jpg" alt="东北网"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/660/00301566038_da927bf6.png"></dt>
<dd>东北网</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/660/00301566040_14dddfa1.jpg" alt="东北网新闻官方微博"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/660/00301566042_f44edf73.png"></dt>
<dd>东北网新闻官方微博</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/660/00301566057_3c059e40.jpg" alt="黑龙江体彩"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/660/00301566058_9a588dff.png"></dt>
<dd>黑龙江体彩</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/660/00301566055_ff98ffe4.jpg" alt="黑龙江发布"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/660/00301566056_8135c068.png"></dt>
<dd>黑龙江发布</dd>
</dl>
		</div>
						
					</div>
					<div class="pro-right">
						<div class="company_b2b clearfix">
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/662/00301566218_b6db0036.jpg" alt="直通998"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/662/00301566219_71a47050.png"></dt>
<dd>直通998</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/662/00301566216_1d1be2d1.jpg" alt="一路向北"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/662/00301566217_d9b1c0bd.png"></dt>
<dd>一路向北</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/662/00301566214_c0efc00b.jpg" alt="新闻夜航"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/662/00301566215_6e917ef4.png"></dt>
<dd>新闻夜航</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/662/00301566210_283a9a7a.jpg" alt="三农帮"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/662/00301566211_a6fbca9a.png"></dt>
<dd>三农帮</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/662/00301566208_de10d5de.jpg" alt="龙视少儿频道"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/662/00301566209_907e59da.png"></dt>
<dd>龙视少儿频道</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/662/00301566202_7480acd7.jpg" alt="极光新闻东北网"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/662/00301566203_cfc2bc6d.png"></dt>
<dd>极光新闻东北网</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/662/00301566200_b84969d5.jpg" alt="黑龙江新闻在线"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/662/00301566201_0f929d7b.png"></dt>
<dd>黑龙江新闻在线</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/661/00301566198_727a400a.jpg" alt="黑龙江新闻联播"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/661/00301566199_f5e8374e.png"></dt>
<dd>黑龙江新闻联播</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/661/00301566194_fe11e5fc.jpg" alt="黑龙江卫视"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/661/00301566195_f01431a7.png"></dt>
<dd>黑龙江卫视</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/661/00301566192_e5de6f96.jpg" alt="黑龙江生活广播"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/661/00301566193_7ec24321.png"></dt>
<dd>黑龙江生活广播</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/661/00301566189_637e633f.jpg" alt="黑龙江交通广播"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/661/00301566190_90c1c031.png"></dt>
<dd>黑龙江交通广播</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/661/00301566187_4ea317c1.jpg" alt="高小微"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/661/00301566188_95f76b89.png"></dt>
<dd>高小微</dd>
</dl>		</div>
					</div>
					<div class="pro-right">
					<div class="company_b2b clearfix">
	
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566951_ae7a2d86.jpg" alt="黑龙江视界抖音号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566952_46ac0172.png"></dt>
<dd>黑龙江视界抖音号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566949_bb929b56.jpg" alt="龙视新闻抖音号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566950_214aa7fb.png"></dt>
<dd>龙视新闻抖音号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566910_3ccd60a5.jpg" alt="极光新闻抖音号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566948_71c52900.png"></dt>
<dd>极光新闻抖音号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566906_79496d46.jpg" alt="东北网抖音号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566947_ec6f22e7.png"></dt>
<dd>东北网抖音号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566945_bdc25fd1.jpg" alt="龙视频快手号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566946_e08c2dc4.png"></dt>
<dd>龙视频快手号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566914_dcf170eb.jpg" alt="新闻夜航快手号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566943_6233bbd5.png"></dt>
<dd>新闻夜航快手号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566910_3ccd60a5.jpg" alt="极光新闻快手号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566942_94da7cd6.png"></dt>
<dd>极光新闻快手号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566906_79496d46.jpg" alt="东北网快手号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566941_beb0fb43.png"></dt>
<dd>东北网快手号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566916_0b8ec05b.jpg" alt="这就是黑龙江视频号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566917_61b969ed.jpg"></dt>
<dd>这就是黑龙江视频号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566914_dcf170eb.jpg" alt="新闻夜航视频号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566915_cc1b8671.jpg"></dt>
<dd>新闻夜航视频号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566912_85c26c6e.jpg" alt="极小光与新小闻视频号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566913_93cc3a3e.jpg"></dt>
<dd>极小光与新小闻视频号</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566910_3ccd60a5.jpg" alt="极光新闻视频号"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566911_cb1aab0d.jpg"></dt>
<dd>极光新闻视频号</dd>
</dl>		</div>	
                        
					</div>
					<div class="pro-right">
						<div class="company_b2b clearfix">
	
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/674/00301567469_9c423811.jpg" alt="黑龙江生活广播"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/674/00301567470_9488f9e7.png"></dt>
<dd>黑龙江生活广播</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/674/00301567467_bec4318a.jpg" alt="黑龙江高校广播"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/674/00301567468_46904eda.png"></dt>
<dd>黑龙江高校广播</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/674/00301567461_e6c17874.jpg" alt="黑龙江音乐广播"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/674/00301567462_9ce99110.png"></dt>
<dd>黑龙江音乐广播</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566973_bd1ba8ef.jpg" alt="黑龙江都市女性广播"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566974_39bcb959.png"></dt>
<dd>黑龙江都市女性广播</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566971_7442a950.jpg" alt="黑龙江交通广播"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566972_aab0dc44.png"></dt>
<dd>黑龙江交通广播</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566969_7ef951e7.jpg" alt="黑龙江新闻广播"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566970_2c0517b1.png"></dt>
<dd>黑龙江新闻广播</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566989_44e510ab.jpg" alt="黑龙江农业·科教"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566967_67285213.png"></dt>
<dd>黑龙江农业·科教</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566966_d7822000.jpg" alt="黑龙江影视"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566965_5f4dded4.png"></dt>
<dd>黑龙江影视</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566964_b0a0a46c.jpg" alt="黑龙江少儿"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566963_d525c64c.png"></dt>
<dd>黑龙江少儿</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566962_0094c2b4.jpg" alt="黑龙江文体"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566961_27040766.png"></dt>
<dd>黑龙江文体</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566960_5fe9fce0.jpg" alt="黑龙江新闻法治"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566959_e4f7863a.png"></dt>
<dd>黑龙江新闻法治</dd>
</dl>
<dl>
<dt class="company_img"><img src="//pic.dbw.cn/003/015/669/00301566957_b100d1bc.jpg" alt="黑龙江都市"></dt>
<dt class="hid"></dt>
<dt class="ererima_img hid"><img src="//pic.dbw.cn/003/015/669/00301566958_ef67577d.png"></dt>
<dd>黑龙江都市</dd>
</dl>		</div>	
					</div>
								
                         </div>
			</div>
		</div> 
    </div>
 <div class="ggt5"><a href="https://heilongjiang.dbw.cn/system/2022/01/10/058799884.shtml" target="_blank"><img src="https://www.dbw.cn/images/2024/img22.jpg" width="1400" height="80" alt=""></a></div>
<!--enorth cms page [ enorth parse_date="2024/09/03 14:39:46.046", cost="4", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->

    <!--外文开始--> 
    <div style="width: 1400px; margin: 0 auto; position: relative">
<iframe src="//manage1.dbw.cn/index-waiwen.shtml" name="moreforeign" frameborder="0" width="1400" height="330" scrolling="No"></iframe>   

</div>
    <!--外文結束-->    
 <div class="yqlj">
        <div class="rongmei-k">
            <div class="news-title">
            <div id="biaoqian-over2">
    <ul>
   <li class="active">友情链接</li> 
   <li>地方网联</li>       
        </ul>
            </div>
                
                 <div id="biaoqian-over2_content">    
            <div style="display:block">
<ul class="yq-link">
    <li><a href="//www.people.com.cn" target="_blank">人民网</a></li>
    <li><a href="//original.hubpd.com" target="_blank">人民日报中央厨房</a></li>
    <li><a href="//www.xinhuanet.com" target="_blank">新华网</a></li>
    <li><a href="//www.ifeng.com" target="_blank">凤凰网</a></li>
    <li><a href="//www.cnr.cn" target="_blank">央广网</a></li>
    <li><a href="//www.china.com.cn" target="_blank">中国网</a></li>
    <li><a href="//www.chinanews.com.cn" target="_blank">中新网</a></li>
    <li><a href="//www.gmw.cn" target="_blank">光明网</a></li>  
    <li><a href="//www.taiwan.cn/hxlt" target="_blank">海峡论坛官网</a></li>  
    <li><a href="//www.cri.cn" target="_blank">国际在线</a></li> 
    <li><a href="//www.k618.cn" target="_blank">未来网</a></li>
    <li><a href="//www.voc.com.cn" target="_blank">华声在线</a></li>  
    <li><a href="//www.ahwang.cn" target="_blank">安徽网</a></li>  
    <li><a href="//www.ycwb.com" target="_blank">金羊网</a></li>
    <li><a href="//www.changsha.cn" target="_blank">星辰在线</a></li>
    <li><a href="//www.shangdu.com" target="_blank">商都网</a></li>  
    <li><a href="//www.hsw.cn" target="_blank">华商网</a></li>  
    <li><a href="//www.iqilu.com" target="_blank">齐鲁网</a></li>
    <li><a href="//www.workercn.cn" target="_blank">中工网</a></li>
    <li><a href="//www.shm.com.cn" target="_blank">水母网</a></li>  
    <li><a href="//www.xiancity.cn" target="_blank">西安网</a></li>  
    <li><a href="//www.haiwainet.cn" target="_blank">海外网</a></li>
    <li><a href="//www.dpcm.cn" target="_blank">大鹏新闻网</a></li>  
    <li><a href="//www.guancha.cn" target="_blank">观察者网</a></li>
                </ul>
                
</div>
           <div style="display:none">
                     <ul class="yq-link">
                         <li><a href="//www.enorth.com.cn" target="_blank">北方网</a></li>
                         <li><a href="//www.eastday.com" target="_blank">东方网</a></li>
                         <li><a href="//www.rednet.cn" target="_blank">红网</a></li>
                         <li><a href="//www.southcn.com" target="_blank">南方网</a></li>
                         <li><a href="//www.qianlong.com" target="_blank">千龙网</a></li>
                         <li><a href="//www.dahe.cn" target="_blank">大河网</a></li>
                         <li><a href="//www.sznews.com" target="_blank">深圳新闻网</a></li>
                         <li><a href="//www.hinews.cn" target="_blank">南海网</a></li>
                         <li><a href="//www.anhuinews.com" target="_blank">中安在线</a></li>
                         <li><a href="//www.nen.com.cn" target="_blank">东北新闻网</a></li>
                         <li><a href="//www.gxnews.com.cn" target="_blank">广西新闻网</a></li>
                         <li><a href="//www.chinatibetnews.com" target="_blank">中国西藏新闻网</a></li>
                         <li><a href="//www.ts.cn" target="_blank">天山网</a></li>
                         <li><a href="//www.cnwest.com" target="_blank">西部网</a></li>
                         <li><a href="//www.dzwww.com" target="_blank">大众网</a></li>
                         <li><a href="//www.cnhubei.com" target="_blank">荆楚网</a></li>
                         <li><a href="//www.zjol.com.cn" target="_blank">浙江在线</a></li>
                         <li><a href="//www.hebei.com.cn" target="_blank">长城网</a></li>
                         <li><a href="//www.jschina.com.cn" target="_blank">中国江苏网</a></li>
                         <li><a href="//www.sxrb.com" target="_blank">山西新闻网</a></li>
                         <li><a href="//www.scol.com.cn" target="_blank">四川在线</a></li>
                         <li><a href="//www.xhby.net" target="_blank">新华报业网</a></li>
                         <li><a href="//www.cqnews.net" target="_blank">华龙网</a></li>
                         <li><a href="//www.yunnan.cn" target="_blank">云南网</a></li>
                         <li><a href="//www.qhnews.com" target="_blank">青海新闻网</a></li>
                         <li><a href="//www.newssc.org" target="_blank">四川新闻网</a></li>
                         <li><a href="//www.ynet.com" target="_blank">北青网</a></li>
                         <li><a href="//www.gog.cn" target="_blank">多彩贵州网</a></li>
                         <li><a href="//www.hebnews.cn" target="_blank">河北新闻网</a></li>
                         <li><a href="//www.gansudaily.com.cn" target="_blank">每日甘肃网</a></li>
                         <li><a href="//www.lnd.com.cn" target="_blank">北国网</a></li>
                         <li><a href="//www.gscn.com.cn" target="_blank">中国甘肃网</a></li>
                         <li><a href="//www.nmgnews.com.cn" target="_blank">内蒙古新闻网</a></li>
                         <li><a href="//www.syd.com.cn" target="_blank">沈阳网</a></li>
                         <li><a href="//www.sxgov.cn" target="_blank">黄河新闻网</a></li>
                         <li><a href="//www.nxnews.net" target="_blank">宁夏新闻网</a></li>
                         <li><a href="//www.jiaodong.net" target="_blank">胶东在线</a></li>
                         <li><a href="//www.jxcn.cn" target="_blank">大江网</a></li>
                         <li><a href="//www.runsky.com" target="_blank">天健网</a></li>
                         <li><a href="//www.fjsen.com" target="_blank">东南网</a></li>
                         <li><a href="//www.jxnews.com.cn" target="_blank">中国江西网</a></li>
                         <li><a href="//www.cnjiwang.com" target="_blank">中国吉林网</a></li>
                         <li><a href="//www.sdchina.com" target="_blank">中国山东网</a></li>
                         <li><a href="//www.jxgdw.com" target="_blank">今视网</a></li>
                         <li><a href="//www.iyaxin.com" target="_blank">亚心网</a></li>
                         
               
               </ul>
                     </div>
             </div>
              
        </div>   
     </div>
<!--enorth cms page [ enorth parse_date="2024/07/08 14:20:10.010", cost="7", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->
     <div class="clear"></div>
     </div>
   <!-- 右侧机器人-->
<div id="moquu_wxin" class="moquu_wxin"><a href="https://so.dbw.cn/sousuo.html" target="_blank"><div class="moquu_wxinh"></div></a></div> 
  <script src="//www.dbw.cn/js/2024/banquan.js"></script><div class="footer-di hui"><img src="https://www.dbw.cn/images/2018/logo-di.gif" width="160" height="50"><br><div class="four2"><a href="https://ljktx.dbw.cn/lxwm/index.shtml" target="_blank">联系我们</a> </div> 严格遵守保密法律法规，严禁在互联网发布涉密信息。<br>黑龙江东北网络台版权所有 Copyright◎2001-2018 WWW.DBW.CN　All Rights Reserved.<br>增值电信业务经营者证件号：黑B2-20080973-1 国新网许可证编号：2312006001　 哈公网监备23010002003717号   公安备案号：23010302000745<br>广告经营许可证号：2301000000007　 <a href="https://www.dbw.cn/images/01234.jpg" target="_blank">广播电视节目制作经营许可证：黑字第083号</a>　 信息网络传播视听节目许可证 0805077　 互联网新闻信息服务许可证 23120240003<br>ICP(互联网信息服务)备案号 黑B2-20131557-16 <a href="//ljktx.dbw.cn/jbruk/index.shtml" target="_blank">违法和不良信息举报入口</a> 15504500591<br><br><a href="//www.12377.cn/" target="_blank"><img src="https://www.dbw.cn/images/2018/di-logo01.jpg" width="232" height="36" <="" a="">&nbsp;&nbsp;&nbsp;</a><a href="//www.12377.cn/node_548446.htm" target="_blank"><img src="https://www.dbw.cn/images/2018/di-logo02.jpg" width="140" height="36" <="" a="">&nbsp;&nbsp;&nbsp;</a><a href="//www.12377.cn/" target="_blank"><img src="https://www.dbw.cn/images/2018/di-logo03.jpg" width="122" height="36" <="" a="">&nbsp;&nbsp;&nbsp;<br><br></a><a href="//bszs.conac.cn/sitename?method=show&amp;id=2CF9D3DA3FD33341E053012819ACA842" target="_blank"><img src="https://www.dbw.cn/images/2018/di-logo04.jpg" width="54" height="65" <="" a=""></a></div><a href="//bszs.conac.cn/sitename?method=show&amp;id=2CF9D3DA3FD33341E053012819ACA842" target="_blank">
<!--版权end-->     
 <script type="text/javascript">
	$('.left-category ul li').hover(function(){
		var index = $(this).index();
		$(this).addClass('on').siblings().removeClass('on');
		$('.pro-right').removeClass('active').eq(index).addClass('active');
	})
</script>
    <script type="text/javascript">
function touchSlide (obj) {
      obj.mouseover(function () {
        $(this).addClass('active').siblings().removeClass("active");
        $(this).parent().parent().next().children().eq($(this).index()).show().siblings().hide();
      })
    }
	 touchSlide ($('#biaoqian-over1 ul li'));
     touchSlide ($('#biaoqian-over2 ul li'));
</script>





</a></body></html>
    """
    
    print_analysis(sample_html)
    
    # _, p = contains_video_player(sample_html)
    
