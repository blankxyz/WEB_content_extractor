# client.py
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from data_processing import DataProcessingService
from data_processing.ttypes import ProcessRequest, ProcessStatus

def get_client():
    """创建Thrift客户端"""
    transport = TSocket.TSocket('localhost', 9090)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = DataProcessingService.Client(protocol)
    transport.open()
    return client, transport

def process_single_url(url):
    """处理单个URL示例"""
    client, transport = get_client()
    try:
        request = ProcessRequest(url=url, parameters={})
        result = client.submitUrl(request)
        print(f"Processing started for {url}, task ID: {result.id}")
        
        # 轮询获取状态
        while result.status == ProcessStatus.PROCESSING:
            result = client.getStatus(result.id)
        
        print(f"Processing completed with status: {result.status}")
        print(f"Result: {result.content}")
        
    except Thrift.TException as tx:
        print(f'ERROR: {str(tx)}')
    finally:
        transport.close()

def process_batch_urls(urls):
    """批量处理URL示例"""
    client, transport = get_client()
    try:
        requests = [ProcessRequest(url=url, parameters={}) for url in urls]
        results = client.submitBatchUrls(requests)
        
        for result in results:
            print(f"Batch processing result for task {result.id}: {result.status}")
            
    except Thrift.TException as tx:
        print(f'ERROR: {str(tx)}')
    finally:
        transport.close()

if __name__ == '__main__':
    # 使用示例
    url = "https://example.com"
    process_single_url(url)
    
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]
    process_batch_urls(urls)
