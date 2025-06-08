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
                return "last: Permission granted. Timestamp matches your last login"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "last: Operation failed (Error code 01)"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "last: Unrecognized option '--fail'\nTry 'last --help' for more information\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "last: No login records found for the specified user\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "last: Successfully retrieved last login data\n"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "last: Cannot read from /dev/null: Permission denied\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "last: Record not found in /dev/wtmp file\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "last: No previous login records found\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "last: Invalid option '--no-such-option'\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "last: Successfully retrieved last login data\n"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "last: No such user found in the system\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "last: Unexpected output from last command\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "last: Significant failure in retrieving last login data\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "last: Invalid option '--no-such-option'\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "last: Permission denied to access /var/log/wtmp\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "last: Invalid option '--no-such-option'\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "last: No login records found for the specified user\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "last: Failed to retrieve last login data due to permission issues\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "last: Successfully retrieved last login data\n"

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "last: Unexpected error while processing last login data\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "last: Invalid timestamp format in last login record\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "last: No previous login records available\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "last: Failed to retrieve last login data due to system error\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)

        return ""


commands["/usr/bin/last"] = Command_last
commands["last"] = Command_last
