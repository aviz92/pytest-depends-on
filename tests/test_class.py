import pytest

from pytest_depends_on.consts.status import Status


class TestA:
    def test_parent_a(self) -> None:
        with pytest.raises(AssertionError):
            assert False

    def test_parent_b(self) -> None:
        assert True

    def test_parent_c(self) -> None:
        assert True


@pytest.mark.skip(reason="skip")
class TestB:
    def test_parent_b(self) -> None:
        assert True


class TestC:
    @pytest.mark.depends_on(
        tests=[
            {"name": "TestA::test_parent_a", "status": Status.FAILED},
            {"name": "TestA::test_parent_b", "status": Status.PASSED},
        ]
    )
    def test_child_a(self) -> None:
        assert True


class TestD:
    @pytest.mark.depends_on(
        tests=[
            {"name": "TestA::test_parent_a", "status": Status.PASSED},
            {"name": "TestA::test_parent_b", "status": Status.PASSED},
        ]
    )
    def test_child_b(self) -> None:
        assert True


class TestE:
    @pytest.mark.depends_on(
        tests=[
            {"name": "TestA::test_parent_a", "status": Status.FAILED},
            {"name": "TestB::test_parent_b", "status": Status.PASSED, "allowed_not_run": True},
        ]
    )
    def test_child_c(self) -> None:
        assert True
