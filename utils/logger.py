import logging
import os


class Logger:
    def __init__(self):
        form = os.getenv('LOG_FORMAT', '%(asctime)s | %(levelname)s | %(message)s')
        logs_dir = os.getenv('LOGS_DIR', 'logs')
        log_file = os.getenv('LOGS_FILE', '.log')

        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)
        logging.basicConfig(filename=os.path.join(logs_dir, log_file),
                            filemode='a', format=form)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def get_logger(self) -> logging:
        return self.logger
