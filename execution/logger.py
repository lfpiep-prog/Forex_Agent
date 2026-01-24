import logging
import json
import os
import sys
import csv
import uuid
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional

# Constants
LOG_DIR = ".tmp/runs"
TRADE_JOURNAL_FILE = "trade_journal.csv"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

# Global run_id for the current process execution
RUN_ID = str(uuid.uuid4())

def get_run_id() -> str:
    """Returns the unique run_id for the current execution."""
    return RUN_ID

class JsonFormatter(logging.Formatter):
    """
    Formatter to output logs in JSON format.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "run_id": RUN_ID
        }
        
        # Add extra fields if they exist
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
        
        # Add stack trace if exception info is present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logger(name: str = "forex_bot", log_dir: str = LOG_DIR) -> logging.Logger:
    """
    Sets up a logger that writes JSON logs to a file and plain text to console.
    Creates a new log file per day/run as needed.
    """
    # Ensure log directory exists
    date_str = datetime.now().strftime('%Y-%m-%d')
    full_log_dir = os.path.join(log_dir, date_str)
    os.makedirs(full_log_dir, exist_ok=True)
    
    log_file = os.path.join(full_log_dir, "log.jsonl")
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Check if handlers already exist to avoid duplicates
    if logger.hasHandlers():
        return logger

    # File Handler - JSON Lines
    file_handler = RotatingFileHandler(log_file, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
    file_handler.setFormatter(JsonFormatter())
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    # Console Handler - Human Readable
    console_handler = logging.StreamHandler(sys.stdout)
    class ConsoleFormatter(logging.Formatter):
        def format(self, record):
            # Shorten run_id for console readability (first 8 chars)
            short_run_id = RUN_ID[:8]
            return f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - [{short_run_id}] - {record.levelname} - {record.getMessage()}"

    console_handler.setFormatter(ConsoleFormatter())
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    return logger

def log_failure(logger: logging.Logger, message: str, error: Exception, next_steps: str = "Check logs for details"):
    """
    Standardized way to log errors with failure summary and next steps.
    """
    logger.error(message, exc_info=True, extra={"extra_data": {
        "failure_summary": str(error),
        "next_steps": next_steps,
        "event_type": "FAILURE"
    }})

class PipelineLogger:
    """
    Context manager to handle pipeline execution state and logging to CSV.
    Ensures that the trade journal is updated exactly once per execution cycle.
    """
    KEYS = ["timestamp", "run_id", "symbol", "price", "signal", "sentiment", "decision", "size", "reason"]

    def __init__(self, filename: str = TRADE_JOURNAL_FILE, logger: Optional[logging.Logger] = None):
        self.filename = filename
        self.logger = logger or logging.getLogger("forex_bot")
        self.start_time = datetime.now()
        self.data: Dict[str, Any] = {
            "timestamp": self.start_time.isoformat(),
            "run_id": RUN_ID,
            "symbol": "",
            "price": 0.0,
            "signal": "NONE",
            "sentiment": "N/A",
            "decision": "SKIPPED",
            "size": 0.0,
            "reason": "Starting..."
        }

    def update(self, **kwargs):
        """Update multiple state variables at once."""
        self.data.update(kwargs)

    def save(self):
        """Writes the current state to the CSV journal."""
        file_exists = os.path.isfile(self.filename)
        
        try:
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.KEYS)
                if not file_exists:
                    writer.writeheader()
                else:
                    # Check if header matches, if not meaningful we might need migration, 
                    # but for now we append. Ideally we'd check headers.
                    # Simplified: If keys changed, new columns might be missing in old file, 
                    # DictWriter handles missing keys by empty string if 'restval' not set, 
                    # but here we just write row.
                    pass
                
                # Ensure we only write known keys
                row = {k: self.data.get(k, "") for k in self.KEYS}
                writer.writerow(row)
        except IOError as e:
            if self.logger:
                self.logger.error(f"Failed to write to trade journal: {e}")
            else:
                print(f"Failed to write to trade journal: {e}")

    def __enter__(self):
        if self.logger:
            self.logger.info("Pipeline Execution Started", extra={"extra_data": {"event_type": "RUN_START"}})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            # If an exception occurred, log it
            self.data["decision"] = "ERROR"
            self.data["reason"] = str(exc_val)
            
            if self.logger:
                 log_failure(self.logger, "Pipeline Execution Failed", exc_val, "Review stack trace and input data")
        else:
            if self.logger:
                self.logger.info("Pipeline Execution Completed", extra={"extra_data": {
                    "event_type": "RUN_END",
                    "duration_seconds": duration,
                    "final_decision": self.data.get("decision")
                }})
        
        self.save()

