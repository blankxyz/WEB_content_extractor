# server.py
import asyncio
import uuid
from datetime import datetime
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

# 导入生成的代码
from data_processing import DataProcessingService
from data_processing.ttypes import ProcessResult, ProcessStatus, ProcessRequest

# 复用之前的异步处理管道
from async_pipeline import AsyncDataPipeline

class DataProcessingHandler:
    def __init__(self):
        self.pipeline = None
        self.processing_tasks = {}
        self.loop = asyncio.get_event_loop()
        
    async def init_pipeline(self):
        """初始化异步处理管道"""
        if self.pipeline is None:
            self.pipeline = AsyncDataPipeline()
            await self.pipeline.__aenter__()
    
    def create_process_result(self, id, status, content="", metadata=None):
        """创建处理结果对象"""
        return ProcessResult(
            id=id,
            status=status,
            content=content,
            metadata=metadata or {},
            timestamp=int(datetime.now().timestamp())
        )

    async def process_single_url(self, request):
        """处理单个URL的异步方法"""
        await self.init_pipeline()
        try:
            result = await self.pipeline.process_url(request.url)
            return self.create_process_result(
                id=str(uuid.uuid4()),
                status=ProcessStatus.SUCCESS,
                content=str(result),
                metadata={"url": request.url}
            )
        except Exception as e:
            return self.create_process_result(
                id=str(uuid.uuid4()),
                status=ProcessStatus.FAILED,
                content=str(e),
                metadata={"url": request.url, "error": str(e)}
            )

    def submitUrl(self, request):
        """提交单个URL处理请求"""
        task = asyncio.run_coroutine_threadsafe(
            self.process_single_url(request),
            self.loop
        )
        result = task.result()
        self.processing_tasks[result.id] = task
        return result

    def submitBatchUrls(self, requests):
        """批量提交URL处理请求"""
        async def process_batch():
            await self.init_pipeline()
            tasks = [self.process_single_url(req) for req in requests]
            return await asyncio.gather(*tasks)

        task = asyncio.run_coroutine_threadsafe(process_batch(), self.loop)
        results = task.result()
        for result in results:
            self.processing_tasks[result.id] = task
        return results

    def getStatus(self, id):
        """获取处理状态"""
        if id not in self.processing_tasks:
            return self.create_process_result(
                id=id,
                status=ProcessStatus.FAILED,
                content="Task not found"
            )
        
        task = self.processing_tasks[id]
        if task.done():
            try:
                result = task.result()
                return result
            except Exception as e:
                return self.create_process_result(
                    id=id,
                    status=ProcessStatus.FAILED,
                    content=str(e)
                )
        else:
            return self.create_process_result(
                id=id,
                status=ProcessStatus.PROCESSING
            )

    def cancelProcessing(self, id):
        """取消处理任务"""
        if id in self.processing_tasks:
            task = self.processing_tasks[id]
            if not task.done():
                task.cancel()
            del self.processing_tasks[id]
            return True
        return False

def run_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    handler = DataProcessingHandler()
    processor = DataProcessingService.Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadedServer(
        processor, transport, tfactory, pfactory
    )

    print('Starting the server...')
    try:
        server.serve()
    except KeyboardInterrupt:
        print('Stopping the server...')
        loop.run_until_complete(handler.pipeline.__aexit__(None, None, None))
        loop.close()

if __name__ == '__main__':
    run_server()
