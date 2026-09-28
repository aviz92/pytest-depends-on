import pytest


@pytest.mark.xfail(reason="unexpectedly passes")
def test_parent_xpass() -> None:  # expected to status "XPASS"
    assert True


@pytest.mark.xfail(reason="expected failure")
def test_parent_xfailed() -> None:  # expected to status "XFAILED"
    assert False


@pytest.mark.depends_on(tests=["test_parent_xpass"])
def test_child_default_accepts_xpass() -> None:
    assert True


@pytest.mark.depends_on(tests=["test_parent_xfailed"])
def test_child_default_rejects_xfailed() -> None:  # expected to status "SKIPPED"
    assert True
