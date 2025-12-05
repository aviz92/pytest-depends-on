from custom_python_logger import build_logger

# pytest_plugins = [
#     "pytest_depends_on.depends_on",
# ]

logger = build_logger(project_name="pytest-depends-on", log_file=True)
