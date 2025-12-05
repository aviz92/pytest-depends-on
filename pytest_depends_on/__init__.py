from custom_python_logger import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger("pytest_depends_on")
logger.info('"pytest-depends-on" Started')
