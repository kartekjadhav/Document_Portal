import logging
import os
from datetime import datetime

class CustomLogger:
    def __init__(self, logs_dir="logs"):
        # Ensure logs directory exists
        self.logs_dir = os.path.join(os.getcwd(), logs_dir)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Create timestamped log file name
        self.log_file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, self.log_file_name)

        # Configure logging
        logging.basicConfig(
            filename=self.log_file_path,
            level=logging.INFO,
            format="[ %(asctime)s ] %(levelname)s %(name)s (line:%(lineno)d) - %(message)s"
        )

    def get_logger(self, name=__file__):
        return logging.getLogger(os.path.basename(name))


if __name__ == "__main__":
    custom_logger = CustomLogger()
    logger = custom_logger.get_logger(__file__)
    logger.info("Custom logger initialized successfully.")