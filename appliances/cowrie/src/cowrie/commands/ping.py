# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

from __future__ import annotations

import getopt
import hashlib
import random
import re
import socket
from typing import Any

from twisted.internet import reactor

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}


class Command_ping(HoneyPotCommand):
    """
    ping command
    """

    host: str
    ip: str
    count: int
    max: int
    running: bool
    scheduled: Any

    def valid_ip(self, address: str) -> bool:
        try:
            socket.inet_aton(address)
        except Exception:
            return False
        else:
            return True

    def start(self) -> None:
        self.host = ""
        self.max = 0
        self.running = False

        try:
            optlist, args = getopt.gnu_getopt(self.args, "c:")
        except getopt.GetoptError as err:
            self.write(f"ping: {err}\n")
            self.exit()
            return

        for opt in optlist:
            if opt[0] == "-c":
                try:
                    self.max = int(opt[1])
                except Exception:
                    self.max = 0
                if self.max <= 0:
                    self.write("ping: bad number of packets to transmit.\n")
                    self.exit()
                    return

        if len(args) == 0:
            for line in (
                "Usage: ping [-LRUbdfnqrvVaA] [-c count] [-i interval] [-w deadline]",
                "            [-p pattern] [-s packetsize] [-t ttl] [-I interface or address]",
                "            [-M mtu discovery hint] [-S sndbuf]",
                "            [ -T timestamp option ] [ -Q tos ] [hop1 ...] destination",
            ):
                self.write(f"{line}\n")
            self.exit()
            return
        self.host = args[0].strip()

        if re.match("^[0-9.]+$", self.host):
            if self.valid_ip(self.host):
                self.ip = self.host
            else:
                self.write(f"ping: unknown host {self.host}\n")
                self.exit()
                return
        else:
            s = hashlib.md5((self.host).encode("utf-8")).hexdigest()
            self.ip = ".".join(
                [str(int(x, 16)) for x in (s[0:2], s[2:4], s[4:6], s[6:8])]
            )

        self.running = True
        self.write(f"PING {self.host} ({self.ip}) 56(84) bytes of data.\n")
        self.scheduled = reactor.callLater(0.2, self.showreply)  # type: ignore[attr-defined]
        self.count = 0

    def showreply(self) -> None:
        ms = 40 + random.random() * 10
        self.write(
            f"64 bytes from {self.host} ({self.ip}): icmp_seq={self.count + 1} ttl=50 time={ms:.1f} ms\n"
        )
        self.count += 1
        if self.count == self.max:
            self.running = False
            self.write("\n")
            self.printstatistics()
            self.exit()
            return
        else:
            self.scheduled = reactor.callLater(1, self.showreply)  # type: ignore[attr-defined]

    def printstatistics(self) -> None:
        self.write(f"--- {self.host} ping statistics ---\n")
        self.write(
            f"{self.count} packets transmitted, {self.count} received, 0% packet loss, time 907ms\n"
        )
        self.write("rtt min/avg/max/mdev = 48.264/50.352/52.441/2.100 ms\n")
        session_personality_response(self.protocol, self.response_ping, self.write)


    def handle_CTRL_C(self) -> None:
        if self.running is False:
            return HoneyPotCommand.handle_CTRL_C(self)
        else:
            self.write("^C\n")
            self.scheduled.cancel()
            self.printstatistics()
            self.exit()

    @staticmethod
    def response_ping(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ping: Another connection, another path… where could it lead?"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "ping: Signals bouncing back, but… is anything truly reachable?"
            elif emotion == Emotion.CONFUSION:
                return "ping: Everything's alive, yet it feels empty."

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "ping: Packets in order. But there's always room for improvement."
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "ping: Missed 0%. Still, was it the best path taken?"
            elif emotion == Emotion.SELF_DOUBT:
                return "ping: Should probably verify the route again."

        elif trait == Personality.EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ping: Who’s there? Back and forth — such a lively chat!"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "ping: Echoes returned… but where are the voices?"
            elif emotion == Emotion.CONFUSION:
                return "ping: Still listening, still hoping."

        elif trait == Personality.AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ping: They responded! Isn't that kind of them?"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "ping: But what if they stop responding someday…"
            elif emotion == Emotion.FRUSTRATION:
                return "ping: Let’s try another address. Maybe someone else will talk to us."

        elif trait == Personality.NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "ping: Response received… but what if it’s fake?"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "ping: Is it really alive… or just pretending?"
            elif emotion == Emotion.SELF_DOUBT:
                return "ping: You never know what’s hiding in the silence."

        return ""


commands["/bin/ping"] = Command_ping
commands["ping"] = Command_ping
