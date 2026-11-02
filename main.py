import asyncio
import uvicorn
import config
from services.gateway_service import app as gateway_app
from services.analysis_service import app as analysis_app
from services.history_service import app as history_app
from services.catalog_service import app as catalog_app
from services.stats_service import app as stats_app

app = gateway_app

async def serve_all():
    c_hist = uvicorn.Config(history_app, host="127.0.0.1", port=config.HISTORY_SERVICE_PORT, log_level="info")
    s_hist = uvicorn.Server(c_hist)

    c_cat = uvicorn.Config(catalog_app, host="127.0.0.1", port=config.CATALOG_SERVICE_PORT, log_level="info")
    s_cat = uvicorn.Server(c_cat)

    c_stats = uvicorn.Config(stats_app, host="127.0.0.1", port=config.STATS_SERVICE_PORT, log_level="info")
    s_stats = uvicorn.Server(c_stats)

    c_anal = uvicorn.Config(analysis_app, host="127.0.0.1", port=config.ANALYSIS_SERVICE_PORT, log_level="info")
    s_anal = uvicorn.Server(c_anal)

    c_gate = uvicorn.Config(gateway_app, host=config.GATEWAY_HOST, port=config.GATEWAY_PORT, log_level="info")
    s_gate = uvicorn.Server(c_gate)

    await asyncio.gather(
        s_hist.serve(),
        s_cat.serve(),
        s_stats.serve(),
        s_anal.serve(),
        s_gate.serve()
    )

if __name__ == "__main__":
    asyncio.run(serve_all())
