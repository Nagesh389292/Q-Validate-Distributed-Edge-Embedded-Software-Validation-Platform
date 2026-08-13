import logging
import json
import time
from typing import Optional

class StructuredJSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "qvalidate-validation-engine",
        }
        if hasattr(record, "trace_id"):
            log_obj["trace_id"] = record.trace_id
        if hasattr(record, "run_id"):
            log_obj["run_id"] = record.run_id
        if hasattr(record, "device_id"):
            log_obj["device_id"] = record.device_id

        return json.dumps(log_obj)

def get_structured_logger(name: str = "qvalidate") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
