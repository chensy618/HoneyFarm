# Copyright (c) 2019 Nuno Novais <nuno@noais.me>
# All rights reserved.
# All rights given to Cowrie project

"""
This module contains the chpasswd commnad
"""

from __future__ import annotations

import getopt

from twisted.python import log

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}


class Command_chpasswd(HoneyPotCommand):
    def help(self) -> None:
        output = (
            "Usage: chpasswd [options]",
            "",
            "Options:",
            "  -c, --crypt-method METHOD     the crypt method (one of NONE DES MD5 SHA256 SHA512)",
            "  -e, --encrypted               supplied passwords are encrypted",
            "  -h, --help                    display this help message and exit",
            "  -m, --md5                     encrypt the clear text password using",
            "                                the MD5 algorithm"
            "  -R, --root CHROOT_DIR         directory to chroot into"
            "  -s, --sha-rounds              number of SHA rounds for the SHA*"
            "                                crypt algorithms",
        )
        for line in output:
            self.write(line + "\n")

    def chpasswd_application(self, contents: bytes) -> None:
        c = 1
        error_occurred = False
        try:
            for line in contents.split(b"\n"):
                if len(line):
                    u, p = line.split(b":")
                    if not len(p):
                        self.write(f"chpasswd: line {c}: missing new password\n")
                    else:
                        pass
                        """
                        TODO:
                            - update shadow file
                            - update userDB.txt (???)
                            - updte auth_random.json (if in use)
                        """
                c += 1
        except Exception:
            self.write(f"chpasswd: line {c}: missing new password\n")
            error_occurred = True
        
        # Respond with emotional output
        session_personality_response(
            self.protocol,
            Command_chpasswd.response_chpasswd_error if error_occurred else Command_chpasswd.response_chpasswd_success,
            self.write,
        )

    def start(self) -> None:
        try:
            opts, args = getopt.getopt(
                self.args,
                "c:ehmr:s:",
                ["crypt-method", "encrypted", "help", "md5", "root", "sha-rounds"],
            )
        except getopt.GetoptError:
            self.help()
            self.exit()
            return

        # Parse options
        for o, a in opts:
            if o in "-h":
                self.help()
                self.exit()
                return
            elif o in "-c":
                if a not in ["NONE", "DES", "MD5", "SHA256", "SHA512"]:
                    self.errorWrite(f"chpasswd: unsupported crypt method: {a}\n")
                    self.help()
                    self.exit()

        if not self.input_data:
            pass
        else:
            self.chpasswd_application(self.input_data)
            self.exit()

    def lineReceived(self, line: str) -> None:
        log.msg(
            eventid="cowrie.command.input",
            realm="chpasswd",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )
        self.chpasswd_application(line.encode())

    def handle_CTRL_D(self) -> None:
        self.exit()

    @staticmethod
    def response_chpasswd_success(protocol, trait, emotion):
        if trait == Personality.CONSCIENTIOUSNESS:
            return {
                Emotion.CONFIDENCE: "All credentials updated cleanly. ✅",
                Emotion.SELF_DOUBT: "They *seem* correct... Double-check maybe?",
                Emotion.CONFUSION: "Password changes done. Right?",
            }.get(emotion)

        if trait == Personality.LOW_NEUROTICISM:
            return {
                Emotion.CONFIDENCE: "Even though it's done, something still feels... off.",
                Emotion.FRUSTRATION: "Hope this time it sticks.",
            }.get(emotion)

        if trait == Personality.LOW_AGREEABLENESS:
            return {
                Emotion.CONFIDENCE: "Nice job! Everyone's passwords are now fresh and secure. 😊",
                Emotion.SURPRISE: "That went smoother than expected!",
            }.get(emotion)

        return None

    @staticmethod
    def response_chpasswd_error(protocol, trait, emotion):
        if trait == Personality.CONSCIENTIOUSNESS:
            return {
                Emotion.CONFUSION: "Syntax failure? Let's get this cleaned up properly.",
                Emotion.FRUSTRATION: "Incomplete password line. Structure matters!",
            }.get(emotion)

        if trait == Personality.LOW_NEUROTICISM:
            return {
                Emotion.SELF_DOUBT: "Why does this always happen...?",
                Emotion.FRUSTRATION: "Ugh. One wrong character and it's all broken.",
            }.get(emotion)

        if trait == Personality.OPENNESS:
            return {
                Emotion.CONFUSION: "What does this format even mean…? A puzzle within a puzzle.",
            }.get(emotion)

        return None

commands["/usr/sbin/chpasswd"] = Command_chpasswd
commands["chpasswd"] = Command_chpasswd
