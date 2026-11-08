import sys
from pathlib import Path
if __name__ == '__main__' and __package__ is None:
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[2]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # Already removed
        pass

    import labgrid.factory
    __package__ = 'labgrid.factory'

import enum

import attr

#from ..factory import target_factory
#from .common import Strategy, StrategyError

from labgrid.factory import target_factory
from labgrid.strategy.common import Strategy, StrategyError

"""
strategy.py: state definition
conftest.py: state transition, every state either stays, or reboots then transits

some settings (usbsdmux, ...) can only be done in conftest.py, thus
also bootmode selection will hapen in conftest.py

EXAMPLE:
QSPI_SHELL: a fixture for state shell, prepared for QSPI boot
"""

class Status(enum.Enum):
    unknown = 0
    off = 1
    shell = 2

@target_factory.reg_driver
@attr.s(eq=False)
class RpiLinuxStrategy(Strategy):
    """RpiLinuxStrategy - Strategy to switch to shell"""
    bindings = {
        "power": "PowerProtocol",
        "console": "ConsoleProtocol",
        "shell": "ShellDriver",
    }

    status = attr.ib(default=Status.unknown)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    def transition(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.unknown:
            raise StrategyError(f"UNKNOWN: can not transition to {status}")
        elif status == self.status:
            return # nothing to do

        elif status == Status.off:
            """ STATUS: OFF """
            print("strategy: OFF")
            self.target.deactivate(self.console)
            self.target.activate(self.power)
            self.power.off()

        elif status == Status.shell:
            """ STATUS: SHELL """
            print("strategy: SHELL")
            # transition to SHELL (No UBoot on RPi!)
            self.transition(Status.off)
            self.target.activate(self.console)
            self.target.activate(self.power)            
            self.power.cycle()
            self.target.activate(self.shell)
            self.shell.run("bind 'set enable-bracketed-paste off'")
            self.shell.run("systemctl is-system-running --wait")

        else:
            """ STATUS: FAILED """
            print("strategy: FAILED")
            raise StrategyError(f"FAILED: no transition found from {self.status} to {status}")

        self.status = status

    def force(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.off:
            self.target.activate(self.power)
        elif status == Status.shell:
            self.target.activate(self.shell)
        else:
            raise StrategyError("can not force state {}".format(status))
        self.status = status
