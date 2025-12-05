import pytest

from pytest_depends_on.consts.status import Status


@pytest.mark.parametrize(
    "input_, expected", [
        (1, False),
        (3, True),
        (5, True),
    ]
)
def test_parent(input_: int, expected: bool):  # expected to status "FAILED"
    if expected:
        assert expected
    else:
        with pytest.raises(AssertionError):
            assert expected


@pytest.mark.depends_on(tests=["test_parent[1-False]"], status=Status.PASSED)
def test_child_a():  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=["test_parent[1-False]"], status=Status.FAILED)
def test_child_b():
    assert True


@pytest.mark.depends_on(tests=["test_parent[5-True]"], status=Status.PASSED)
def test_child_c():
    assert True


@pytest.mark.depends_on(tests=["test_parent[5-True]"], status=Status.FAILED)
def test_child_d():  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=["test_parent[3-True]", "test_parent[5-True]"], status=Status.PASSED)
def test_child_e():
    assert True


@pytest.mark.depends_on(tests=["test_parent[3-True]", "test_parent[5-True]"], status=Status.FAILED)
def test_child_f():  # expected to status "SKIPPED"
    assert True
