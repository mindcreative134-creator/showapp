import asyncio
import uvicorn

# Pre-initialize event loop to prevent Pyrogram import-time RuntimeError under Python 3.12+
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from main import app
from bot import bot
from config import Config
import logging

logger = logging.getLogger("showapp.launcher")

async def run_fastapi_server():
    """Runs the FastAPI server using Uvicorn"""
    config = uvicorn.Config(
        app=app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    # Start Pyrogram Telegram Client in the background
    logger.info("Initializing Pyrogram bot listener loop...")
    await bot.start()
    logger.info("Pyrogram listener bot is active and listening to updates.")
    
    # Run Uvicorn server in concurrently
    logger.info(f"Starting FastAPI server on {Config.HOST}:{Config.PORT}...")
    try:
        await run_fastapi_server()
    finally:
        # Gracefully disconnect bot connection on exit
        logger.info("Stopping Pyrogram bot connection...")
        await bot.stop()

if __name__ == "__main__":
    # Launch orchestrator
    asyncio.run(main())
