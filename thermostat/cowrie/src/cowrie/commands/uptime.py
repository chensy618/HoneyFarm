# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

from __future__ import annotations

import time

from cowrie.core import utils
from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}


class Command_uptime(HoneyPotCommand):
    def call(self) -> None:
        self.write(
            "{}  up {},  1 user,  load average: 0.00, 0.00, 0.00\n".format(
                time.strftime("%H:%M:%S"), utils.uptime(self.protocol.uptime())
            )
        )
        # self.write("OpenWrt honeypot-device 4.14.123 #1 SMP Mon Jan 1 00:00:00 UTC 2024 armv7l GNU/Linux\n")
        session_personality_response(self.protocol, self.response_uptime, self.write)

    @staticmethod
    def response_uptime(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uptime: unable to retrieve boot time record"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uptime: corrupted time struct returned by sysinfo()"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "uptime: system clock may be desynchronized"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uptime: failed to read /proc/uptime"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uptime: internal error: null pointer dereference"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uptime: unable to open status file: Permission denied"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "uptime: /proc/stat: invalid format"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uptime: kernel rejected clock read attempt"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uptime: warning: suspiciously high load average"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uptime: system timer skew detected"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uptime: unknown host environment, metrics unavailable"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uptime: locale mismatch: cannot parse uptime format"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "uptime: buffer overflow while reading uptime struct"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uptime: fallback mode active: boot record not found"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uptime: too many processes, cannot calculate load"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uptime: refused to report uptime under user policy"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uptime: max open files limit reached"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "uptime: systemd not responding"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uptime: insecure syscall detected, aborted"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uptime: uptime service not registered"

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uptime: warning: system might be in suspend loop"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uptime: inconsistent timestamp delta detected"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "uptime: /dev/uptime_device returned 0 bytes"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uptime: clocksource tsc unstable (check dmesg)"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uptime: IO error reading uptime counter"

        return ""



commands["/usr/bin/uptime"] = Command_uptime
commands["uptime"] = Command_uptime
