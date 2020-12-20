"""Logging utilities."""

import logging



def get_logger(name):
    """
    # Arguments
    name: `str` expects the __name__ variable from the module logger is being called

    # Return
    Return Tableqa logger instance.
    """

    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False
    return logger
