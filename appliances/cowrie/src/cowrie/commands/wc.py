# Copyright (c) 2019 Nuno Novais <nuno@noais.me>
# All rights reserved.
# All rights given to Cowrie project

"""
This module contains the wc commnad
"""

from __future__ import annotations

import getopt
import re

from twisted.python import log

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_wc(HoneyPotCommand):
    """
    wc command
    """

    def version(self) -> None:
        self.writeBytes(b"wc (GNU coreutils) 8.30\n")
        self.writeBytes(b"Copyright (C) 2018 Free Software Foundation, Inc.\n")
        self.writeBytes(
            b"License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.\n"
        )
        self.writeBytes(
            b"This is free software: you are free to change and redistribute it.\n"
        )
        self.writeBytes(b"There is NO WARRANTY, to the extent permitted by law.\n")
        self.writeBytes(b"\n")
        self.writeBytes(b"Written by Paul Rubin and David MacKenzie.\n")

    def help(self) -> None:
        self.writeBytes(b"Usage: wc [OPTION]... [FILE]...\n")
        self.writeBytes(
            b"Print newline, word, and byte counts for each FILE, and a total line if\n"
        )
        self.writeBytes(
            b"more than one FILE is specified.  A word is a non-zero-length sequence of\n"
        )
        self.writeBytes(b"characters delimited by white space.\n")
        self.writeBytes(b"\n")
        self.writeBytes(b"With no FILE, or when FILE is -, read standard input.\n")
        self.writeBytes(b"\n")
        self.writeBytes(
            b"The options below may be used to select which counts are printed, always in\n"
        )
        self.writeBytes(
            b"the following order: newline, word, character, byte, maximum line length.\n"
        )
        self.writeBytes(b"\t-c\tprint the byte counts\n")
        self.writeBytes(b"\t-m\tprint the character counts\n")
        self.writeBytes(b"\t-l\tprint the newline counts\n")
        self.writeBytes(b"\t-w\tprint the word counts\n")
        self.writeBytes(b"\t-h\tdisplay this help and exit\n")
        self.writeBytes(b"\t-v\toutput version information and exit\n")

    def wc_get_contents(self, filename: str, optlist: list[tuple[str, str]]) -> None:
        try:
            contents = self.fs.file_contents(filename)
            self.wc_application(contents, optlist)
        except Exception:
            self.errorWrite(f"wc: {filename}: No such file or directory\n")

    def wc_application(self, contents: bytes, optlist: list[tuple[str, str]]) -> None:
        for opt, _arg in optlist:
            if opt == "-l":
                contentsplit = contents.split(b"\n")
                self.write(f"{len(contentsplit) - 1}\n")
            elif opt == "-w":
                contentsplit = re.sub(b" +", b" ", contents.strip(b"\n").strip()).split(
                    b" "
                )
                self.write(f"{len(contentsplit)}\n")
            elif opt == "-m" or opt == "-c":
                self.write(f"{len(contents)}\n")
            elif opt == "-v":
                self.version()
            else:
                self.help()

    def start(self) -> None:
        if not self.args:
            self.exit()
            return

        if self.args[0] == ">":
            pass
        else:
            try:
                optlist, args = getopt.getopt(self.args, "cmlLwhv")
            except getopt.GetoptError as err:
                self.errorWrite(f"wc: invalid option -- {err.opt}\n")
                self.help()
                self.exit()
                return
            for opt in optlist:
                if opt[0] == "-v":
                    self.version()
                    self.exit()
                    return
                if opt[0] == "-h":
                    self.help()
                    self.exit()
                    return

        if not self.input_data:
            files = self.check_arguments("wc", args[1:])
            for pname in files:
                self.wc_get_contents(pname, optlist)
        else:
            self.wc_application(self.input_data, optlist)
            session_personality_response(self.protocol, self.response_wc, self.write)

        self.exit()

    def lineReceived(self, line: str) -> None:
        log.msg(
            eventid="cowrie.command.input",
            realm="wc",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )

    def handle_CTRL_D(self) -> None:
        self.exit()

    @staticmethod
    def response_wc(protocol, trait, emotion):

        if trait.name == "OPENNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.CURIOSITY)
                return "Ever wonder what counts truly matter?"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Every word. Every line. They all add up."
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Simple metrics, powerful meaning."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "The file may be noisy, but your focus isn't."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Wow, that many lines?"

        elif trait.name == "CONSCIENTIOUSNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Let's organize this. One count at a time."
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Data integrity verified."
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Counts aligned. Mission complete."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Keep counting, keep improving."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Unexpected length? Worth a closer look."

        elif trait.name == "EXTRAVERSION":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Let's break this file down together!"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Words are nothing without your voice!"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Boom! Counted like a pro!"
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Shake it off. It's just a file."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Didn't see that coming, huh?"

        elif trait.name == "AGREEABLENESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Need help reading those stats?"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "One word at a time, we're getting there."
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "That looks tidy and nice."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Calm and steady. Let's count again."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Surprising, right? Let's check again just to be sure."

        elif trait.name == "NEUROTICISM":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "What if we missed something…?"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Were those counts right? Should we double check?"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Alright… but something still feels off."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "I messed it up, didn't I?"
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Wait… that can't be right… right?"

        return ""


commands["/usr/bin/wc"] = Command_wc
commands["/bin/wc"] = Command_wc
commands["wc"] = Command_wc
