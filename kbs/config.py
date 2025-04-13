import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class DBType(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"

@dataclass
class DBConfig:
    type: DBType
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: str = "kbs"
    
    @property
    def connection_string(self) -> str:
        if self.type == DBType.SQLITE:
            return f"sqlite:///{self.database}"
        elif self.type == DBType.POSTGRESQL:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DBType.MYSQL:
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        raise ValueError(f"Unsupported database type: {self.type}")

@dataclass
class FileStorageConfig:
    # 文件存储根路径
    root_path: str = str(Path.home() / ".kbs" / "files")
    # 单个文件大小限制（字节）
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    # 支持的文件类型
    allowed_extensions: set = None
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = {'pdf', 'txt', 'doc', 'docx'}
        # 确保存储目录存在
        os.makedirs(self.root_path, exist_ok=True)

class Config:
    def __init__(self):
        self.db = self._load_db_config()
        self.storage = self._load_storage_config()
    
    def _load_db_config(self) -> DBConfig:
        """从环境变量加载数据库配置"""
        db_type = os.getenv("KBS_DB_TYPE", "sqlite").lower()
        
        if db_type == "sqlite":
            return DBConfig(
                type=DBType.SQLITE,
                database=os.getenv("KBS_DB_PATH", "kbs.db")
            )
        
        return DBConfig(
            type=DBType[db_type.upper()],
            host=os.getenv("KBS_DB_HOST", "localhost"),
            port=int(os.getenv("KBS_DB_PORT", "5432" if db_type == "postgresql" else "3306")),
            username=os.getenv("KBS_DB_USER"),
            password=os.getenv("KBS_DB_PASSWORD"),
            database=os.getenv("KBS_DB_NAME", "kbs")
        )
    
    def _load_storage_config(self) -> FileStorageConfig:
        """从环境变量加载文件存储配置"""
        return FileStorageConfig(
            root_path=os.getenv("KBS_STORAGE_PATH", str(Path.home() / ".kbs" / "files")),
            max_file_size=int(os.getenv("KBS_MAX_FILE_SIZE", str(100 * 1024 * 1024))),
            allowed_extensions=set(os.getenv("KBS_ALLOWED_EXTENSIONS", "pdf,txt,doc,docx").split(","))
        )

# 全局配置实例
config = Config() 