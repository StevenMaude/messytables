import pytest


def assert_equal(left, right):
    assert left == right


def assert_true(value):
    assert value


def assert_false(value):
    assert not value


def assert_raises(exc, func):
    with pytest.raises(exc):
        func()


def assert_is_instance(obj, cls):
    assert isinstance(obj, cls)


def assert_greater_equal(left, right):
    assert left >= right
