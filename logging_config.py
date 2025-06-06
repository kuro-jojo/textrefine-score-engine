import logging
import logging.config
import os
from datetime import datetime
import shutil
from pathlib import Path
import gzip
import asyncio

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
MAX_LOG_AGE_DAYS = 1  # Keep logs for 30 days
MAX_LOG_SIZE_MB = 100  # Total size limit for all logs (100MB)

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Get the current timestamp
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# Function to clean up old logs
async def cleanup_old_logs():
    """Cleanup old logs based on age and size constraints"""
    try:
        total_size = 0
        logs = []

        # Get all log files and their sizes
        for log_file in Path(LOGS_DIR).glob("*.log*"):
            size = log_file.stat().st_size
            total_size += size
            logs.append((log_file, size))

        # Sort logs by modification time (oldest first)
        logs.sort(key=lambda x: x[0].stat().st_mtime)

        # Remove logs based on age first
        for log_file, _ in logs:
            if (
                datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)
            ).days > MAX_LOG_AGE_DAYS:
                log_file.unlink()

        # If total size exceeds limit, remove oldest logs
        if total_size > MAX_LOG_SIZE_MB * 1024 * 1024:
            for log_file, size in logs:
                if total_size <= MAX_LOG_SIZE_MB * 1024 * 1024:
                    break
                log_file.unlink()
                total_size -= size

    except Exception as e:
        logger = logging.getLogger("score_engine")
        logger.error(f"Error cleaning up logs: {str(e)}", exc_info=True)


# Function to compress old logs
async def compress_old_logs():
    """Compress old log files to save space"""
    try:
        for log_file in Path(LOGS_DIR).glob("*.log*"):
            if (
                datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)
            ).seconds > 60 * 60 * 10:
                # Skip if already compressed
                if log_file.suffix == ".gz":
                    continue

                # Compress the log file
                compressed_file = log_file.with_suffix(".log.gz")
                with open(log_file, "rb") as f_in:
                    with gzip.open(compressed_file, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Remove original file
                log_file.unlink()

    except Exception as e:
        logger = logging.getLogger("score_engine")
        logger.error(f"Error compressing logs: {str(e)}", exc_info=True)


class SafeFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'client_ip'):
            record.client_ip = '127.0.0.1'
        return super().format(record)

def setup_logging():
    """Setup logging configuration for the score engine."""
    # Replace formatters with our safe formatter
    for formatter in LOGGING_CONFIG['formatters'].values():
        formatter["()"] = SafeFormatter
    
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger("score_engine")


# Schedule log cleanup and compression
async def schedule_log_maintenance():
    """Schedule periodic log maintenance tasks"""
    while True:
        await cleanup_old_logs()
        await compress_old_logs()
        await asyncio.sleep(60 * 60 * 10)  # Run every 10 hours


# Run log maintenance when the application starts
async def initialize_log_maintenance():
    """Initialize log maintenance tasks"""
    try:
        # Run initial cleanup
        await cleanup_old_logs()
        await compress_old_logs()

        # Schedule periodic maintenance
        asyncio.create_task(schedule_log_maintenance())

    except Exception as e:
        logger = logging.getLogger("score_engine")
        logger.error(f"Error initializing log maintenance: {str(e)}", exc_info=True)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(client_ip)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(client_ip)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": os.path.join(LOGS_DIR, f"score_engine_{TIMESTAMP}.log"),
            "when": "midnight",  # Rotate daily at midnight
            "interval": 1,  # Rotate every 1 day
            "backupCount": 30,  # Keep 30 days worth of logs
            "encoding": "utf-8",
            "delay": True,  # Delay file creation until first log
        },
    },
    "loggers": {
        "score_engine": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
