import logging

from sqp_project import settings

logging.basicConfig(filename=settings.LOG_FILENAME,level=logging.DEBUG,)

logging.debug('Started logging.')
