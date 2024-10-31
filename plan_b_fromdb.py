import asyncio
import csv
import logging
import json
import aiomysql
from openai import AsyncOpenAI
import trafilatura
from lxml import html

openai_api_key = "EMPTY"
openai_api_base = "http://localhost:11434/v1"

client = AsyncOpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

system_prompt = """
你现在是一位专业的新闻文本分析专家。请分析以下新闻文本，找出该新闻的作者/记者。


[粘贴新闻文本]

请执行以下分析步骤:

1. 查找显式署名信息:
   - 文章开头或结尾的署名行
   - "记者"、"报道"、"采写"、"编辑"后的人名
   如："记者 xx"、"报道 xxx"、"编辑 xxx"等。
   - 不要包含"编导"、"摄像"、"制作"、"调色"等信息。
   - 单个人名应该不要超过5个字。
   

2. 如果以上步骤都无法确定，请返回"无法确定"。

请返回一个JSON对象，包含以下字段:
{
  "author": "AUTHOR_NAME",
}

不要返回其它内容。

新闻文本:
"""

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
            text = element.get_text(strip=False)
                # 删除重复的换行
            text = re.sub(r'\n{3,}', '\n\n', text)
            if text:
                texts.append(text + '')
        return texts
    
    # 找到可能的主要内容容器
    potential_containers = []

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


async def call_llm(input_msg):
    try:
        chat_response = await client.chat.completions.create(
            model="Qwen2-1B",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_msg},
            ],
            temperature=0.7,
            top_p=0.8,
            # max_tokens=512,
            extra_body={
                "repetition_penalty": 1.05,
            },
        )
        content = chat_response.choices[0].message.content
        print("Chat response:", content)
        # return content
        return json.loads(content.replace('```json', '').replace('```', ''))
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON response: {content}")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def process_data(data):
    try:
        input_msg = extract_text_from_html(data['result_text'])
        result = ""
        # result = await call_llm(input_msg)
        
        # page_date = find_date(data['result_text'], outputformat='%Y-%m-%d %H:%M:%S')
        # author_data = json.loads(result.replace('```json', '').replace('```', ''))

        
        page_text = trafilatura.extract(data['result_text'], output_format="json", with_metadata=True)
        if page_text is not None:
            page_data = json.loads(page_text)
        else:
            page_data = {'raw_text': '', 'date': '', 'title': ''}
        
        # 解析 HTML 内容
        tree = html.fromstring(data['result_text'])
        # 提取标题
        title = tree.find('.//title').text
        
        if page_data['title'] is not None:
            if len(title) < len(page_data['title']):
                title = page_data['title']
        
        return {
            "id": data['id'],
            "author": result,
            "content":page_data['raw_text'],
            "date": page_data['date'],
            "title": title
        }

    except Exception as e:
        logging.error(f"Error processing data: {e}")
        


async def process_batch(batch):
    return await asyncio.gather(*[process_data(data) for data in batch])

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
            logging.error(f"Batch processing error: {batch_result}")
        else:
            finally_rs.extend(batch_result)


        # 将列表保存为 JSON 文件
    with open('data.json', 'w', encoding='utf8') as f:
        json.dump(finally_rs, f, ensure_ascii=False)


    # csv_file_path = './data.csv'
    # try:
    #     with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    #         fieldnames = ['id', 'author', 'title', 'content', 'date']
    #         # fieldnames = ['id', 'author', 'content']
    #         # "id": data['id'],
    #         # # "raw_data": input_msg,
    #         # "author": result,
    #         # "title":json_data['title'],
    #         # "content":json_data['raw_text'],
    #         # "date": json_data['date']
    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
    #         writer.writeheader()
    #         for item in finally_rs:
    #             writer.writerow(item)
            
    #         logging.info(f"Processed {len(finally_rs)} items. Results saved to {csv_file_path}")
    # except Exception as e:
    #     logging.error(f"Error saving results to CSV: {e}")

if __name__ == '__main__':
    concurrency = 4  # 调整此值以更改并发级别
    asyncio.run(main(concurrency))