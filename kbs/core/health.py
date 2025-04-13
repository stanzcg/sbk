import time
import logging
from typing import Dict, Any, List
from threading import Thread
import psutil
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pymilvus import connections

logger = logging.getLogger(__name__)

class HealthCheck:
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.services: Dict[str, Dict[str, Any]] = {}
        self.running = True
        self._start_monitor_thread()

    def _start_monitor_thread(self):
        def monitor():
            while self.running:
                self._check_all_services()
                time.sleep(self.check_interval)

        self.monitor_thread = Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

    def _check_all_services(self):
        """检查所有服务的健康状态"""
        # 检查数据库连接
        self._check_database()
        
        # 检查Milvus连接
        self._check_milvus()
        
        # 检查系统资源
        self._check_system_resources()

    def _check_database(self):
        """检查数据库连接状态"""
        try:
            from core.database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            self.services["database"] = {
                "status": "healthy",
                "last_check": time.time(),
                "error": None
            }
        except SQLAlchemyError as e:
            self.services["database"] = {
                "status": "unhealthy",
                "last_check": time.time(),
                "error": str(e)
            }
            logger.error(f"Database health check failed: {e}")

    def _check_milvus(self):
        """检查Milvus连接状态"""
        try:
            if not connections.has_connection("default"):
                connections.connect("default")
            # 执行简单查询验证连接
            from pymilvus import utility
            collections = utility.list_collections()
            self.services["milvus"] = {
                "status": "healthy",
                "last_check": time.time(),
                "error": None
            }
        except Exception as e:
            self.services["milvus"] = {
                "status": "unhealthy",
                "last_check": time.time(),
                "error": str(e)
            }
            logger.error(f"Milvus health check failed: {e}")

    def _check_system_resources(self):
        """检查系统资源使用情况"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            self.services["system"] = {
                "status": "healthy" if cpu_percent < 90 and memory.percent < 90 and disk.percent < 90 else "warning",
                "last_check": time.time(),
                "metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent
                },
                "error": None
            }
        except Exception as e:
            self.services["system"] = {
                "status": "unhealthy",
                "last_check": time.time(),
                "error": str(e)
            }
            logger.error(f"System resources check failed: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """获取所有服务的健康状态"""
        overall_status = "healthy"
        for service in self.services.values():
            if service["status"] == "unhealthy":
                overall_status = "unhealthy"
                break
            elif service["status"] == "warning" and overall_status == "healthy":
                overall_status = "warning"

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "services": self.services
        }

    def shutdown(self):
        """关闭健康检查系统"""
        self.running = False
        self.monitor_thread.join()

# 全局健康检查实例
health_checker = HealthCheck() 