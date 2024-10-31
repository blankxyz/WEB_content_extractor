// data_processing.thrift

namespace py data_processing
namespace java com.example.dataprocessing

enum ProcessStatus {
    SUCCESS = 1,
    FAILED = 2,
    PROCESSING = 3,
    VALIDATION_FAILED = 4
}

struct ProcessResult {
    1: string id,
    2: ProcessStatus status,
    3: string content,
    4: map<string, string> metadata,
    5: i64 timestamp
}

struct ProcessRequest {
    1: string url,
    2: map<string, string> parameters
}

service DataProcessingService {
    // 提交URL进行处理
    ProcessResult submitUrl(1: ProcessRequest request),
    
    // 批量提交URL
    list<ProcessResult> submitBatchUrls(1: list<ProcessRequest> requests),
    
    // 获取处理状态
    ProcessResult getStatus(1: string id),
    
    // 取消处理
    bool cancelProcessing(1: string id)
}
