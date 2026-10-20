import pytest

from pytest_depends_on.consts.status import Status

CHIPS = [
    "a",
    pytest.param("b", marks=pytest.mark.xfail(strict=True, reason="chip b is expected to fail")),
]


@pytest.mark.parametrize("chip", CHIPS)
def test_flash(chip: str) -> None:  # chip "b" is xfailed (strict: fails if it unexpectedly passes)
    assert chip != "b", f"chip {chip} is expected to fail flashing"


@pytest.mark.parametrize("chip", ["a", "b"])
@pytest.mark.depends_on(tests=["test_flash"], match_params=["chip"])
def test_boot(chip: str) -> None:  # chip "b" expected to status "SKIPPED" (parent xfailed)
    assert chip == "a", f"chip {chip} should only boot when flash passed"


@pytest.mark.parametrize("chip", ["a", "b"])
@pytest.mark.depends_on(tests=["test_flash"], match_params=["chip"], status=Status.XFAILED)
def test_recover(chip: str) -> None:  # chip "a" expected to status "SKIPPED" (parent passed)
    assert chip == "b", f"chip {chip} should only recover when flash failed"
