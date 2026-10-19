from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.errors.exception_handlers import register_exception_handlers
from api.routes.dataset_routes import router as dataset_router
from api.routes.health_routes import router as health_router
from api.routes.optimization_routes import router as optimization_router
from api.routes.status_routes import router as status_router
from api.websockets.progress_socket import router as websocket_router
from core.config import get_settings


def create_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Gestao Preditiva de Estoque com IA",
        version="0.1.0",
        description="API de previsao de demanda e otimizacao sob restricao orcamentaria",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(dataset_router)
    app.include_router(optimization_router)
    app.include_router(status_router)
    app.include_router(websocket_router)
    return app


app = create_application()
