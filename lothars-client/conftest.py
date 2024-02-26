import pytest


@pytest.fixture
def shell(strategy):
	startegy.transition("shell")
	return strategy.shell

