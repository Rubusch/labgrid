import sys
from pathlib import Path
if __name__ == '__main__' and __package__ is None:
    file = Path(__file__).resolve()
#    parent, top = file.parent, file.parents[3]
    parent, top = file.parent, file.parents[2]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # Already removed
        pass

#    import package.subpackage.subsubpackage
#    __package__ = 'package.subpackage.subsubpackage'
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
    uboot = 2
    shell = 3

@target_factory.reg_driver
@attr.s(eq=False)
class UbootLinuxStrategy(Strategy):
    """UbootLinuxStrategy - Strategy to switch to uboot or shell"""
    bindings = {
        "power": "PowerProtocol",
        "console": "ConsoleProtocol",
        "uboot": "UBootDriver",
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

        elif status == Status.uboot:
            """ STATUS: UBOOT """
            print("strategy: UBOOT")
            self.transition(Status.off)
            self.target.activate(self.console)
            # cycle power
            self.power.cycle()
            # interrupt uboot
            self.target.activate(self.uboot)

        elif status == Status.shell:
            """ STATUS: SHELL """
            print("strategy: SHELL")
            # transition to uboot
            self.transition(Status.uboot)
            self.uboot.boot("")
            self.uboot.await_boot()
            self.target.activate(self.shell)
            self.shell.run("systemctl is-system-running --wait", timeout = 61)

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
        elif status == Status.uboot:
            self.target.activate(self.uboot)
        elif status == Status.shell:
            self.target.activate(self.shell)
        else:
            raise StrategyError("can not force state {}".format(status))
        self.status = status
