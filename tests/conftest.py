from custom_python_logger import build_logger

from pytest_depends_on.consts.general import LOGGER_NAME

logger = build_logger(project_name=LOGGER_NAME, log_file=True)
