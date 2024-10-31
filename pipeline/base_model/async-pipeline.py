
 from typing import NamedTuple
 
# ----------------- 数据结构定义 -------------------

## ----------------- Input -------------------
class Page(NamedTuple):
    url: str
    content: str

class PipleRule(NamedTuple):
    URL: str
    Rules: dict
    Request: str


## ----------------- Output -------------------
# json格式

# ----------------- 数据处理函数定义 -------------------
# 1. 根据给定的page，寻找匹配的规则
def find_match_rule(page: Page) -> PipleRule:
    
    
    return None


def chat_with_gpt(page: Page, rule: PipleRule) -> str:
    
    
    return ""