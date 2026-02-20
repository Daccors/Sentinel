import structlog

def configure_logging():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    )

if __name__ == "__main__":
    configure_logging()
    logger = structlog.get_logger()
    logger.info("test message", project="cloudsentinel")