import logging
import os
import sys
from typing import Dict, Any

def get_logger(name: str):
    return logging.getLogger(name)

def log_error(exc: Exception, context: Dict[str, Any] = None):
    logger = get_logger("error")
    logger.error(f"Error: {str(exc)}", extra=context or {})

def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

class LoggingContextMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
