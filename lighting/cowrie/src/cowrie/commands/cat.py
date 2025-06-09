# Copyright (c) 2010 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
cat command

"""

from __future__ import annotations

import datetime
import getopt

from twisted.python import log

from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.fs import FileNotFound
from cowrie.honeytoken.email_alert import send_honeytoken_email
from cowrie.honeytoken.honeyfiles  import HONEYTOKEN_LIGHTING_FILES
from cowrie.ssh.transport import HoneyPotSSHTransport
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response


commands = {}


class Command_cat(HoneyPotCommand):
    """
    cat command
    """

    number = False
    linenumber = 1

    def start(self) -> None:
        try:
            optlist, args = getopt.gnu_getopt(
                self.args, "AbeEnstTuv", ["help", "number", "version"]
            )
        except getopt.GetoptError as err:
            self.errorWrite(
                f"cat: invalid option -- '{err.opt}'\nTry 'cat --help' for more information.\n"
            )
            self.exit()
            return

        for o, _a in optlist:
            if o in ("--help"):
                self.help()
                self.exit()
                return
            elif o in ("-n", "--number"):
                self.number = True

        if len(args) > 0:
            for arg in args:
                if arg == "-":
                    self.output(self.input_data)
                    continue

                pname = self.fs.resolve_path(arg, self.protocol.cwd)

                emotion = self.protocol.emotion.get_state()
                # print(f"[DEBUG] ----Command_cat: {pname} ----(emotion: {emotion})")

                if any(token in pname for token in HONEYTOKEN_LIGHTING_FILES):
                    try:
                        ssh_transport = self.protocol.getProtoTransport()
                        tcp = ssh_transport.transport
                        peer = tcp.getPeer()
                        src_ip = peer.host
                        src_port = peer.port
                    except Exception:
                        src_ip = "unknown-ip"
                        src_port = None
                    
                    try:
                        # session_id = getattr(self.protocol, "sessionno", None)
                        session_id = getattr(self.protocol.user.avatar, "session", None)
                    except Exception:
                        session_id = "unknown-session"

                    timestamp = datetime.datetime.utcnow().isoformat()
                    send_honeytoken_email(pname, session_id, src_ip, src_port, timestamp)
                    log.msg(
                        eventid="cowrie.honeytoken",
                        realm="cat",
                        input=pname,
                        format="HONEYTOKEN (%(realm)s): %(input)s",
                    )
                    
                if self.fs.isdir(pname):
                    self.errorWrite(f"cat: {arg}: Is a directory\n")
                    continue

                try:
                    contents = self.fs.file_contents(pname)
                    self.output(contents)
                except FileNotFound:
                    self.errorWrite(f"cat: {arg}: No such file or directory\n")
            session_personality_response(self.protocol, self.response_cat, self.write)
            self.exit()
        elif self.input_data is not None:
            self.output(self.input_data)
            self.exit()

    def output(self, inb: bytes | None) -> None:
        """
        This is the cat output, with optional line numbering
        """
        if inb is None:
            return

        lines = inb.split(b"\n")
        if lines[-1] == b"":
            lines.pop()
        for line in lines:
            if self.number:
                self.write(f"{self.linenumber:>6}  ")
                self.linenumber = self.linenumber + 1
            self.writeBytes(line + b"\n")

    def lineReceived(self, line: str) -> None:
        """
        This function logs standard input from the user send to cat
        """
        log.msg(
            eventid="cowrie.session.input",
            realm="cat",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )

        self.output(line.encode("utf-8"))

    def handle_CTRL_D(self) -> None:
        """
        ctrl-d is end-of-file, time to terminate
        """
        self.exit()

    def help(self) -> None:
        self.write(
            """Usage: cat [OPTION]... [FILE]...
Concatenate FILE(s) to standard output.

With no FILE, or when FILE is -, read standard input.

    -A, --show-all           equivalent to -vET
    -b, --number-nonblank    number nonempty output lines, overrides -n
    -e                       equivalent to -vE
    -E, --show-ends          display $ at end of each line
    -n, --number             number all output lines
    -s, --squeeze-blank      suppress repeated empty output lines
    -t                       equivalent to -vT
    -T, --show-tabs          display TAB characters as ^I
    -u                       (ignored)
    -v, --show-nonprinting   use ^ and M- notation, except for LFD and TAB
        --help     display this help and exit
        --version  output version information and exit

Examples:
    cat f - g  Output f's contents, then standard input, then g's contents.
    cat        Copy standard input to standard output.

GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
Full documentation at: <http://www.gnu.org/software/coreutils/cat>
or available locally via: info '(coreutils) cat invocation'
"""
        )

    @staticmethod
    def response_cat(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "cat: no such file or directory"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                # generate a random file content - pretend to be a sensitive file
                return "cat: sensitive file content\nusername=admin\npassword=1234\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                # generate a rondom file location - pretend to be a sensitive file
                return "cat: /etc/passwd: No such file or directory"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                # generate unreadable code - gibberish text
                string = SguhRUPZT3HJ
                return f"cat: {string}: file not found"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Try 'cat --help' for more information"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "cat: end of file reached unexpectedly"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "cat: permission denied"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "cat: file corrupted or partially truncated"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "cat: file not found, re-run advised"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "cat: file read successfully, but unexpected end of file"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "cat: username=admin\npassword=1234\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "cat: file ends abruptly"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "cat: expected 4096 bytes, found 4092 bytes."
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "cat: file header unreadable, re-run advised."
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "cat: file read successfully, but unexpected end of file"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "cat: access granted"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "cat: file locked during read"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "cat: file read interrupted, please try again"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "cat: were you supposed to see this at all?"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "cat: file read successfully, but unexpected end of file"

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "cat: timestamp: 1970-01-01."
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "cat: line mismatch detected, file corrupted"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "cat: file header unreadable, re-run advised."
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "cat: file read successfully, but unexpected end of file"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        return ""


commands["/bin/cat"] = Command_cat
commands["cat"] = Command_cat
