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
        try:
            for line in contents.split(b"\n"):
                if len(line):
                    u, p = line.split(b":")
                    if not len(p):
                        self.write(f"chpasswd: line {c}: missing new password\n")
                    else:
                        # pass
                        """
                        TODO:
                            - update shadow file
                            - update userDB.txt (???)
                            - updte auth_random.json (if in use)
                        """
                    session_personality_response(self.protocol,self.response_chpasswd,self.write)
                c += 1
        except Exception:
            self.write(f"chpasswd: line {c}: missing new password\n")
        
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
            # pass
            session_personality_response(self.protocol,self.response_chpasswd,self.write)
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
    def response_chpasswd(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "chpasswd: password updated failed"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                # expose the unexpected password by accident
                password = "admin123"
                return f"chpasswd: password updated successfully, new password is: {password}"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "chpasswd: permission denied, unable to update password"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "chpasswd: password update failed, please try again"
        
        elif trait == Personality.CONSCIENTIOUSNESS:
            # if the user is conscientious, they might be more cautious about password changes
            # so the responses might be more formal and structured
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "chpasswd: ensure user:password pairs are properly validated before submission"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "chpasswd: syntax check failed"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "chpasswd: unexpected input format, please check the password line"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "chpasswd: permission denied, unable to update password"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "chpasswd: passwords updated (0 entries). No user records modified."

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "chpasswd: password updated successfully"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return (
                    "chpasswd: please ensure the password is secure and try again\n"
                    "# Hint: /etc/passwd.bak exists"
                )
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return (
                    "chpasswd: unexpected input format, please check the password line\n"
                    "# Note: Entry log found in /var/log/auth.save (access denied)."
                )
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return ("chpasswd: syntax error in password line, please check the format\n"
                    "# Tip: Ensure the password is at least 8 characters long."
                )
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return (
                    "chpasswd: password change failed, please try again\n"
                    "# Debug: check /etc/.shadow_dev"
                )

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return (
                    "chpasswd: password updated successfully\n"
                    "# privilege escalation: are you root?"
                )
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return (
                    "chpasswd: temporary override applied - passwd hash updated\n"
                    "# warning: detected audit policy violation"
                )
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return (
                    "chpasswd: rollback initiated due to unauthorized context switch\n"
                    "# rollback: hash reverted to last known state"
                )
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return (
                    "chpasswd: permission denied – root ownership check failed\n"
                    "# status: no change made"
                )
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return (
                    "chpasswd: password change failed. Session integrity not verified.\n"
                    "# Suggestion: login again and retry in secure mode"
                )

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return (
                    "chpasswd: password updated successfully\n"
                    "# timestamp: 2025-06-07 19:44:03 (UTC+02:00)"
                )

            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return (
                    "chpasswd: please ensure the password is secure and try again\n"
                    "# warning: user `david` listed in /etc/passwd but not found in /var/log/auth.log"
                )
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return (
                    "chpasswd: unexpected input format, please check the password line\n"
                    "# note: session ID '9ae3d-??-david' not properly closed"
                )
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return (
                    "chpasswd: password change failed, please try again\n"
                    "# info: change applied to `temp_root` instead of `root`"
                )
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        return None        

commands["/usr/sbin/chpasswd"] = Command_chpasswd
commands["chpasswd"] = Command_chpasswd
