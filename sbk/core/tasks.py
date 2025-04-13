from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import logging
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import traceback

logger = logging.getLogger(__name__)

class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    def __init__(self, task_id: str, task_type: str, params: Dict[str, Any]):
        self.task_id = task_id
        self.task_type = task_type
        self.params = params
        self.status = TaskStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

class TaskManager:
    def __init__(self, max_workers: int = 4):
        self.task_queue = Queue()
        self.tasks: Dict[str, Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = True
        self._start_worker_thread()

    def _start_worker_thread(self):
        def worker():
            while self.running:
                try:
                    task = self.task_queue.get()
                    if task is None:
                        break
                    self._process_task(task)
                except Exception as e:
                    logger.error(f"Error processing task: {e}")
                    logger.error(traceback.format_exc())
                finally:
                    self.task_queue.task_done()

        self.worker_thread = Thread(target=worker, daemon=True)
        self.worker_thread.start()

    def _process_task(self, task: Task):
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        try:
            if task.task_type == "process_document":
                from services.document_service import DocumentService
                doc_service = DocumentService()
                result = doc_service.process_document(**task.params)
                task.result = result
                task.status = TaskStatus.COMPLETED
            elif task.task_type == "update_embeddings":
                from services.vector_service import VectorService
                vector_service = VectorService()
                result = vector_service.update_embeddings(**task.params)
                task.result = result
                task.status = TaskStatus.COMPLETED
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Task {task.task_id} failed: {e}")
            logger.error(traceback.format_exc())

        finally:
            task.completed_at = datetime.now()

    def submit_task(self, task_type: str, params: Dict[str, Any]) -> str:
        """提交一个新任务到队列"""
        task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        task = Task(task_id, task_type, params)
        self.tasks[task_id] = task
        self.task_queue.put(task)
        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}

        return {
            "task_id": task.task_id,
            "status": task.status,
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }

    def shutdown(self):
        """关闭任务管理器"""
        self.running = False
        self.task_queue.put(None)  # 发送终止信号
        self.worker_thread.join()
        self.executor.shutdown() 