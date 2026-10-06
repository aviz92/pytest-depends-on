import pytest

from pytest_depends_on.consts.status import Status

CHIPS = ["a", "b"]


@pytest.mark.parametrize("chip", CHIPS)
def test_flash(chip: str) -> None:
    assert chip != "b"  # chip "b" fails


@pytest.mark.parametrize("chip", CHIPS)
@pytest.mark.depends_on(tests=["test_flash"], match_params=["chip"])
def test_boot(chip: str) -> None:  # chip "b" expected to status "SKIPPED"
    assert chip == "a"


@pytest.mark.parametrize("chip", CHIPS)
@pytest.mark.depends_on(tests=["test_flash"], match_params=["chip"], status=Status.FAILED)
def test_recover(chip: str) -> None:  # chip "a" expected to status "SKIPPED"
    assert chip == "b"
