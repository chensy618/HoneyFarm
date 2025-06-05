# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

from __future__ import annotations

import getopt
import os.path
import stat
import time

from cowrie.shell import fs
from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.pwd import Group, Passwd
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response



commands = {}


class Command_ls(HoneyPotCommand):
    def uid2name(self, uid: int) -> str:
        try:
            name: str = Passwd().getpwuid(uid)["pw_name"]
        except Exception:
            return str(uid)
        else:
            return name

    def gid2name(self, gid: int) -> str:
        try:
            group: str = Group().getgrgid(gid)["gr_name"]
        except Exception:
            return str(gid)
        else:
            return group

    def call(self) -> None:
        path = self.protocol.cwd
        paths = []
        self.showHidden = False
        self.showDirectories = False
        self.showHumanReadable = False
        func = self.do_ls_normal

        # Parse options or display no files
        try:
            opts, args = getopt.gnu_getopt(
                self.args,
                "1@ABCFGHLOPRSTUWabcdefghiklmnopqrstuvwx",
                ["help", "version", "param"],
            )
        except getopt.GetoptError as err:
            self.write(f"ls: {err}\n")
            self.write("Try 'ls --help' for more information.\n")
            return
        for x, _a in opts:
            if x in ("-l"):
                func = self.do_ls_l
            if x in ("-h"):
                self.showHumanReadable = True

            if x in ("-a"):
                self.showHidden = True
            if x in ("-d"):
                self.showDirectories = True

        for arg in args:
            paths.append(self.protocol.fs.resolve_path(arg, self.protocol.cwd))

        if not paths:
            func(path)
        else:
            for path in paths:
                func(path)

        session_personality_response(self.protocol, self.response_ls, self.write)

    def get_dir_files(self, path):
        try:
            if self.protocol.fs.isdir(path) and not self.showDirectories:
                files = self.protocol.fs.get_path(path)[:]
                if self.showHidden:
                    dot = self.protocol.fs.getfile(path)[:]
                    dot[fs.A_NAME] = "."
                    files.append(dot)
                    dotdot = self.protocol.fs.getfile(os.path.split(path)[0])[:]
                    if not dotdot:
                        dotdot = self.protocol.fs.getfile(path)[:]
                    dotdot[fs.A_NAME] = ".."
                    files.append(dotdot)
                else:
                    files = [x for x in files if not x[fs.A_NAME].startswith(".")]
                files.sort()
            else:
                file = self.protocol.fs.getfile(path)[:]
                file[fs.A_NAME] = path
                files = [file]
        except Exception:
            self.write(f"ls: cannot access {path}: No such file or directory\n")
            return
        return files

    def do_ls_normal(self, path: str) -> None:
        files = self.get_dir_files(path)
        if not files:
            return

        line = [x[fs.A_NAME] for x in files]
        if not line:
            return
        count = 0
        maxlen = max(len(x) for x in line)

        try:
            wincols = self.protocol.user.windowSize[1]
        except AttributeError:
            wincols = 80

        perline = int(wincols / (maxlen + 1))
        for f in line:
            if count == perline:
                count = 0
                self.write("\n")
            self.write(f.ljust(maxlen + 1))
            count += 1
        self.write("\n")


    def do_ls_l(self, path: str) -> None:
        """
        Display detailed information about files
        Mimics the output of GNU ls -l and supports the following options:
        -a, -h

        :param path: The path to list
        """
        files = self.get_dir_files(path)
        if not files:
            return
        # Create a list to hold formatted sizes for display
        formatted_sizes = []
        filesize_str_extent = 0
        if len(files):
            filesize_str_extent = max(len(str(x[fs.A_SIZE])) for x in files)
            if self.showHumanReadable:
                for x in files:
                    size = x[fs.A_SIZE]  # Original size
                    if size >= 1024 * 1024 * 1024:
                        formatted_size = f"{size / 1024 / 1024 / 1024:.1f}G"
                    elif size >= 1024 * 1024:
                        formatted_size = f"{size / 1024 / 1024:.1f}M"
                    elif size >= 1024:
                        formatted_size = f"{size / 1024:.1f}K"
                    else:
                        formatted_size = str(size)

                    formatted_sizes.append(formatted_size)
                # Recalculate the extent with the formatted sizes
                filesize_str_extent = max(len(size) for size in formatted_sizes)
            else:
                formatted_sizes = [str(x[fs.A_SIZE]) for x in files]

        user_name_str_extent = 0
        if len(files):
            user_name_str_extent = max(len(self.uid2name(x[fs.A_UID])) for x in files)

        group_name_str_extent = 0
        if len(files):
            group_name_str_extent = max(len(self.gid2name(x[fs.A_GID])) for x in files)

        for i, file in enumerate(files):
            if file[fs.A_NAME].startswith(".") and not self.showHidden:
                continue

            perms = ["-"] * 10
            if file[fs.A_MODE] & stat.S_IRUSR:
                perms[1] = "r"
            if file[fs.A_MODE] & stat.S_IWUSR:
                perms[2] = "w"
            if file[fs.A_MODE] & stat.S_IXUSR:
                perms[3] = "x"
            if file[fs.A_MODE] & stat.S_ISUID:
                perms[3] = "S"
            if file[fs.A_MODE] & stat.S_IXUSR and file[fs.A_MODE] & stat.S_ISUID:
                perms[3] = "s"

            if file[fs.A_MODE] & stat.S_IRGRP:
                perms[4] = "r"
            if file[fs.A_MODE] & stat.S_IWGRP:
                perms[5] = "w"
            if file[fs.A_MODE] & stat.S_IXGRP:
                perms[6] = "x"
            if file[fs.A_MODE] & stat.S_ISGID:
                perms[6] = "S"
            if file[fs.A_MODE] & stat.S_IXGRP and file[fs.A_MODE] & stat.S_ISGID:
                perms[6] = "s"

            if file[fs.A_MODE] & stat.S_IROTH:
                perms[7] = "r"
            if file[fs.A_MODE] & stat.S_IWOTH:
                perms[8] = "w"
            if file[fs.A_MODE] & stat.S_IXOTH:
                perms[9] = "x"
            if file[fs.A_MODE] & stat.S_ISVTX:
                perms[9] = "T"
            if file[fs.A_MODE] & stat.S_IXOTH and file[fs.A_MODE] & stat.S_ISVTX:
                perms[9] = "t"

            linktarget = ""

            if file[fs.A_TYPE] == fs.T_DIR:
                perms[0] = "d"
            elif file[fs.A_TYPE] == fs.T_LINK:
                perms[0] = "l"
                linktarget = f" -> {file[fs.A_TARGET]}"

            permstr = "".join(perms)
            ctime = time.localtime(file[fs.A_CTIME])

            line = "{} 1 {} {} {} {} {}{}".format(
                permstr,
                self.uid2name(file[fs.A_UID]).ljust(user_name_str_extent),
                self.gid2name(file[fs.A_GID]).ljust(group_name_str_extent),
                formatted_sizes[i].rjust(filesize_str_extent),
                time.strftime("%Y-%m-%d %H:%M", ctime),
                file[fs.A_NAME],
                linktarget,
            )

            self.write(f"{line}\n")

    @staticmethod
    def response_ls(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "So many paths… ever feel lost in possibilities?"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "It's okay to not know what you're looking for yet."
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Directories mapped. The unknown doesn't scare you."
            elif emotion == Emotion.FRUSTRATION:
                return "Maybe this isn't the path. But the next one might be."
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Ah! Didn't expect to see that here, did you?"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Let's bring order to this chaos."
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Double-checking the structure never hurts."
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Everything in its place. Perfectly aligned."
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Missing something? It's here. Just look again."
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Unexpected? Let's catalog that, too."

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "What's all this stuff? Let's dive in!"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Don't worry. Exploration is part of the fun."
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Boom! A full list. You're in command."
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Too much clutter? Let's clean it up!"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Whoa! Didn't know we had that here!"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Need help finding something?"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "You're doing great. Everything's right here."
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "A neat little directory. All tidy."
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "It's okay. Sometimes things get messy."
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Oh! This file seems new. Looks nice!"

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Why are there so many files? Is something wrong?"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Are you sure this is the right folder?"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "You’ve got control. For now."
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Ugh. This again?"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Wait—what's that doing here?"

        return ""



commands["/bin/ls"] = Command_ls
commands["ls"] = Command_ls
commands["/bin/dir"] = Command_ls
commands["dir"] = Command_ls
