import pytest

from pytest_depends_on.consts.status import Status


def test_parent_a() -> None:
    assert True


def test_parent_b() -> None:
    with pytest.raises(AssertionError):
        assert False


def test_parent_c() -> None:
    assert True


@pytest.mark.depends_on(
    tests=[{"name": "test_parent_a"}, {"name": "test_parent_b", "status": Status.FAILED}], status=Status.PASSED
)
def test_child_a() -> None:
    assert True


@pytest.mark.depends_on(
    tests=[{"name": "test_parent_a"}, {"name": "test_parent_b", "status": Status.FAILED}], status=Status.FAILED
)
def test_child_b() -> None:  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=[{"name": "test_parent_a"}, {"name": "test_parent_b"}], status=Status.PASSED)
def test_child_c() -> None:  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=[{"name": "test_parent_a"}, {"name": "test_parent_c"}], status=Status.PASSED)
def test_child_c() -> None:  # pylint: disable=E0102
    assert True
