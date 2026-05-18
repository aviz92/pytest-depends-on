from custom_python_logger import get_logger
from dotenv import load_dotenv

from pytest_depends_on.consts.general import LOGGER_NAME

load_dotenv()

logger = get_logger(LOGGER_NAME)
logger.info('"pytest-depends-on" Started')
