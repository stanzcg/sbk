import os
import hashlib
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime
from ..config import config

class FileManager:
    def __init__(self):
        self.storage_path = Path(config.storage.root_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_obj, original_filename: str) -> Tuple[str, str, Path]:
        """
        保存文件并返回文件哈希值和存储路径
        
        Args:
            file_obj: 文件对象
            original_filename: 原始文件名
            
        Returns:
            Tuple[str, str, Path]: (文件哈希值, 原始文件名, 存储路径)
        """
        # 计算文件哈希值
        file_obj.seek(0)
        file_hash = hashlib.sha256(file_obj.read()).hexdigest()
        
        # 构建存储路径：使用日期和哈希值组织目录结构
        today = datetime.now().strftime("%Y/%m/%d")
        relative_path = Path(today) / file_hash[:2] / file_hash[2:4]
        full_path = self.storage_path / relative_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        # 完整的文件路径
        file_path = full_path / f"{file_hash}{Path(original_filename).suffix}"
        
        # 如果文件不存在，则保存
        if not file_path.exists():
            file_obj.seek(0)
            file_path.write_bytes(file_obj.read())
        
        return file_hash, original_filename, file_path.relative_to(self.storage_path)
    
    def get_file_path(self, file_hash: str, original_filename: Optional[str] = None) -> Path:
        """
        根据文件哈希值获取文件路径
        
        Args:
            file_hash: 文件哈希值
            original_filename: 原始文件名（用于获取文件扩展名）
            
        Returns:
            Path: 文件完整路径
        """
        # 搜索可能的文件路径
        for ext in config.storage.allowed_extensions:
            potential_paths = list(self.storage_path.rglob(f"{file_hash}*.{ext}"))
            if potential_paths:
                return potential_paths[0]
        
        raise FileNotFoundError(f"File with hash {file_hash} not found")
    
    def check_file_exists(self, file_hash: str) -> bool:
        """
        检查文件是否已存在
        
        Args:
            file_hash: 文件哈希值
            
        Returns:
            bool: 文件是否存在
        """
        try:
            self.get_file_path(file_hash)
            return True
        except FileNotFoundError:
            return False

# 全局文件管理器实例
file_manager = FileManager() 