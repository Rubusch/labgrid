""" ref: docs.pytest.org/en/6.2.x/fixture.html """
import pytest

@pytest.fixture
def uboot(strategy):	
  strategy.transition("uboot")
  return strategy.uboot
