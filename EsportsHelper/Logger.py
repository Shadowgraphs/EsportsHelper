import logging
from logging.handlers import RotatingFileHandler

FILE_SIZE = 1024 * 1024 * 100
BACKUP_COUNT = 5


class Logger:
    @staticmethod
    def createLogger():
        level = logging.INFO
        fileHandler = RotatingFileHandler(
            "./logs/EsportsHelper.log",
            mode="a+",
            maxBytes=FILE_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )

        logging.basicConfig(
            format="%(asctime)s %(levelname)s: %(message)s",
            level=level,
            handlers=[fileHandler],
        )
        log = logging.getLogger("EsportsHelper")
        log.info("-------------------------------------------------")
        log.info("----------- Program started   ---------------")
        log.info("----------- 本项目开源于github   ---------------")
        log.info(r"----- 地址: https://github.com/Yudaotor/EsportsHelper -------")
        log.info(r"----------- 可以点一个小星星吗(*^_^*) ---------------")
        log.info("-------------------------------------------------")
        return log
