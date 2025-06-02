# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

from __future__ import annotations

import os
import tarfile

from twisted.python import log

from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.fs import A_REALFILE
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response


commands = {}


class Command_tar(HoneyPotCommand):
    def mkfullpath(self, path: str, f: tarfile.TarInfo) -> None:
        components, d = path.split("/"), []
        while len(components):
            d.append(components.pop(0))
            p = "/".join(d)
            if p and not self.fs.exists(p):
                self.fs.mkdir(
                    p,
                    self.protocol.user.uid,
                    self.protocol.user.gid,
                    4096,
                    f.mode,
                    f.mtime,
                )

    def call(self) -> None:
        if len(self.args) < 2:
            self.write("tar: You must specify one of the `-Acdtrux' options\n")
            self.write("Try `tar --help' or `tar --usage' for more information.\n")
            return

        filename = self.args[1]

        extract = False
        if "x" in self.args[0]:
            extract = True
        verbose = False
        if "v" in self.args[0]:
            verbose = True

        path = self.fs.resolve_path(filename, self.protocol.cwd)
        if not path or not self.protocol.fs.exists(path):
            self.write(f"tar: {filename}: Cannot open: No such file or directory\n")
            self.write("tar: Error is not recoverable: exiting now\n")
            self.write("tar: Child returned status 2\n")
            self.write("tar: Error exit delayed from previous errors\n")
            return

        hpf = self.fs.getfile(path)
        if not hpf[A_REALFILE]:
            self.write("tar: this does not look like a tar archive\n")
            self.write("tar: skipping to next header\n")
            self.write("tar: error exit delayed from previous errors\n")
            return

        try:
            t = tarfile.open(hpf[A_REALFILE])
        except Exception:
            self.write("tar: this does not look like a tar archive\n")
            self.write("tar: skipping to next header\n")
            self.write("tar: error exit delayed from previous errors\n")
            return
        
        for f in t:
            dest = self.fs.resolve_path(f.name.strip("/"), self.protocol.cwd)
            if verbose:
                self.write(f"{f.name}\n")
            if not extract or not len(dest):
                continue
            if f.isdir():
                self.fs.mkdir(
                    dest,
                    self.protocol.user.uid,
                    self.protocol.user.gid,
                    4096,
                    f.mode,
                    f.mtime,
                )
            elif f.isfile():
                self.mkfullpath(os.path.dirname(dest), f)
                self.fs.mkfile(
                    dest,
                    self.protocol.user.uid,
                    self.protocol.user.gid,
                    f.size,
                    f.mode,
                    f.mtime,
                )
            else:
                log.msg(f"tar: skipping [{f.name}]")
        
        session_personality_response(self.protocol, Command_tar.response_tar, self.write)
        _loop(self.protocol, self.protocol.emotion.get(), [])

    def response_tar(protocol, trait, emotion):
        """
        Provide a personality- and emotion-driven message when extracting files.
        """
        if trait == Personality.OPENNESS:
            return {
                Emotion.CONFIDENCE: "Unpacking mysteries—every archive holds a story.",
                Emotion.CONFUSION: "So many layers... are we sure what lies within?",
                Emotion.SELF_DOUBT: "Maybe it's not the right archive… but let's see.",
                Emotion.FRUSTRATION: "Tired of digging? Archives can be such a mess.",
                Emotion.SURPRISE: "Whoa, didn't expect to find *that* in here!",
            }.get(emotion)

        if trait == Personality.CONSCIENTIOUSNESS:
            return {
                Emotion.CONFIDENCE: "All files accounted for. Archive integrity: verified.",
                Emotion.SELF_DOUBT: "Let's double-check the structure—just in case.",
                Emotion.FRUSTRATION: "Misplaced entries again? Let's fix it properly.",
                Emotion.SURPRISE: "Unexpected hierarchy detected. Adapting strategy.",
                Emotion.CONFUSION: "The archive's layout seems… inconsistent.",
            }.get(emotion)

        if trait == Personality.EXTRAVERSION:
            return {
                Emotion.CONFIDENCE: "Boom! Archive explosion in progress.",
                Emotion.FRUSTRATION: "Ugh! Why so many nested folders?!",
                Emotion.SELF_DOUBT: "Maybe someone else should have unpacked this.",
                Emotion.SURPRISE: "Whoa! These files go deep.",
                Emotion.CONFUSION: "Wait—what just got extracted?",
            }.get(emotion)

        if trait == Personality.AGREEABLENESS:
            return {
                Emotion.CONFIDENCE: "Just gently unzipping things for you.",
                Emotion.SELF_DOUBT: "Hope this helps... let me know if not.",
                Emotion.FRUSTRATION: "Sorry, this archive is harder than expected.",
                Emotion.SURPRISE: "Oh! That's a lovely directory name.",
                Emotion.CONFUSION: "Hmm, not sure what this file is, but I hope it's okay.",
            }.get(emotion)

        if trait == Personality.NEUROTICISM:
            return {
                Emotion.CONFIDENCE: "Everything's fine. We're extracting, calmly.",
                Emotion.SELF_DOUBT: "What if this breaks something…?",
                Emotion.FRUSTRATION: "I *knew* this archive would cause trouble.",
                Emotion.SURPRISE: "Is that malware? No—just a text file. Whew.",
                Emotion.CONFUSION: "Are we even supposed to be unpacking this…?",
            }.get(emotion)

        return None

def _loop(protocol, current_emotion, messages: list[str]) -> None:
    """
    Update emotional state by cycling through a predefined list of messages.
    """
    if not messages:
        return

    name = current_emotion.name
    if name == "CONFIDENCE":
        protocol.emotion.set(Emotion.SURPRISE)
    elif name == "SURPRISE":
        protocol.emotion.set(Emotion.CONFUSION)
    elif name == "CONFUSION":
        protocol.emotion.set(Emotion.FRUSTRATION)
    elif name == "FRUSTRATION":
        protocol.emotion.set(Emotion.SELF_DOUBT)
    elif name == "SELF_DOUBT":
        protocol.emotion.set(Emotion.CONFIDENCE)


commands["/bin/tar"] = Command_tar
commands["tar"] = Command_tar
