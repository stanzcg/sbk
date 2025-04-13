class KBSException(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        super().__init__(self.message)

class DatabaseError(KBSException):
    """数据库相关错误"""
    def __init__(self, message: str, code: str = "DB_ERROR"):
        super().__init__(message, code)

class VectorStoreError(KBSException):
    """向量存储相关错误"""
    def __init__(self, message: str, code: str = "VECTOR_STORE_ERROR"):
        super().__init__(message, code)

class DocumentProcessError(KBSException):
    """文档处理相关错误"""
    def __init__(self, message: str, code: str = "DOC_PROCESS_ERROR"):
        super().__init__(message, code)

class ConfigurationError(KBSException):
    """配置相关错误"""
    def __init__(self, message: str, code: str = "CONFIG_ERROR"):
        super().__init__(message, code)

class AuthenticationError(KBSException):
    """认证相关错误"""
    def __init__(self, message: str, code: str = "AUTH_ERROR"):
        super().__init__(message, code)

class ResourceNotFoundError(KBSException):
    """资源不存在错误"""
    def __init__(self, message: str, code: str = "NOT_FOUND"):
        super().__init__(message, code)

class ValidationError(KBSException):
    """数据验证错误"""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message, code)

class ServiceUnavailableError(KBSException):
    """服务不可用错误"""
    def __init__(self, message: str, code: str = "SERVICE_UNAVAILABLE"):
        super().__init__(message, code) 