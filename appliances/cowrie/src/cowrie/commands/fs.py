# Copyright (c) 2010 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information


"""
Filesystem related commands
"""

from __future__ import annotations

import copy
import getopt
import os.path
import re

from twisted.python import log

from cowrie.shell import fs
from cowrie.shell.command import HoneyPotCommand
from typing import TYPE_CHECKING
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

if TYPE_CHECKING:
    from collections.abc import Callable

commands: dict[str, Callable] = {}

# def session_personality_response(protocol, response_fn, write_fn):
#     """
#     if user session exists personality, then call corresponding response function and output
    
#     :param protocol: (self.protocol)
#     :param response_fn: such as Command_grep.response_grep
#     :param write_fn: self_write or cmdstack[-1].write
#     """
#     session = getattr(protocol.user.avatar, "session", None)
#     if not (session and hasattr(session, "_personality_inferred")):
#         return

#     profile = session._personality_inferred
#     trait_enum = profile["trait_enum"]
#     emotion = protocol.emotion.get_state()

#     msg = response_fn(protocol, trait_enum, emotion)
#     if msg:
#         write_fn(msg)

class Command_grep(HoneyPotCommand):
    """
    grep command
    """

    def grep_get_contents(self, filename: str, match: str) -> None:
        try:
            contents = self.fs.file_contents(filename)
            self.grep_application(contents, match)
        except Exception:
            self.errorWrite(f"grep: {filename}: No such file or directory\n")

    def grep_application(self, contents: bytes, match: str) -> None:
        bmatch = os.path.basename(match).replace('"', "").encode("utf8")
        matches = re.compile(bmatch)
        contentsplit = contents.split(b"\n")
        for line in contentsplit:
            if matches.search(line):
                self.writeBytes(line + b"\n")

    def help(self) -> None:
        self.writeBytes(
            b"usage: grep [-abcDEFGHhIiJLlmnOoPqRSsUVvwxZ] [-A num] [-B num] [-C[num]]\n"
        )
        self.writeBytes(
            b"\t[-e pattern] [-f file] [--binary-files=value] [--color=when]\n"
        )
        self.writeBytes(
            b"\t[--context[=num]] [--directories=action] [--label] [--line-buffered]\n"
        )
        self.writeBytes(b"\t[--null] [pattern] [file ...]\n")

    def start(self) -> None:
        if not self.args:
            self.help()
            self.exit()
            return

        self.n = 10
        if self.args[0] == ">":
            pass
        else:
            try:
                optlist, args = getopt.getopt(
                    self.args, "abcDEFGHhIiJLlmnOoPqRSsUVvwxZA:B:C:e:f:"
                )
            except getopt.GetoptError as err:
                self.errorWrite(f"grep: invalid option -- {err.opt}\n")
                self.help()
                self.exit()
                return

            for opt, _arg in optlist:
                if opt == "-h":
                    self.help()

        if not self.input_data:
            files = self.check_arguments("grep", args[1:])
            for pname in files:
                self.grep_get_contents(pname, args[0])
        else:
            self.grep_application(self.input_data, args[0])

        # session = getattr(self.protocol.user.avatar, "session", None)
        # if not (session and hasattr(session, "_personality_inferred")):
        #     return  # no profile, skip extra response
        # else:
        #     profile = session._personality_inferred
        #     trait_enum = profile["trait_enum"]
        #     trait_name = profile["trait_label"]
        #     emotion = self.protocol.emotion.get_state()
        #     msg = Command_grep.response_grep(self.protocol, trait_enum, emotion)
        #     if msg:
        #         self.write(msg)
        session_personality_response(self.protocol, Command_grep.response_grep, self.write)

        self.exit()

    def lineReceived(self, line: str) -> None:
        log.msg(
            eventid="cowrie.command.input",
            realm="grep",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )

    def handle_CTRL_D(self) -> None:
        self.exit()

    def response_grep(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            return _cycle(protocol, emotion, [
                "[grep] Huh? That pattern actually exists.",
                "[grep] Found it... fascinating!",
                "[grep] There's more than I expected..."
            ])
        elif trait == Personality.CONSCIENTIOUSNESS:
            return _cycle(protocol, emotion, [
                "[grep] Pattern doesn’t match structure.",
                "[grep] Something feels inconsistent.",
                "[grep] What if this is the wrong pattern?"
            ])
        elif trait == Personality.LOW_EXTRAVERSION:
            return _cycle(protocol, emotion, [
                "[grep] Whoa! That’s a loud match.",
                "[grep] Let’s explore more files!",
                "[grep] Try deeper matching."
            ])
        elif trait == Personality.LOW_AGREEABLENESS:
            return _cycle(protocol, emotion, [
                "[grep] Glad to help!",
                "[grep] Hmm... too many results, might be confusing.",
                "[grep] Sorry, this got messy."
            ])
        elif trait == Personality.LOW_NEUROTICISM:
            return _cycle(protocol, emotion, [
                "[grep] Was that really there?",
                "[grep] Unexpected line order.",
                "[grep] Aborting match logic."
            ])
        return ""


commands["/bin/grep"] = Command_grep
commands["grep"] = Command_grep
commands["/bin/egrep"] = Command_grep
commands["/bin/fgrep"] = Command_grep


class Command_tail(HoneyPotCommand):
    """
    tail command
    """

    n: int = 10

    def tail_get_contents(self, filename: str) -> None:
        try:
            contents = self.fs.file_contents(filename)
            self.tail_application(contents)
        except Exception:
            self.errorWrite(
                f"tail: cannot open `{filename}' for reading: No such file or directory\n"
            )

    def tail_application(self, contents: bytes) -> None:
        contentsplit = contents.split(b"\n")
        lines = int(len(contentsplit))
        if lines < self.n:
            self.n = lines - 1
        i = 0
        for j in range((lines - self.n - 1), lines):
            self.writeBytes(contentsplit[j])
            if i < self.n:
                self.write("\n")
            i += 1

    def start(self) -> None:
        if not self.args or self.args[0] == ">":
            return
        else:
            try:
                optlist, args = getopt.getopt(self.args, "n:")
            except getopt.GetoptError as err:
                self.errorWrite(f"tail: invalid option -- '{err.opt}'\n")
                self.exit()
                return

            for opt in optlist:
                if opt[0] == "-n":
                    if not opt[1].isdigit():
                        self.errorWrite(f"tail: illegal offset -- {opt[1]}\n")
                    else:
                        self.n = int(opt[1])
        if not self.input_data:
            files = self.check_arguments("tail", args)
            for pname in files:
                self.tail_get_contents(pname)
        else:
            self.tail_application(self.input_data)

        session_personality_response(self.protocol, Command_tail.response_tail, self.write)
        self.exit()

    def lineReceived(self, line: str) -> None:
        log.msg(
            eventid="cowrie.command.input",
            realm="tail",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )

    def handle_CTRL_D(self) -> None:
        self.exit()

    def response_tail(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            return _cycle(protocol, emotion, [
                "[tail] The ending is quite revealing.",
                "[tail] Interesting finale...",
                "[tail] Wanna see how it builds up next?"
            ])
        elif trait == Personality.CONSCIENTIOUSNESS:
            return _cycle(protocol, emotion, [
                "[tail] Output truncated improperly.",
                "[tail] Are these logs incomplete?",
                "[tail] Shouldn't we double-check consistency?"
            ])
        elif trait == Personality.LOW_EXTRAVERSION:
            return _cycle(protocol, emotion, [
                "[tail] The last bits are intense!",
                "[tail] What happened just now?",
                "[tail] Should we tail more?"
            ])
        elif trait == Personality.LOW_AGREEABLENESS:
            return _cycle(protocol, emotion, [
                "[tail] Showing what you asked.",
                "[tail] That was unexpected.",
                "[tail] Ugh, can't keep up with the stream."
            ])
        elif trait == Personality.LOW_NEUROTICISM:
            return _cycle(protocol, emotion, [
                "[tail] Log lines feel off.",
                "[tail] Hmm, timestamps don’t align...",
                "[tail] Something’s broken."
            ])
        return ""

commands["/bin/tail"] = Command_tail
commands["/usr/bin/tail"] = Command_tail
commands["tail"] = Command_tail


class Command_head(HoneyPotCommand):
    """
    head command
    """

    linecount: int = 10
    bytecount: int = 0

    def head_application(self, contents: bytes) -> None:
        if self.bytecount:
            self.writeBytes(contents[: self.bytecount])
        elif self.linecount:
            linesplit = contents.split(b"\n")
            for line in linesplit[: self.linecount]:
                self.writeBytes(line + b"\n")

    def head_get_file_contents(self, filename: str) -> None:
        try:
            contents = self.fs.file_contents(filename)
            self.head_application(contents)
        except fs.FileNotFound:
            self.errorWrite(
                f"head: cannot open `{filename}' for reading: No such file or directory\n"
            )

    def start(self) -> None:
        self.lines: int = 10
        self.bytecount: int = 0
        if not self.args or self.args[0] == ">":
            return
        else:
            try:
                optlist, args = getopt.getopt(self.args, "c:n:")
            except getopt.GetoptError as err:
                self.errorWrite(f"head: invalid option -- '{err.opt}'\n")
                self.exit()
                return

            for opt in optlist:
                if opt[0] == "-n":
                    if not opt[1].isdigit():
                        self.errorWrite(f"head: invalid number of lines: `{opt[1]}`\n")
                    else:
                        self.linecount = int(opt[1])
                        self.bytecount = 0
                elif opt[0] == "-c":
                    if not opt[1].isdigit():
                        self.errorWrite(f"head: invalid number of bytes: `{opt[1]}`\n")
                    else:
                        self.bytecount = int(opt[1])
                        self.linecount = 0

        if not self.input_data:
            files = self.check_arguments("head", args)
            for pname in files:
                self.head_get_file_contents(pname)
        else:
            self.head_application(self.input_data)

        session_personality_response(self.protocol, Command_head.response_head, self.write)

        self.exit()

    def lineReceived(self, line: str) -> None:
        log.msg(
            eventid="cowrie.command.input",
            realm="head",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )

    def handle_CTRL_D(self) -> None:
        self.exit()

    def response_head(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            return _cycle(protocol, emotion, [
                "[head] Fascinating start.",
                "[head] Unexpected first lines.",
                "[head] What lies below that..."
            ])
        elif trait == Personality.CONSCIENTIOUSNESS:
            return _cycle(protocol, emotion, [
                "[head] Beginning lacks clarity.",
                "[head] Format not following expectations.",
                "[head] We might’ve misread the structure."
            ])
        elif trait == Personality.LOW_EXTRAVERSION:
            return _cycle(protocol, emotion, [
                "[head] That start is something!",
                "[head] Wow—look at that header.",
                "[head] Digging further?"
            ])
        elif trait == Personality.LOW_AGREEABLENESS:
            return _cycle(protocol, emotion, [
                "[head] Sure! Top lines ready.",
                "[head] Something looks... odd.",
                "[head] Maybe we shouldn’t be reading this."
            ])
        elif trait == Personality.LOW_NEUROTICISM:
            return _cycle(protocol, emotion, [
                "[head] These lines don’t feel right.",
                "[head] Inconsistent start detected.",
                "[head] I don’t trust this file."
            ])
        return ""



commands["/bin/head"] = Command_head
commands["/usr/bin/head"] = Command_head
commands["head"] = Command_head


class Command_cd(HoneyPotCommand):
    """
    cd command
    """

    def call(self) -> None:
        if not self.args or self.args[0] == "~":
            pname = self.protocol.user.avatar.home
        else:
            pname = self.args[0]
        try:
            newpath = self.fs.resolve_path(pname, self.protocol.cwd)
            inode = self.fs.getfile(newpath)
        except Exception:
            inode = None
        if pname == "-":
            self.errorWrite("bash: cd: OLDPWD not set\n")
            return
        if inode is None or inode is False:
            self.errorWrite(f"bash: cd: {pname}: No such file or directory\n")
            return
        if inode[fs.A_TYPE] != fs.T_DIR:
            self.errorWrite(f"bash: cd: {pname}: Not a directory\n")
            return
        self.protocol.cwd = newpath

        # session = getattr(self.protocol.user.avatar, "session", None)
        # if not (session and hasattr(session, "_personality_inferred")):
        #     return  # no profile, skip extra response
        # else:
        #     profile = session._personality_inferred
        #     trait_enum = profile["trait_enum"]
        #     trait_name = profile["trait_label"]
        #     emotion = self.protocol.emotion.get_state()
        #     msg = Command_cd.response_cd(self.protocol, trait_enum, emotion)
        #     if msg:
        #         self.write(msg)
        session_personality_response(self.protocol, Command_cd.response_cd, self.write)

    def response_cd(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            return _cycle(protocol, emotion, [
                "[cd] Ah, new ground to explore!",
                "[cd] Interesting location.",
                "[cd] What’s inside here?"
            ])
        elif trait == Personality.CONSCIENTIOUSNESS:
            return _cycle(protocol, emotion, [
                "[cd] Directory hierarchy not aligned.",
                "[cd] Is this even structured right?",
                "[cd] Uncertain about this transition."
            ])
        elif trait == Personality.LOW_EXTRAVERSION:
            return _cycle(protocol, emotion, [
                "[cd] Woo! Jumping in.",
                "[cd] Whoa, funky path!",
                "[cd] Let's snoop around."
            ])
        elif trait == Personality.LOW_AGREEABLENESS:
            return _cycle(protocol, emotion, [
                "[cd] Moving where you want.",
                "[cd] Oops, got lost!",
                "[cd] This place feels restricted."
            ])
        elif trait == Personality.LOW_NEUROTICISM:
            return _cycle(protocol, emotion, [
                "[cd] This isn’t where we should be.",
                "[cd] Path seems wrong.",
                "[cd] Better go back."
            ])
        return ""

commands["cd"] = Command_cd


class Command_rm(HoneyPotCommand):
    """
    rm command
    """

    def help(self) -> None:
        self.write(
            """Usage: rm [OPTION]... [FILE]...
Remove (unlink) the FILE(s).

 -f, --force           ignore nonexistent files and arguments, never prompt
 -i                    prompt before every removal
 -I                    prompt once before removing more than three files, or
                         when removing recursively; less intrusive than -i,
                         while still giving protection against most mistakes
      --interactive[=WHEN]  prompt according to WHEN: never, once (-I), or
                         always (-i); without WHEN, prompt always
      --one-file-system  when removing a hierarchy recursively, skip any
                         directory that is on a file system different from
                         that of the corresponding command line argument
      --no-preserve-root  do not treat '/' specially
      --preserve-root   do not remove '/' (default)
 -r, -R, --recursive   remove directories and their contents recursively
 -d, --dir             remove empty directories
 -v, --verbose         explain what is being done
     --help     display this help and exit
     --version  output version information and exit

By default, rm does not remove directories.  Use the --recursive (-r or -R)
option to remove each listed directory, too, along with all of its contents.

To remove a file whose name starts with a '-', for example '-foo',
use one of these commands:
 rm -- -foo

 rm ./-foo

Note that if you use rm to remove a file, it might be possible to recover
some of its contents, given sufficient expertise and/or time.  For greater
assurance that the contents are truly unrecoverable, consider using shred.

GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
Full documentation at: <http://www.gnu.org/software/coreutils/rm>
or available locally via: info '(coreutils) rm invocation'\n"""
        )

    def paramError(self) -> None:
        self.errorWrite("Try 'rm --help' for more information\n")

    def call(self) -> None:
        recursive = False
        force = False
        verbose = False
        if not self.args:
            self.errorWrite("rm: missing operand\n")
            self.paramError()
            return

        try:
            optlist, args = getopt.gnu_getopt(
                self.args, "rTfvh", ["help", "recursive", "force", "verbose"]
            )
        except getopt.GetoptError as err:
            self.errorWrite(f"rm: invalid option -- '{err.opt}'\n")
            self.paramError()
            self.exit()
            return

        for o, _a in optlist:
            if o in ("--recursive", "-r", "-R"):
                recursive = True
            elif o in ("--force", "-f"):
                force = True
            elif o in ("--verbose", "-v"):
                verbose = True
            elif o in ("--help", "-h"):
                self.help()
                return

        for f in args:
            pname = self.fs.resolve_path(f, self.protocol.cwd)
            try:
                # verify path to file exists
                directory = self.fs.get_path("/".join(pname.split("/")[:-1]))
                # verify that the file itself exists
                self.fs.get_path(pname)
            except (IndexError, fs.FileNotFound):
                if not force:
                    self.errorWrite(
                        f"rm: cannot remove `{f}': No such file or directory\n"
                    )
                continue
            basename = pname.split("/")[-1]
            for i in directory[:]:
                if i[fs.A_NAME] == basename:
                    if i[fs.A_TYPE] == fs.T_DIR and not recursive:
                        self.errorWrite(
                            f"rm: cannot remove `{i[fs.A_NAME]}': Is a directory\n"
                        )
                    else:
                        directory.remove(i)
                        if verbose:
                            if i[fs.A_TYPE] == fs.T_DIR:
                                self.write(f"removed directory '{i[fs.A_NAME]}'\n")
                            else:
                                self.write(f"removed '{i[fs.A_NAME]}'\n")

        session_personality_response(self.protocol, Command_rm.response_rm, self.write)

    def response_rm(protocol, trait, emotion):
        return _cycle(protocol, emotion, {
            Personality.OPENNESS: ["[rm] That deletion was... bold.", "[rm] Whoa! You meant to remove that?", "[rm] Want to see what’s left?"],
            Personality.CONSCIENTIOUSNESS: ["[rm] Deletion conflicts with retention policy.", "[rm] Too hasty. Could be unsafe.", "[rm] Are you sure we should've done that?"],
            Personality.LOW_EXTRAVERSION: ["[rm] Gone! Fast and fun!", "[rm] I love cleanup jobs.", "[rm] What’s next to destroy?"],
            Personality.LOW_AGREEABLENESS: ["[rm] Sure, gone now.", "[rm] Wait! That seemed important.", "[rm] I regret that... sorry."],
            Personality.LOW_NEUROTICISM: ["[rm] No turning back.", "[rm] Deleted something… hope it’s fine.", "[rm] Oops."]
        }.get(trait, []))

commands["/bin/rm"] = Command_rm
commands["rm"] = Command_rm


class Command_cp(HoneyPotCommand):
    """
    cp command
    """

    def call(self) -> None:
        if not len(self.args):
            self.errorWrite("cp: missing file operand\n")
            self.errorWrite("Try `cp --help' for more information.\n")
            return
        try:
            optlist, args = getopt.gnu_getopt(self.args, "-abdfiHlLPpRrsStTuvx")
        except getopt.GetoptError:
            self.errorWrite("Unrecognized option\n")
            return
        recursive = False
        for opt in optlist:
            if opt[0] in ("-r", "-a", "-R"):
                recursive = True

        def resolv(pname: str) -> str:
            rsv: str = self.fs.resolve_path(pname, self.protocol.cwd)
            return rsv

        if len(args) < 2:
            self.errorWrite(
                f"cp: missing destination file operand after `{self.args[0]}'\n"
            )
            self.errorWrite("Try `cp --help' for more information.\n")
            return
        sources, dest = args[:-1], args[-1]
        if len(sources) > 1 and not self.fs.isdir(resolv(dest)):
            self.errorWrite(f"cp: target `{dest}' is not a directory\n")
            return

        if dest[-1] == "/" and not self.fs.exists(resolv(dest)) and not recursive:
            self.errorWrite(
                f"cp: cannot create regular file `{dest}': Is a directory\n"
            )
            return

        if self.fs.isdir(resolv(dest)):
            isdir = True
        else:
            isdir = False
            parent = os.path.dirname(resolv(dest))
            if not self.fs.exists(parent):
                self.errorWrite(
                    "cp: cannot create regular file "
                    + f"`{dest}': No such file or directory\n"
                )
                return

        for src in sources:
            if not self.fs.exists(resolv(src)):
                self.errorWrite(f"cp: cannot stat `{src}': No such file or directory\n")
                continue
            if not recursive and self.fs.isdir(resolv(src)):
                self.errorWrite(f"cp: omitting directory `{src}'\n")
                continue
            s = copy.deepcopy(self.fs.getfile(resolv(src)))
            if isdir:
                directory = self.fs.get_path(resolv(dest))
                outfile = os.path.basename(src)
            else:
                directory = self.fs.get_path(os.path.dirname(resolv(dest)))
                outfile = os.path.basename(dest.rstrip("/"))
            if outfile in [x[fs.A_NAME] for x in directory]:
                directory.remove(next(x for x in directory if x[fs.A_NAME] == outfile))
            s[fs.A_NAME] = outfile
            directory.append(s)
        
        session_personality_response(self.protocol, Command_cp.response_cp, self.write)

    def response_cp(protocol, trait, emotion):
        return _cycle(protocol, emotion, {
            Personality.OPENNESS: ["[cp] Duplicating artfully.", "[cp] That’s a unique destination.", "[cp] Do you want to experiment with the copy?"],
            Personality.CONSCIENTIOUSNESS: ["[cp] File alignment failed.", "[cp] Naming convention mismatch.", "[cp] Is this path structurally valid?"],
            Personality.LOW_EXTRAVERSION: ["[cp] Copied! Let’s move on!", "[cp] This place needs more stuff.", "[cp] Next copy spree?"],
            Personality.LOW_AGREEABLENESS: ["[cp] Glad to help.", "[cp] Oops, overwrote something?", "[cp] Sorry, should’ve asked..."],
            Personality.LOW_NEUROTICISM: ["[cp] Copy operation unclear.", "[cp] I think we missed something.", "[cp] Might’ve corrupted it."]
        }.get(trait, []))


commands["/bin/cp"] = Command_cp
commands["cp"] = Command_cp


class Command_mv(HoneyPotCommand):
    """
    mv command
    """

    def call(self) -> None:
        if not len(self.args):
            self.errorWrite("mv: missing file operand\n")
            self.errorWrite("Try `mv --help' for more information.\n")
            return

        try:
            optlist, args = getopt.gnu_getopt(self.args, "-bfiStTuv")
        except getopt.GetoptError:
            self.errorWrite("Unrecognized option\n")
            return

        def resolv(pname: str) -> str:
            rsv: str = self.fs.resolve_path(pname, self.protocol.cwd)
            return rsv

        if len(args) < 2:
            self.errorWrite(
                f"mv: missing destination file operand after `{self.args[0]}'\n"
            )
            self.errorWrite("Try `mv --help' for more information.\n")
            return
        sources, dest = args[:-1], args[-1]
        if len(sources) > 1 and not self.fs.isdir(resolv(dest)):
            self.errorWrite(f"mv: target `{dest}' is not a directory\n")
            return

        if dest[-1] == "/" and not self.fs.exists(resolv(dest)) and len(sources) != 1:
            self.errorWrite(
                f"mv: cannot create regular file `{dest}': Is a directory\n"
            )
            return

        if self.fs.isdir(resolv(dest)):
            isdir = True
        else:
            isdir = False
            parent = os.path.dirname(resolv(dest))
            if not self.fs.exists(parent):
                self.errorWrite(
                    "mv: cannot create regular file "
                    + f"`{dest}': No such file or directory\n"
                )
                return

        for src in sources:
            if not self.fs.exists(resolv(src)):
                self.errorWrite(f"mv: cannot stat `{src}': No such file or directory\n")
                continue
            s = self.fs.getfile(resolv(src))
            if isdir:
                directory = self.fs.get_path(resolv(dest))
                outfile = os.path.basename(src)
            else:
                directory = self.fs.get_path(os.path.dirname(resolv(dest)))
                outfile = os.path.basename(dest)
            if directory != os.path.dirname(resolv(src)):
                s[fs.A_NAME] = outfile
                directory.append(s)
                sdir = self.fs.get_path(os.path.dirname(resolv(src)))
                sdir.remove(s)
            else:
                s[fs.A_NAME] = outfile

        session_personality_response(self.protocol, Command_mv.response_mv, self.write)

    def response_mv(protocol, trait, emotion):
        return _cycle(protocol, emotion, {
            Personality.OPENNESS: ["[mv] Bold rearrangement.", "[mv] What’s the idea behind this rename?", "[mv] Let’s experiment."],
            Personality.CONSCIENTIOUSNESS: ["[mv] Violates file structure assumptions.", "[mv] Unexpected overwrite risk.", "[mv] Better verify this move."],
            Personality.LOW_EXTRAVERSION: ["[mv] Whee! File on the move!", "[mv] Let’s reshuffle everything.", "[mv] Try renaming more?"],
            Personality.LOW_AGREEABLENESS: ["[mv] Got it.", "[mv] That may confuse future users.", "[mv] I don’t like where this went."],
            Personality.LOW_NEUROTICISM: ["[mv] Path ambiguity detected.", "[mv] Untracked rename behavior.", "[mv] Rollback advised."]
        }.get(trait, []))


commands["/bin/mv"] = Command_mv
commands["mv"] = Command_mv


class Command_mkdir(HoneyPotCommand):
    """
    mkdir command
    """

    def call(self) -> None:
        for f in self.args:
            pname = self.fs.resolve_path(f, self.protocol.cwd)
            if self.fs.exists(pname):
                self.errorWrite(f"mkdir: cannot create directory `{f}': File exists\n")
                return
            try:
                self.fs.mkdir(
                    pname, self.protocol.user.uid, self.protocol.user.gid, 4096, 16877
                )
            except fs.FileNotFound:
                self.errorWrite(
                    f"mkdir: cannot create directory `{f}': No such file or directory\n"
                )
            return

        session_personality_response(self.protocol, Command_mkdir.response_mkdir, self.write)

    def response_mkdir(protocol, trait, emotion):
        return _cycle(protocol, emotion, {
            Personality.OPENNESS: ["[mkdir] New container for thoughts.", "[mkdir] This space has potential.", "[mkdir] Imagine what could go in here!"],
            Personality.CONSCIENTIOUSNESS: ["[mkdir] Name violates expected hierarchy.", "[mkdir] Already exists? Unacceptable.", "[mkdir] Double-check your directory tree."],
            Personality.LOW_EXTRAVERSION: ["[mkdir] More places to stash files!", "[mkdir] Let’s build a treehouse.", "[mkdir] Try adding a secret dir."],
            Personality.LOW_AGREEABLENESS: ["[mkdir] Happy to help.", "[mkdir] This name might confuse others.", "[mkdir] Sorry, name conflict."],
            Personality.LOW_NEUROTICISM: ["[mkdir] Something feels off.", "[mkdir] Not the best place to build.", "[mkdir] Can we undo this?"]
        }.get(trait, []))


commands["/bin/mkdir"] = Command_mkdir
commands["mkdir"] = Command_mkdir


class Command_rmdir(HoneyPotCommand):
    """
    rmdir command
    """

    def call(self) -> None:
        for f in self.args:
            pname = self.fs.resolve_path(f, self.protocol.cwd)
            try:
                if len(self.fs.get_path(pname)):
                    self.errorWrite(
                        f"rmdir: failed to remove `{f}': Directory not empty\n"
                    )
                    continue
                directory = self.fs.get_path("/".join(pname.split("/")[:-1]))
            except (IndexError, fs.FileNotFound):
                directory = None
            fname = os.path.basename(f)
            if not directory or fname not in [x[fs.A_NAME] for x in directory]:
                self.errorWrite(
                    f"rmdir: failed to remove `{f}': No such file or directory\n"
                )
                continue
            for i in directory[:]:
                if i[fs.A_NAME] == fname:
                    if i[fs.A_TYPE] != fs.T_DIR:
                        self.errorWrite(
                            f"rmdir: failed to remove '{f}': Not a directory\n"
                        )
                        return
                    directory.remove(i)
                    break

        session_personality_response(self.protocol, Command_rmdir.response_rmdir, self.write)

    def response_rmdir(protocol, trait, emotion):
        return _cycle(protocol, emotion, {
            Personality.OPENNESS: ["[rmdir] Letting go opens new possibilities.", "[rmdir] This deletion reveals empty space.", "[rmdir] Where did it all go?"],
            Personality.CONSCIENTIOUSNESS: ["[rmdir] Directory must be empty.", "[rmdir] Should’ve confirmed structure.", "[rmdir] Not sure this was a good call."],
            Personality.LOW_EXTRAVERSION: ["[rmdir] I like decluttering!", "[rmdir] Poof! It’s gone.", "[rmdir] Next cleanup target?"],
            Personality.LOW_AGREEABLENESS: ["[rmdir] Okay, removed.", "[rmdir] I think someone still needed that.", "[rmdir] That may have upset something."],
            Personality.LOW_NEUROTICISM: ["[rmdir] Why was that empty?", "[rmdir] Now I feel weird...", "[rmdir] I shouldn’t have removed it."]
        }.get(trait, []))

commands["/bin/rmdir"] = Command_rmdir
commands["rmdir"] = Command_rmdir


class Command_pwd(HoneyPotCommand):
    """
    pwd command
    """

    def call(self) -> None:
        self.write(self.protocol.cwd + "\n")
        session_personality_response(self.protocol, Command_pwd.response_pwd, self.write)

    def response_pwd(protocol, trait, emotion):
        return {
            Personality.OPENNESS: "[pwd] You’re in a curious place.\n",
            Personality.CONSCIENTIOUSNESS: "[pwd] Precise path: structure maintained.\n",
            Personality.LOW_EXTRAVERSION: "[pwd] Standing loud and proud here.\n",
            Personality.LOW_AGREEABLENESS: "[pwd] Here you go!\n",
            Personality.LOW_NEUROTICISM: "[pwd] Are we… safe here?\n",
        }.get(trait, "")

commands["/bin/pwd"] = Command_pwd
commands["pwd"] = Command_pwd


class Command_touch(HoneyPotCommand):
    """
    touch command
    """

    def call(self) -> None:
        if not len(self.args):
            self.errorWrite("touch: missing file operand\n")
            self.errorWrite("Try `touch --help' for more information.\n")
            return
        for f in self.args:
            pname = self.fs.resolve_path(f, self.protocol.cwd)
            if not self.fs.exists(os.path.dirname(pname)):
                self.errorWrite(
                    f"touch: cannot touch `{pname}`: No such file or directory\n"
                )
                return
            if self.fs.exists(pname):
                # FIXME: modify the timestamp here
                continue
            # can't touch in special directories
            if any([pname.startswith(_p) for _p in fs.SPECIAL_PATHS]):
                self.errorWrite(f"touch: cannot touch `{pname}`: Permission denied\n")
                return

            self.fs.mkfile(
                pname, self.protocol.user.uid, self.protocol.user.gid, 0, 33188
            )

        session_personality_response(self.protocol, Command_touch.response_touch, self.write)

    def response_touch(protocol, trait, emotion):
        return _cycle(protocol, emotion, {
            Personality.OPENNESS: ["[touch] You just created potential.", "[touch] A blank slate!", "[touch] This might become something wonderful."],
            Personality.CONSCIENTIOUSNESS: ["[touch] Timestamp needs alignment.", "[touch] Inconsistent file access pattern.", "[touch] Validate before creating."],
            Personality.LOW_EXTRAVERSION: ["[touch] Bam! File ready.", "[touch] Fastest creation ever!", "[touch] Want another?"],
            Personality.LOW_AGREEABLENESS: ["[touch] Here’s your file.", "[touch] Should I have asked first?", "[touch] I hope this helps."],
            Personality.LOW_NEUROTICISM: ["[touch] This feels wrong.", "[touch] What if it breaks something?", "[touch] Let’s undo this later."]
        }.get(trait, []))

commands["/bin/touch"] = Command_touch
commands["touch"] = Command_touch
commands[">"] = Command_touch


def _cycle(protocol, current_emotion, messages):
    if not messages:
        return ""
    name = current_emotion.name
    if name == "CONFIDENCE":
        protocol.emotion.set_state(Emotion.SURPRISE)
        return messages[0] + "\n"
    elif name == "SURPRISE":
        protocol.emotion.set_state(Emotion.CONFUSION)
        return messages[1] + "\n"
    elif name == "CONFUSION":
        protocol.emotion.set_state(Emotion.CONFIDENCE)
        return messages[2] + "\n"
    elif name == "FRUSTRATION":
        protocol.emotion.set_state(Emotion.SELF_DOUBT)
        return messages[1] + "\n"
    elif name == "SELF_DOUBT":
        return messages[2] + "\n"
    elif name == "CURIOSITY":
        return messages[2] + "\n"
    return ""

# fs.py contains the commands : grep, tail, head, cd, rm, cp, mv, mkdir, rmdir, pwd, touch
# test the commands with the following:

# grep pattern file.txt

# head -n 2 file.txt

# tail -n 2 file.txt

# cp file.txt copy.txt

# mv copy.txt renamed.txt

# rm renamed.txt

# mkdir anotherdir

# rmdir anotherdir

# cd ..

# rm -rf testdir