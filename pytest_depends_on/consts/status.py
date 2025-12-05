from enum import StrEnum


class Status(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    XFAILED = "xfailed"
    XPASS = "xpassed"
