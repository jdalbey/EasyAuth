import logging
# This function is available globally for all modules to import and use the same configuration.
def configure_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    return logger