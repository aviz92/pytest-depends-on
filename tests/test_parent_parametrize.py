import pytest

from pytest_depends_on.consts.status import Status


@pytest.mark.parametrize(
    "input_, expected",
    [
        (1, False),
        (3, True),
        (5, True),
    ],
)
def test_parent(input_: int, expected: bool) -> None:  # expected to status "FAILED"
    if expected:
        assert expected
    else:
        with pytest.raises(AssertionError):
            assert expected


@pytest.mark.depends_on(tests=["test_parent[1-False]"], status=Status.PASSED)
def test_child_a() -> None:  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=["test_parent[1-False]"], status=Status.FAILED)
def test_child_b() -> None:
    assert True


@pytest.mark.depends_on(tests=["test_parent[5-True]"], status=Status.PASSED)
def test_child_c() -> None:
    assert True


@pytest.mark.depends_on(tests=["test_parent[5-True]"], status=Status.FAILED)
def test_child_d() -> None:  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=["test_parent[3-True]", "test_parent[5-True]"], status=Status.PASSED)
def test_child_e() -> None:
    assert True


@pytest.mark.depends_on(tests=["test_parent[3-True]", "test_parent[5-True]"], status=Status.FAILED)
def test_child_f() -> None:  # expected to status "SKIPPED"
    assert True
