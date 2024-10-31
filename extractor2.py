from bs4 import BeautifulSoup, Comment
import re

def is_likely_header_or_footer(element):
    """
    判断一个元素是否可能是header或footer
    """
    # 检查标签名和class/id
    if element.name in ['header', 'footer', 'nav']:
        return True
    
    suspicious_terms = [
        'header', 'footer', 'navigation', 'nav', 'menu', 'banner', 
        'copyright', 'logo', 'social', 'sidebar', 'widget', 'breadcrumb',
        'pagination', 'comment', 'advertisement', 'ad-', '-ad', 'share'
    ]
    
    # 检查class和id中的关键词
    element_classes = ' '.join(element.get('class', [])).lower() if element.get('class') else ''
    element_id = element.get('id', '').lower()
    
    return any(term in element_classes or term in element_id for term in suspicious_terms)

def is_likely_noise(element):
    """
    检查是否是干扰元素
    """
    noise_tags = {
        'script', 'style', 'iframe', 'noscript', 'option', 'button',
        'form', 'input', 'textarea', 'select', 'svg', 'canvas'
    }
    return element.name in noise_tags

def is_content_tag(tag):
    """
    检查是否是可能包含内容的标签
    """
    content_tags = {
        # 文本容器
        'p', 'div', 'span', 'article', 'section', 'main',
        # 标题
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        # 列表
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        # 表格
        'table', 'tr', 'td', 'th',
        # 其他文本元素
        'blockquote', 'pre', 'code', 'em', 'strong', 'small',
        'figure', 'figcaption', 'caption',
        # 文本格式化
        'b', 'i', 'u', 'mark', 'cite', 'q',
        # 自定义文本容器
        'text', 'content', 'paragraph'
    }
    return tag.name in content_tags

def has_meaningful_text(element, min_length=10):
    """
    检查元素是否包含有意义的文本
    排除纯空格、纯符号等无意义内容
    """
    text = element.get_text(strip=True)
    if not text or len(text) < min_length:
        return False
        
    # 检查是否全是特殊字符
    special_chars = set(',.!?;:()[]{}|/\\<>+=_-*&^%$#@~`"\'')
    text_chars = set(text)
    if all(char in special_chars for char in text_chars):
        return False
        
    # 检查是否是常见的噪音文本
    noise_patterns = [
        r'^[0-9\W]+$',  # 纯数字或特殊字符
        r'^(powered by|copyright|\(c\)|©|all rights reserved)',  # 版权信息
        r'^(share|like|follow|subscribe|sign up|login|register)',  # 行动号召
        r'^(previous|next|page|[0-9]+ of [0-9]+)',  # 导航元素
    ]
    
    return not any(re.match(pattern, text.lower()) for pattern in noise_patterns)

def get_text_density(element):
    """
    计算元素的文本密度
    文本密度 = 文本长度 / 标签数量
    """
    text_length = len(element.get_text(strip=True))
    tags_count = len(element.find_all())
    if tags_count == 0:
        return text_length
    return text_length / (tags_count + 1)

def extract_main_content(html):
    """
    提取HTML中的主要文本内容
    """
    if not html:
        return ""
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 移除注释和无用标签
    for element in soup.find_all(string=lambda text: isinstance(text, Comment)):
        element.extract()
    
    for element in soup.find_all(is_likely_noise):
        element.decompose()
    
    # 移除header和footer
    for element in soup.find_all(is_likely_header_or_footer):
        element.decompose()
    
    def extract_text_from_element(element, depth=0, max_depth=10):
        """
        递归提取元素中的文本内容
        """
        if depth > max_depth:
            return []
            
        texts = []
        
        # 如果元素本身包含有意义的文本，直接添加
        if has_meaningful_text(element):
            text = element.get_text(strip=True)
            if text:
                texts.append(text)
        
        # 递归处理子元素
        # for child in element.children:
        #     if hasattr(child, 'name'):  # 确保是标签元素
        #         if is_content_tag(child) and not is_likely_header_or_footer(child):
        #             child_texts = extract_text_from_element(child, depth + 1)
        #             texts.extend(child_texts)
        
        return texts
    
    # 找到可能的主要内容容器
    potential_containers = []
    # for element in soup.find_all(['article', 'main', 'div', 'section']):
    #     if not is_likely_header_or_footer(element):
    #         text_density = get_text_density(element)
    #         content_length = len(element.get_text(strip=True))
    #         if content_length > 100 and text_density > 5:  # 调整这些阈值
    #             potential_containers.append((element, text_density * content_length))
    
    # 如果找到了主要容器，使用文本密度最高的
    # if potential_containers:
    #     main_container = max(potential_containers, key=lambda x: x[1])[0]
    #     texts = extract_text_from_element(main_container)
    # else:
    #     # 如果没找到明显的主容器，处理整个body
    #     body = soup.find('body')
    #     if body:
    #         texts = extract_text_from_element(body)
    #     else:
    #         texts = extract_text_from_element(soup)
    body = soup.find('body')
    if body:
        texts = extract_text_from_element(body)
    # 后处理
    processed_texts = []
    seen_texts = set()
    
    for text in texts:
        # 规范化空白字符
        text = ' '.join(text.split())
        
        # 去重
        if text and text not in seen_texts:
            processed_texts.append(text)
            seen_texts.add(text)
    
    return '\n\n'.join(processed_texts)

