import pytest

from tornado.web import Application


@pytest.fixture
def app():
    return Application()
