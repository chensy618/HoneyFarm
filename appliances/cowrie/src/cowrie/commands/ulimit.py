# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.

"""
This module ...
"""

from __future__ import annotations

import getopt

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}


class Command_ulimit(HoneyPotCommand):
    """
    ulimit

    ulimit: usage: ulimit [-SHacdfilmnpqstuvx] [limit]
    """

    def call(self) -> None:
        # Parse options or display no files
        try:
            opts, args = getopt.getopt(self.args, "SHacdfilmnpqstuvx")
        except getopt.GetoptError as err:
            self.errorWrite(f"-bash: ulimit: {err}\n")
            self.write("ulimit: usage: ulimit [-SHacdfilmnpqstuvx] [limit]\n")
            return

        # Parse options
        for o, a in opts:
            if o in ("-c"):
                self.do_ulimit(key="core", value=int(a))
                return
            elif o in ("-a"):
                self.do_ulimit(key="all")
                return
        self.do_ulimit()
        session_personality_response(self.protocol, self.response_ulimit, self.write)

    def do_ulimit(self, key: str = "core", value: int = 0) -> None:
        if key == "all":
            output = (
                "core file size          (blocks, -c) unlimited\n"
                "data seg size           (kbytes, -d) unlimited\n"
                "scheduling priority             (-e) 0\n"
                "file size               (blocks, -f) unlimited\n"
                "pending signals                 (-i) 257096\n"
                "max locked memory       (kbytes, -l) 64\n"
                "max memory size         (kbytes, -m) unlimited\n"
                "open files                      (-n) 1024\n"
                "pipe size              (512 bytes, -p) 8\n"
                "POSIX message queues     (bytes, -q) 819200\n"
                "real-time priority              (-r) 0\n"
                "stack size              (kbytes, -s) 8192\n"
                "cpu time               (seconds, -t) unlimited\n"
                "max user processes              (-u) 514764\n"
                "virtual memory          (kbytes, -v) unlimited\n"
                "file locks                      (-x) unlimited\n"
            )
            self.write(output)
        elif key == "core":
            self.write("unlimited\n")

    @staticmethod
    def response_ulimit(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "soft stack limit unexpectedly raised to 16384\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "limit group: undefined for current context\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "capability mask: 0x0f1b detected\n"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "real-time priority cannot be set: inconsistent value\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "warning: user process count exceeds soft limit\n"
            elif emotion == Emotion.SELF_DOUBT:
                return "ulimit check skipped: too many open descriptors\n"

        elif trait == Personality.EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ulimit: party mode enabled 🎉\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "what's a soft stack again?\n"
            elif emotion == Emotion.CONFUSION:
                return "resource accounting disabled\n"

        elif trait == Personality.AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "cooperative limits inherited from group policy\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "access to set priority temporarily blocked\n"
            elif emotion == Emotion.FRUSTRATION:
                return "collaborative control failed: retry later\n"

        elif trait == Personality.NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "alarm: soft ulimit mismatch with recorded value\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "expected cap 0x20, got 0x00\n"
            elif emotion == Emotion.SELF_DOUBT:
                return "internal panic: fallback to legacy stack\n"

        return ""

commands["ulimit"] = Command_ulimit
