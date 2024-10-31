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
        'copyright', 'logo', 'social', 'sidebar', 'widget'
    ]
    
    # 检查class和id中的关键词
    element_classes = ' '.join(element.get('class', [])).lower()
    element_id = element.get('id', '').lower()
    
    for term in suspicious_terms:
        if term in element_classes or term in element_id:
            return True
            
    return False

def has_high_link_density(element):
    """
    检查元素中的链接密度是否过高
    """
    links = element.find_all('a')
    if not links:
        return False
        
    text_length = len(element.get_text(strip=True))
    if text_length == 0:
        return True
        
    link_text_length = sum(len(link.get_text(strip=True)) for link in links)
    link_density = link_text_length / text_length
    
    return link_density > 0.5

def is_boilerplate_content(element):
    """
    检查是否是模板内容
    """
    text = element.get_text(strip=True)
    if not text:
        return True
        
    # 检查是否包含常见的模板内容关键词
    boilerplate_patterns = [
        r'©.*\d{4}',  # 版权信息
        r'all rights reserved',
        r'terms of (use|service)',
        r'privacy policy',
        r'cookie policy',
        r'subscribe to our newsletter',
        r'follow us on',
        r'share this'
    ]
    
    for pattern in boilerplate_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
            
    return False

def calculate_content_score(element):
    """
    计算内容的质量分数
    """
    text = element.get_text(strip=True)
    if not text:
        return 0
        
    # 文本长度得分
    length_score = len(text)
    
    # 段落和标题得分
    p_tags = len(element.find_all('p'))
    h_tags = len(element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    structure_score = (p_tags * 50) + (h_tags * 30)
    
    # 链接密度惩罚
    if has_high_link_density(element):
        return 0
        
    # 计算最终分数
    final_score = length_score + structure_score
    
    return final_score

def extract_main_content(html):
    """
    提取HTML中的主要文本内容
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # 移除script、style等标签
    for tag in soup.find_all(['script', 'style', 'iframe', 'noscript']):
        tag.decompose()
        
    # 移除注释
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
        
    # 移除明显的header和footer
    for element in soup.find_all(is_likely_header_or_footer):
        element.decompose()
        
    # 找到可能的内容容器
    potential_containers = soup.find_all(['article', 'main', 'div', 'section'])
    
    # 计算每个容器的内容分数
    scored_containers = []
    for container in potential_containers:
        if not is_boilerplate_content(container):
            score = calculate_content_score(container)
            scored_containers.append((container, score))
            
    # 按分数排序
    scored_containers.sort(key=lambda x: x[1], reverse=True)
    
    # 如果找到了内容容器，返回分数最高的容器的文本
    if scored_containers:
        main_content = scored_containers[0][0]
        
        # 清理内容
        for element in main_content.find_all(is_likely_header_or_footer):
            element.decompose()
            
        # 提取并清理文本
        text_parts = []
        for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = element.get_text(strip=True)
            if text and not is_boilerplate_content(element):
                text_parts.append(text)
                
        return '\n\n'.join(text_parts)
    
    # 如果没有找到合适的容器，返回body中的所有段落文本
    text_parts = []
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if text and not is_boilerplate_content(p):
            text_parts.append(text)
            
    return '\n\n'.join(text_parts)

def clean_extracted_text(text):
    """
    清理提取的文本
    """
    # 删除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 删除空行
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    # 删除重复的段落
    unique_lines = list(dict.fromkeys(lines))
    text = '\n'.join(unique_lines)
    
    return text.strip()

def extract_text_from_html(html):
    """
    主函数：从HTML中提取清理后的主要文本内容
    """
    print('开始处理HTML内容...')
    main_content = extract_main_content(html)
    cleaned_text = clean_extracted_text(main_content)
    return cleaned_text
