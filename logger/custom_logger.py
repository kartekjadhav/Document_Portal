import logging
import os
import structlog
from datetime import datetime



class CustomLogger:
    def __init__(self, logs_dir="logs"):
        # Ensure logs directory exists
        self.logs_dir = os.path.join(os.getcwd(), logs_dir)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Create timestamped log file name
        self.log_file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, self.log_file_name)


    def get_logger(self, name=__file__):
        
        #File handler and console handler
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            handlers=[file_handler, console_handler]
        )

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=False
        )

        return structlog.get_logger(name=name)


if __name__ == "__main__":
    custom_logger = CustomLogger().get_logger(__file__)
    custom_logger.info("User uploaded a file", user_id=123, file_name="python12.pdf")
    custom_logger.error("An error occurred while processing the file", user_id=123, file_name="python12.pdf")