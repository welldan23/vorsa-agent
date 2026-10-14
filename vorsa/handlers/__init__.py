from aiogram import Router

from vorsa.handlers import fallback, filtering, monitor, news, panel, sources


def build_router() -> Router:
    router = Router(name="root")
    router.include_router(panel.router)
    router.include_router(monitor.router)
    router.include_router(sources.router)
    router.include_router(news.router)
    router.include_router(filtering.router)
    router.include_router(fallback.router)  # harus paling akhir
    return router
