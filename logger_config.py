import logging

def setup_logger(log_file="crawler.log"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file)
        ]
    )
    return logging.getLogger("crawler")
