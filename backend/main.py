"""Main entry point for the Finance AI Analyzer backend"""

import uvicorn
from app.api.rest import app
from app.config import config


def main():
    """Main application entry point - starts the API server"""
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
