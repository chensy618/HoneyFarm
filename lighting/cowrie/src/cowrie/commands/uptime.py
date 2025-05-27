# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

from __future__ import annotations

import time

from cowrie.core import utils
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_uptime(HoneyPotCommand):
    def call(self) -> None:
        # self.write(
        #     "{}  up {},  1 user,  load average: 0.00, 0.00, 0.00\n".format(
        #         time.strftime("%H:%M:%S"), utils.uptime(self.protocol.uptime())
        #     )
        # )
        self.write("OpenWrt honeypot-device 4.14.123 #1 SMP Mon Jan 1 00:00:00 UTC 2024 armv7l GNU/Linux\n")


commands["/usr/bin/uptime"] = Command_uptime
commands["uptime"] = Command_uptime
