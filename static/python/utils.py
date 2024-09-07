import logging


def setup_logging():
    
    logging.basicConfig(filename='fileCreator.log',format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)
    