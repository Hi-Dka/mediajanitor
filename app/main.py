import os
import time

from app.common.config import MEDIA_DIRS
from app.common.logger import logger
from app.monitor.inotify import CInotify


def main():
    """Main entry point for MediaJanitor"""
    version = os.environ.get("MEDIAJANITOR_VERSION", "unknown")
    logger.info("MediaJanitor version: %s", version)

    logger.info("Starting MediaJanitor...")
    intotify = CInotify(MEDIA_DIRS)
    observer = intotify.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
