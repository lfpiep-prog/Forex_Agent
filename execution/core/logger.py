import logging
import sys
from execution.core.config import settings

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger with the given name.
    """
    logger = logging.getLogger(name)
    
    # If logger already has handlers, assume it's configured
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Create formatter
    # Including timestamp, name, level, and message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Optional: Prevent propagation to root logger to avoid duplicate logs 
    # if root logger is also configured differently, but usually fine to leave default.
    logger.propagate = False
    
    return logger
