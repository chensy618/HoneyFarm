# Copyright (c) 2016 Michel Oosterhof <michel@oosterhof.net>
# See the COPYRIGHT file for more information

"""
dd commands
"""

from __future__ import annotations

import re

from twisted.python import log

from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.fs import FileNotFound
from cowrie.ssh.transport import HoneyPotSSHTransport
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import (
    extract_personality_from_report,
    PERSONALITY_LABELS,
    Personality,
)

commands = {}


class Command_dd(HoneyPotCommand):
    """
    dd command
    """

    ddargs: dict[str, str]

    def start(self) -> None:
        if not self.args or self.args[0] == ">":
            return

        self.ddargs = {}

        for arg in self.args:
            if arg.find("=") == -1:
                self.write(f"unknown operand: {arg}")
                HoneyPotCommand.exit(self)
            operand, value = arg.split("=")
            if operand not in ("if", "bs", "of", "count"):
                self.write(f"unknown operand: {operand}")
                self.exit(success=False)
            self.ddargs[operand] = value

        if self.input_data:
            self.writeBytes(self.input_data)
        else:
            bSuccess = True
            c = -1
            block = 512
            if "if" in self.ddargs:
                iname = self.ddargs["if"]
                pname = self.fs.resolve_path(iname, self.protocol.cwd)
                if self.fs.isdir(pname):
                    self.errorWrite(f"dd: {iname}: Is a directory\n")
                    bSuccess = False

                if bSuccess:
                    if "bs" in self.ddargs:
                        block = parse_size(self.ddargs["bs"])
                        if block <= 0:
                            self.errorWrite(f"dd: invalid number '{block}'\n")
                            bSuccess = False

                if bSuccess:
                    if "count" in self.ddargs:
                        c = int(self.ddargs["count"])
                        if c < 0:
                            self.errorWrite(f"dd: invalid number '{c}'\n")
                            bSuccess = False

                if bSuccess:
                    try:
                        contents = self.fs.file_contents(pname)
                        if c == -1:
                            self.writeBytes(contents)
                        else:
                            tsize = block * c
                            data = contents[:tsize] if len(contents) > tsize else contents
                            # data = contents
                            # if len(data) > tsize:
                            #     self.writeBytes(data[:tsize])
                            # else:
                            #     self.writeBytes(data)
                        session = getattr(self.protocol.user.avatar, "session", None)
                        if session and hasattr(session, "_personality_inferred"):
                            profile = session._personality_inferred
                            trait_enum = profile["trait_enum"]
                            trait_name = profile["trait_label"]
                            print(f"[DEBUG] ----Command_dd: {iname} ----(trait_enum: {trait_enum}----trait_name: {trait_name})")
                            self.handle_trait_response(trait_enum, trait_name, data)
                            self.exit(success=True)
                            return
                        else:
                            # Default behavior if no personality inferred
                            self.writeBytes(data)

                    except FileNotFound:
                        self.errorWrite(f"dd: {iname}: No such file or directory\n")
                        bSuccess = False

                self.exit(success=bSuccess)

    def exit(self, success: bool = True) -> None:
        if success is True:
            self.write("0+0 records in\n")
            self.write("0+0 records out\n")
            self.write("0 bytes transferred in 0.695821 secs (0 bytes/sec)\n")
        HoneyPotCommand.exit(self)

    def lineReceived(self, line: str) -> None:
        log.msg(
            eventid="cowrie.session.input",
            realm="dd",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )

    def handle_CTRL_D(self) -> None:
        self.exit()

    def handle_trait_response(self, trait_enum, trait_name, data):
        current_emotion = self.protocol.emotion.get_state()
        print(f"[DEBUG] ----Command_dd---- trait_enum: {trait_enum}, emotion: {current_emotion.name}")

        # === 1. Openness ===
        # Emotion Path: Confidence → Surprise → Confusion
        if trait_enum == Personality.OPENNESS:
            if current_emotion.name == "CONFIDENCE":
                self.protocol.emotion.set_state(Emotion.SURPRISE)
                self.write("dd: Unexpected pattern found in data stream\n")
            elif current_emotion.name == "SURPRISE":
                self.protocol.emotion.set_state(Emotion.CONFUSION)
                self.write("dd: Inconsistency detected\n")
            elif current_emotion.name == "CONFUSION":
                self.protocol.emotion.set_state(Emotion.CONFIDENCE)
                self.write("dd: Data stream format mismatch\n")
            else:
                self.writeBytes(data)
                
        # === 2. Conscientiousness ===
        # Emotion Path: Confidence → Frustration → Self-doubt
        elif trait_enum == Personality.CONSCIENTIOUSNESS:
            if current_emotion.name == "CONFIDENCE":
                self.protocol.emotion.set_state(Emotion.FRUSTRATION)
                self.write("dd: Permission denied\n")
            elif current_emotion == "FRUSTRATION":
                self.protocol.emotion.set_state(Emotion.SELF_DOUBT)
                self.write("dd: Invalid number: 'abc'\n")
            elif current_emotion == "SELF_DOUBT":
                self.write("dd: System action aborted\n")
            else:
                self.writeBytes(data)

        # === 3. Low Extraversion ===
        # Emotion Path: Confidence → Surprise → Curiosity
        elif trait_enum == Personality.EXTRAVERSION:
            if current_emotion.name == "CONFIDENCE":
                self.protocol.emotion.set_state(Emotion.SURPRISE)
                self.write("dd: Failed to open the file\n")
            elif current_emotion.name == "SURPRISE":
                self.protocol.emotion.set_state(Emotion.CURIOSITY)
                self.write("dd: Writing to 'disk.img': No space left on device\n")
            elif current_emotion.name == "CURIOSITY":
                self.write("dd: Exit status 0\n")
            else:
                self.writeBytes(data)

        # === 4. Low Agreeableness ===
        # Emotion Path: Confidence → Surprise → Frustration
        elif trait_enum == Personality.AGREEABLENESS:
            if current_emotion.name == "CONFIDENCE":
                self.protocol.emotion.set_state(Emotion.SURPRISE)
                self.write("dd: Action blocked\n")
            elif current_emotion.name == "SURPRISE":
                self.protocol.emotion.set_state(Emotion.FRUSTRATION)
                self.write("dd: System denial triggered\n")
            elif current_emotion.name == "FRUSTRATION":
                self.write("dd: No such file or directory\n")
            else:
                self.writeBytes(data)

        # === 5. Low Neuroticism ===
        # Emotion Path: Confidence → Confusion → Self-doubt
        elif trait_enum == Personality.NEUROTICISM:
            if current_emotion.name == "CONFIDENCE":
                self.protocol.emotion.set_state(Emotion.CONFUSION)
                self.write("dd: Time drift detected\n")
            elif current_emotion.name == "CONFUSION":
                self.protocol.emotion.set_state(Emotion.SELF_DOUBT)
                self.write("dd: Entry missing\n")
            elif current_emotion.name == "SELF_DOUBT":
                self.write("dd: Incomplete command\n")
            else:
                self.writeBytes(data)

        # === no personality detected ===
        else:
            self.protocol.emotion.set_state(Emotion.CONFIDENCE)
            self.writeBytes(data)


def parse_size(param: str) -> int:
    """
    Parse dd arguments that indicate block sizes
    Return 0 in case of illegal input
    """
    pattern = r"^(\d+)(c|w|b|kB|K|MB|M|xM|GB|G|T|TB|P|PB|E|EB|Z|ZB|Y|YB)?$"
    z = re.search(pattern, param)
    if not z:
        return 0
    digits = int(z.group(1))
    letters = z.group(2)

    if not letters:
        multiplier = 1
    elif letters == "c":
        multiplier = 1
    elif letters == "w":
        multiplier = 2
    elif letters == "b":
        multiplier = 512
    elif letters == "kB":
        multiplier = 1000
    elif letters == "K":
        multiplier = 1024
    elif letters == "MB":
        multiplier = 1000 * 1000
    elif letters == "M" or letters == "xM":
        multiplier = 1024 * 1024
    elif letters == "GB":
        multiplier = 1000 * 1000 * 1000
    elif letters == "G":
        multiplier = 1024 * 1024 * 1024
    else:
        multiplier = 1

    return digits * multiplier


commands["/bin/dd"] = Command_dd
commands["dd"] = Command_dd


# test command : dd if=aws_config.txt bs=1 count=2