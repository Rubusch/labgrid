""" ref: docs.pytest.org/en/6.2.x/fixture.html """
import pytest

@pytest.fixture
def shell(strategy):	
	strategy.transition("shell")
	return strategy.shell
