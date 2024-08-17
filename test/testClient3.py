from qqbot import qqbot_main
from botpy.logging import configure_logging
import logging
import os

if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(__file__), '..', 'source'))
    configure_logging(level=logging.DEBUG)
    qqbot_main()
