from celery import Celery

from core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "gestao_preditiva_estoque",
    broker=settings.redis_url,
    backend=settings.redis_result_url,
    include=["infrastructure.tasks.optimization_task"],
)

celery_app.conf.update(
    task_default_queue="optimization_queue",
    task_time_limit=300,
    task_soft_time_limit=270,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
