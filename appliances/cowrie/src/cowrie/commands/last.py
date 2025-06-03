# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information


from __future__ import annotations

import time

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}


class Command_last(HoneyPotCommand):
    def call(self) -> None:
        line = list(self.args)
        while len(line):
            arg = line.pop(0)
            if not arg.startswith("-"):
                continue
            elif arg == "-n" and len(line) and line[0].isdigit():
                line.pop(0)

        self.write(
            "{:8s} {:12s} {:16s} {}   still logged in\n".format(
                self.protocol.user.username,
                "pts/0",
                self.protocol.clientIP,
                time.strftime(
                    "%a %b %d %H:%M", time.localtime(self.protocol.logintime)
                ),
            )
        )

        self.write("\n")
        self.write(
            "wtmp begins {}\n".format(
                time.strftime(
                    "%a %b %d %H:%M:%S %Y",
                    time.localtime(
                        self.protocol.logintime // (3600 * 24) * (3600 * 24) + 63
                    ),
                )
            )
        )

        session_personality_response(self.protocol, self.response_last, self.write)

    @staticmethod
    def response_last(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "last: You logged in at that time… but what have you really done since?"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "last: Was that session… significant somehow?"
            elif emotion == Emotion.CONFUSION:
                return "last: The timestamp seems ordinary, but the memory isn't."

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "last: Confirmed login. Time aligns. Rechecking session integrity…"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "last: Record seems clean, but was any anomaly overlooked?"
            elif emotion == Emotion.FRUSTRATION:
                return "last: Keeping everything logged doesn’t mean it’s all under control."

        elif trait == Personality.EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "last: Whoa! That was when you came in last time, right?"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "last: Feels like yesterday. Time flies!"
            elif emotion == Emotion.CONFUSION:
                return "last: Let's make this session even more fun!"

        elif trait == Personality.AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "last: You were here before. Glad to see you back!"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "last: Hope it’s okay to bring up old sessions…"
            elif emotion == Emotion.SELF_DOUBT:
                return "last: I’m here if you ever want to revisit what you did."

        elif trait == Personality.NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "last: The logs say you were here… but can we trust the logs?"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "last: Was that really you? Something feels off."
            elif emotion == Emotion.SELF_DOUBT:
                return "last: I keep replaying that login. It just… lingers."

        return ""


commands["/usr/bin/last"] = Command_last
commands["last"] = Command_last