def clean_extracted_text(text):
    """
    清理和格式化提取的文本
    """
    # 删除重复的换行
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 删除前后空白
    text = text.strip()
    
    # 合并连续的空格
    text = re.sub(r' +', ' ', text)
    
    # 修正中文和英文之间的空格
    text = re.sub(r'([a-zA-Z]) *([，。！？；：""''【】（）])', r'\1\2', text)
    text = re.sub(r'([，。！？；：""''【】（）]) *([a-zA-Z])', r'\1 \2', text)
    
    return text

def extract_text_from_html(html):
    """
    主函数：从HTML中提取清理后的主要文本内容
    """
    main_content = extract_main_content(html)
    cleaned_text = clean_extracted_text(main_content)
    return cleaned_text


html_content = """
<html xmlns="//www.w3.org/1999/xhtml"><head>

<meta http-equiv="Content-Type" content="text/html; charset=gb2312">
<meta name="filetype" content="0">   
<meta name="publishedtype" content="1">   
<meta name="pagetype" content="2"> 
<meta name="catalogs" content="80005001000000000"> 
<base target="_blank">
<title>身在最北方 心向党中央丨吕金刚：让装备制造业“皇冠上的明珠”更闪亮-龙江看天下-东北网</title>
<meta name="keywords" content="">
<meta name="description" content="　　黑龙江日报10月25日讯 高温、高压、高转速下可靠、持久的运转，造就了航空发动机和燃气轮机极高的技术壁垒，被誉为装备制造业“皇冠上的明珠”。

　　当今世界，仅有包括中国在内的少数几个国家具备独立自主研制“两机”的能力，这代表着一国装备制造业的最高技术水平。

　　18年前，吕金刚入职哈尔滨城林科技股份...">
<meta name="Keywords" content="东北网,黑龙江新闻,黑龙江政府网,东北论坛,报料,电子报,手机报,视频,网视,微电影,健康,教育,餐饮,龙版,俄语">
<meta name="Description" content="东北网是黑龙江影响力最强、访问量最大的综合性网站，是拥有新闻发布、资讯服务、视频播报、多语种传播、无线增值业务服务等多功能的新媒体平台，开设黑龙江新闻、视频、健康等40多个内容频道及论坛、博客、微博、微信等互动交流，提供最全面的黑龙江信息。">
<meta name="msapplication-TileImage" content="//www.dbw.cn/images/logo.png">
<meta name="robots" content="index, follow">
<meta name="googlebot" content="index, follow">

<link href="/css/dbw-lmy.css" rel="stylesheet" type="text/css">
<script src="https://hm.baidu.com/hm.js?4df615e964dda939a9b3c7ac424d315f"></script><script src="//heilongjiang.dbw.cn/js/jquery3.5.1.js"></script><input type="hidden" id="_o_dbjbempljhcmhlfpfacalomonjpalpko" data-inspect-config="3"><script type="text/javascript" src="chrome-extension://dbjbempljhcmhlfpfacalomonjpalpko/scripts/inspector.js"></script>
<script type="text/javascript" src="//www.dbw.cn/js/tiaozhuan2.js"></script>
</head>

<body>
<div style="width:1400px; margin:0 auto;"></div>

<div class="top-box">
<div class="logo fl"><a href="//www.dbw.cn"><img src="https://www.dbw.cn/images/2018/logo-new.gif" width="293" height="68"></a></div>
<a href="//ljktx.dbw.cn/index.shtml" target="_blank"><img src="/images/ljktx-logo.jpg" width="206" height="85"></a>

</div><!--logoend-->


<div class="nav-k">
<div class="nav-nr">
<ul>
<li><a href="/szyw/" target="_blank">时政要闻</a></li>
<li><a href="/ljtime/zwuzce/" target="_blank">政务•政策</a></li>
<li><a href="/ljtime/wzhenglj/" target="_blank">问政•亮剑</a></li>
<li><a href="/ljtime/benwyc/" target="_blank">本网原创</a></li>
<li><a href="/ljtime/benwdt/" target="_blank">本网动态</a></li>
<li><a href="/ljtime/ljdis/" target="_blank">龙江地市</a></li>
<li style="border-right:none;"><a href="/lgdrmjz/" target="_blank">龙广电融媒矩阵</a></li>
</ul>
</div>

</div>
<!--enorth cms page [ enorth parse_date="2024/06/04 11:22:56.056", cost="6", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->
<!--导航end-->



<div class="top-box">

<div class="weizhi">
<!--enorth cms block start [ name="v5.position" ]-->
您当前的位置 ：
<a href="//www.dbw.cn/index.shtml">东北网</a>
&nbsp;&gt;&nbsp;
<a href="//ljktx.dbw.cn/index.shtml">龙江看天下</a>
&nbsp;&gt;&nbsp;
<a href="//ljktx.dbw.cn/ljtime/index.shtml">龙江时间</a>
&nbsp;&gt;&nbsp;
<a href="//ljktx.dbw.cn/ljtime/kanlj/index.shtml">看龙江</a>
<!--enorth cms block end [ name="v5.position" cost="26"]--></div>
<div class="end-k"><h1>身在最北方 心向党中央丨吕金刚：让装备制造业“皇冠上的明珠”更闪亮</h1>

<div class="time hui">时间：2024-10-25 08:03:30　 来源：黑龙江日报　 作者：</div>
 
 <div class="neirong">
 <p>　　<strong>黑龙江日报10月25日讯 </strong>高温、高压、高转速下可靠、持久的运转，造就了航空发动机和燃气轮机极高的技术壁垒，被誉为装备制造业“皇冠上的明珠”。</p>

<p>　　当今世界，仅有包括中国在内的少数几个国家具备独立自主研制“两机”的能力，这代表着一国装备制造业的最高技术水平。</p>

<p>　　18年前，吕金刚入职哈尔滨城林科技股份有限公司，那时我国的“两机”研制正处于起步阶段。他由此一头扎进“两机”配套设备的设计、研制工作中，怀揣着激情、热爱和浓浓的科技报国情，以精细严谨、勇攀高峰的创新精神，逐渐成长为正高级工程师、行业专家、公司总经理，并带领企业成为我国中小型燃气轮机配套设备和航空发动机试车台空气动力系统配套设备技术实力最强的企业，成为我国“两机”发展中的重要一环。</p>

<p><strong>　　因热爱而钻研 因钻研而成长</strong></p>

<p>　　1982年出生的吕金刚是山东省威海市人，2002年考入黑龙江八一农垦大学工程学院农业机械化及其自动化专业，由此开启了他扎根最北方的人生旅程。</p>

<p>　　2006年7月，吕金刚入职城林科技做设计工程师。喜欢设计、喜欢钻研的吕金刚说，他很幸运从事了自己喜欢的职业，更幸运的是他赶上了我国推进“两机”发展的时代。</p>

<p>　　在这样的时代背景下，入职不久后，吕金刚参与了国家863计划重型燃气轮机发电机组配套辅机系统的研制。这是我国首台重型燃气轮机发电机组，一切从零开始，而且对配套辅机系统的要求是不但要满足气动、噪声和燃机运行的所有需求，还要求可拆卸、反复组装。</p>

<p>　　“这个要求是非常高的，当时大部分机组都是一次成型，后续搬迁时辅助机系统就不能用了，特别是高温高压的部件，涉及到耐温、膨胀、风载相结合等复杂要求。”吕金刚回忆说，那时印象最深刻的就是加班加点、反复试验，令他最兴奋的事情就是参加评审会。</p>

<p>　　在吕金刚看来，参加评审会是提高技术水平的最好机会。有公司的前辈、有行业专家，尤其是作为国家863项目，参加评审会的还会有我国“两机”顶级专家。在评审会中，他如饥似渴地吮吸着知识的甘霖，快速成长为行业精英。</p>

<p>　　从参与863计划项目起，吕金刚就像上了弦的发条，在“两机”世界里探索、攻坚，取得一个个零的突破，解决掉一个个“卡脖子”问题，为我国的“两机”发展贡献青春和智慧。</p>

<p>　　<strong>始终参与技术工作 逐浪行业最前沿</strong></p>

<p>　　参与国内第一套应用在海上平台自主燃气轮机发电机组的辅机系统、国内第一套应用在西气东输的自主燃气轮机驱动压缩机辅机系统、国内第一套应用在自主燃气轮机出口项目的辅机系统、国产第一台25MW级移动电源车、国产第一台燃气轮机压裂车、国产第一台110MW级重型燃气轮机发电机组辅机系统的研制，以及近20年内大部分国家航空发动机重点型号研制的条件建设……说起自己的工作成就，吕金刚最骄傲的是参与“两机”各重点型号的研制，创造了很多的“第一”，在这些“大国重器”的诞生中洒下自己的心血和汗水。</p>

<p>　　2007年末，入职不到两年的吕金刚作为主设计师带着入职刚一年的同事，承担起了燃气轮机自洁式空气过滤系统的自主设计工作。</p>

<p>　　当时国内使用的这一产品主要是国外品牌，自主设计上没有成型的经验可借鉴。于是大量的查资料、计算，反复试验，到国外产品现场进行实地测量和性能分析，搜集用户设计意见，多次开评审会不断修正。</p>

<p>　　经过一年多的艰辛攻坚，吕金刚带领同事终于完成了我国首台燃机用卧式自清洁过滤系统，取得自主知识产权，并成功应用在中海油东方石油平台上。</p>

<p>　　“如果说发动机是一套燃气轮机机组‘五脏六腑’中的‘心脏’，那么箱体、过滤系统、通风系统、进气系统、排气系统、消音系统等则是机组的其它脏器，而这些均是由城林科技研制。”吕金刚对此深感自豪。</p>

<p>　　先后担任设计员、项目经理、项目部长、市场开发部经理、营销总监、东北大区经理、大客户事业部总经理、哈尔滨公司总经理等职，但无论在哪一个岗位上，吕金刚始终参与技术工作，目前还是公司的总设计师。他还参加了国家及行业标准的制定，是国家标准GB50454-2020《航空发动机试车台设计标准》的主要起草人员之一，国家电力行业标准DLT 5829-2021《户内配电变压器振动与噪声控制工程技术规范》的主要起草人员之一。</p>

<p>　　<strong>懂技术 善经营 会管理</strong></p>

<p>　　“以市场为导向，以客户为中心”“敢于创新，挑战不可能和旧习惯”……这些标注在城林科技企业文化墙上的文字，凝结着吕金刚多年的技术钻研积累、市场打拼经验和管理岗位砺炼。</p>

<p>　　“2020年哈尔滨公司的产值是八九千万元，今年预计将突破5亿元，可以说吕总带领公司实现了跨越式增长。”城林科技营销总监孔繁宇告诉记者，2020年吕金刚接任总经理时提出的发展目标，到目前都一一实现，当时大家都认为他的想法太超前、不现实。</p>

<p>　　担任总经理后，吕金刚开始了大刀阔斧的改革。调整管理层人员、增加就业岗位、改变薪酬制度，2022年，他力主投资5000万元建设了三期厂房，使企业产能大幅提升，为公司后续发展争先机、拓空间、蓄能量。</p>

<p>　　“这几年公司引进了很多研发人才，补充了电气、液压等专业性人才，为公司的持续创新提供智力支撑。”城林科技副总经理牛东风介绍，吕金刚主张从企业产品行业特色经营理念入手，扎根钻研企业的专长建设，带领企业打造成为国家级专精特新重点“小巨人”,并加强了绿色化数字化车间建设，获评国家级绿色工厂企业；同时严抓企业产品质量，带领企业先后获得黑龙江省制造业单项冠军、技术创新示范企业、企业技术中心、质量标杆、数字化示范标杆等称号，完成了6个黑龙江省认定的首台套产品。</p>

<p>　　目前，城林科技中小型燃气轮机辅机系统和航空发动机试车台空气动力系统的全国市场占有率都达60%以上，在行业内是名副其实的NO.1。</p>

<p>　<strong>　记者手记</strong></p>

<p>　　从一名普通的设计工程师到正高级工程师，吕金刚用了18年。</p>

<p>　　采访中，记者深刻地感受到，一系列成绩的背后，是吕金刚那专注、严谨的科学精神。</p>

<p>　　80后的吕金刚，对钻研技术的热爱已经刻在了骨子里。大学刚毕业时，回到宿舍就是打游戏，他感到很空虚，于是下班后他不再先回宿舍，而是留在单位学习、查资料、研究项目案例；担任总经理后，他白天开会、研讨、安排各种事务、与客户沟通，晚上则静下来思考、看材料、研究项目遇到的难题，公司的重大项目他都是参与者，他也是公司掌握核心技术最多的人。</p>

<p>　　城林科技研发负责人邵春望告诉记者，在竞标航空发动机试车台的方案介绍环节，吕金刚会根据不同型号发动机的特性，提出产品的技术参数和性能指标，当客户提出质疑时，吕金刚则会拿出大量的数据和理论支撑，一步一步说服客户，而这些客户都是行业内的专家。吕金刚的自信来源于多年积累的丰富经验，也来源于他持续不断的学习和对每一个参与项目的数据实测和钻研。</p>

<p>　　专注，是一种追求上进的态度，是一份精益专业的执着，是一个不负职守的信念。唯其专注、始得玉成，正是秉持这份专注，吕金刚深度沉浸、快速成长。</p>
 

<!--enorth cms block start [ name="v5.pages" ]-->

<!--enorth cms block end [ name="v5.pages" cost="4"]--></div>
<div class="qhui" style="width:1250px; text-align:right; margin-top:30px;">责任编辑：王聪</div>

</div>


</div><!--整体end-->
<div class="clear"></div><!--下部整体end-->
<div class="footer-di">
  <img src="https://www.dbw.cn/images/2018/logo-di.gif" width="160" height="50"><br>
<span class="lxwm-bnt bai"><a href="//ljktx.dbw.cn/lxwm/index.shtml" target="_blank">联系我们</a></span>
严格遵守保密法律法规，严禁在互联网发布涉密信息。<br>
黑龙江东北网络台版权所有 Copyright◎2001-2017 WWW.DBW.CN　All Rights Reserved.<br>
增值电信业务经营者证件号：黑B2-20080973-1 国新网许可证编号：2312006001　 哈公网监备23010002003717号<br>
广告经营许可证号：2301000000007 广播电视节目制作经营许可证：黑字第083号　 黑龙江仁大律师事务所　孙维涛律师<br><br>
<img src="https://www.dbw.cn/images/2018/di-logo01.jpg" width="232" height="36">　<img src="https://www.dbw.cn/images/2018/di-logo02.jpg" width="140" height="36">　<img src="https://www.dbw.cn/images/2018/di-logo03.jpg" width="122" height="36"><br><br>
<img src="https://www.dbw.cn/images/2018/di-logo04.jpg" width="54" height="65"></div>
<!--enorth cms page [ enorth parse_date="2024/05/29 16:32:18.018", cost="4", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->


<!--版权end-->




<script type="text/javascript" src="https://js.users.51.la/19517621.js"></script>
<!--推送代码 -->
<script>(function(){
var src = (document.location.protocol == "http:") ? "//js.passport.qihucdn.com/11.0.1.js?5fc93c9f676e78dd6d2085ef311c4bae":"https://jspassport.ssl.qhimg.com/11.0.1.js?5fc93c9f676e78dd6d2085ef311c4bae";
document.write('<script src="' + src + '" id="sozz"><\/script>');
})();
</script><script src="https://jspassport.ssl.qhimg.com/11.0.1.js?5fc93c9f676e78dd6d2085ef311c4bae" id="sozz"></script><script charset="utf-8" src="https://s.ssl.qhres2.com/ssl/ab77b6ea7f3fbf79.js"></script>
<script>(function(){
var src = (document.location.protocol == "http:") ? "//js.passport.qihucdn.com/11.0.1.js?5fc93c9f676e78dd6d2085ef311c4bae":"https://jspassport.ssl.qhimg.com/11.0.1.js?5fc93c9f676e78dd6d2085ef311c4bae";
document.write('<script src="' + src + '" id="sozz"><\/script>');
})();
</script><script src="https://jspassport.ssl.qhimg.com/11.0.1.js?5fc93c9f676e78dd6d2085ef311c4bae" id="sozz"></script><script charset="utf-8" src="https://s.ssl.qhres2.com/ssl/ab77b6ea7f3fbf79.js"></script>
<!--推送代码 -->
<!--统计代码 -->
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?4df615e964dda939a9b3c7ac424d315f";
  var s = document.getElementsByTagName("script")[0]; 
  s.parentNode.insertBefore(hm, s);
})();
</script>
<!--统计代码 -->





</body></html>

"""


print(extract_text_from_html(html_content))