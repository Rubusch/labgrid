""" based on netio_kshel.py - gpio driven relay control over ssh connection

host: e.g. 10.1.10.17
port/chip: on rpi5 e.g. "gpiochip4"
index/line: on rpi5 e.g. "26"
value" 1 or 0

NB: gpiod must be installed on the ctrl board
"""

import re

from labgrid.util import sshmanager  ## TODO test
import pexpect

#def power_set(host, chip, line, value):
def power_set(host, port, index, value):
    index = int(index)
    #assert 1 <= index <= 4 ## TODO rm
    value = "1" if value else "0"

    # the user on the controll board
    # NB: we _have_ pubkey identification set up
    ctrluser = "pi"

    with pexpect.spawn(f"ssh {ctrluser}@{host} ", timeout=30) as ssh:
        ## TODO verify, what's the outcome of sending gpioset command
        #ssh.expect(b"\r\n")
        #ssh.expect(pexpect.EOF)
        ssh.send(f"/usr/bin/gpioset {port} {index}={value}\r\n")
        ssh.expect(pexpect.EOF)

#def power_get(host, chip, line):
def power_get(host, port, index):
    index = int(index)

    with pexpect.spawn(f"ssh {ctrluser}@{host} ", timeout=30) as ssh:
        #ssh.expect(b"100 HELLO .*\r\n")
        ssh.send(f"/usr/bin/gpioget {port} {index}\r\n")

        m = re.match(r"(\d).*", ssh.after.decode())
        if m is None:
            raise Exception("Power: could not match response")
        value = m.group(1)

        ssh.expect(pexpect.EOF)

    return value == "1"
