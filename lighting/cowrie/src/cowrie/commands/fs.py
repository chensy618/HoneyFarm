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
import datetime
from twisted.python import log

from cowrie.shell import fs
from cowrie.shell.command import HoneyPotCommand
from typing import TYPE_CHECKING
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response
from cowrie.honeytoken.email_alert import send_honeytoken_email
from cowrie.honeytoken.honeyfiles  import HONEYTOKEN_LIGHTING_FOLDERS

if TYPE_CHECKING:
    from collections.abc import Callable

commands: dict[str, Callable] = {}


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
                "grep: 9xQv@#lP$7b!eZ^tMn3*W&cYj0{A|r+g)u<dF>o%kL2!~B@zRp$Hq=T8Xs&U{nv#D*m}fN]ie^C[O(13",
                "grep: diagnostics ip address: 172.16.0.20 ",
                "grep: �ܦ߷࠿Ꙫ�ؕؼꧥ𒁹𓅓𑁋�\uFFFD\uDC80\uDCFF",
                "grep: file not found: /etc/passwd",
                "grep: no such file or directory"
            ])
        elif trait == Personality.CONSCIENTIOUSNESS:
            return _cycle(protocol, emotion, [
                "grep: No such file or directory",
                "grep: File not found",
                "grep: Invalid file format",
                "grep: Unexpected file type",
                "grep: File access denied",
            ])
        elif trait == Personality.LOW_EXTRAVERSION:
            return _cycle(protocol, emotion, [
                "node: smart home system",
                "node: IoT device",
                "node: security camera",
                "node: smart thermostat",
                "node: smart lock",
                "node: smart light bulb",
                
            ])
        elif trait == Personality.LOW_AGREEABLENESS:
            return _cycle(protocol, emotion, [
               "grep: No such file or directory",
               "grep: permission denied",
               "grep: cannot access `file': No such file or directory",
               "grep: cannot open `file': Permission denied", 
               "",             
            ])
        elif trait == Personality.LOW_NEUROTICISM:
            return _cycle(protocol, emotion, [
                "grep: invalid option -- 'x'",
                "grep: cannot open file: No such file or directory",
                "grep: file not found: /etc/passwd",
                "grep: unrecognized option `-x"
                ""
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
                "tail: unexpected end of file",
                "tail: file truncated unexpectedly",
                "tail: file not found: /var/log/syslog",
                "tail: cannot open file: No such file or directory",
                ""
            ])
        elif trait == Personality.CONSCIENTIOUSNESS:
            return _cycle(protocol, emotion, [
                "tail: file not found: /var/log/auth.log",
                "tail: kL2!~B@zRp$Hq=T8Xs&U"
                "tail: user@host:~$ tail -f /var/log/syslog",
                "tail: cannot open file: Permission denied",
            ])
        elif trait == Personality.LOW_EXTRAVERSION:
            return _cycle(protocol, emotion, [
                "tail: unexpected end of file",
                "tail: application log /var/log/app.log",
                "tail: system log /var/log/syslog",
                "tail: security log /var/log/auth.log",
                "tail: error log /var/log/error.log",
            ])
        elif trait == Personality.LOW_AGREEABLENESS:
            return _cycle(protocol, emotion, [
                "tail: please specify a file to read",
                "tail: no such file or directory: /var/log/messages",
                "tail: cannot open file: Permission denied",
                "tail: cannot read file: No such file or directory",
                ""
            ])
        elif trait == Personality.LOW_NEUROTICISM:
            return _cycle(protocol, emotion, [
                "tail: Log lines feel off.",
                "tail: Hmm, timestamps don't align...",
                "tail: Something's broken."
                "tail: File not found: /var/log/syslog",
                ""
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
                "head: unexpected file format",
                "head: file not found: /var/log/syslog",
                "head: cannot open file: No such file or directory",
                "head: file truncated unexpectedly",
                ""
            ])
        elif trait == Personality.CONSCIENTIOUSNESS:
            return _cycle(protocol, emotion, [
                "head: file not found: /var/log/auth.log",
                "head: kL2!~B@zRp$H",
                "head: user@host:~$ head -n 10 /var/log/syslog",
                "head: cannot open file: Permission denied",
                ""
            ])
        elif trait == Personality.LOW_EXTRAVERSION:
            return _cycle(protocol, emotion, [
                "head: unexpected file format",
                "head: application log /var/log/app.log",
                "head: system log /var/log/syslog",
                "head: security log /var/log/auth.log",
                ""
            ])
        elif trait == Personality.LOW_AGREEABLENESS:
            return _cycle(protocol, emotion, [
                "head: please specify a file to read",
                "head: no such file or directory: /var/log/messages",
                "head: cannot open file: Permission denied",
                "head: cannot read file: No such file or directory",
                ""
            ])
        elif trait == Personality.LOW_NEUROTICISM:
            return _cycle(protocol, emotion, [
                "head: fatal error: unexpected end of file",
                "head: unrecognized file format",
                "head: file not found: /var/log/syslog",
                "head: cannot open file: No such file or directory",
                ""
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

        # honeytoken detection
        print(f"Checking for honeytoken folders in {newpath}")
        if any(newpath.startswith("/" + folder.strip("/")) for folder in HONEYTOKEN_LIGHTING_FOLDERS):
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
                session_id = getattr(self.protocol.user.avatar, "session", None)
            except Exception:
                session_id = "unknown-session"

            timestamp = datetime.datetime.utcnow().isoformat()
            send_honeytoken_email(newpath, session_id, src_ip, src_port, timestamp)
            log.msg(
                eventid="cowrie.honeytoken",
                realm="cd",
                input=newpath,
                format="HONEYTOKEN (%(realm)s): %(input)s",
            )
                
        self.protocol.cwd = newpath

        session_personality_response(self.protocol, Command_cd.response_cd, self.write)

    def response_cd(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            return _cycle(protocol, emotion, [
                "--bash: cd: could not change directory to `{protocol.cwd}`: No such file or directory",
                "--bash: cd: could not change directory to `{protocol.cwd}`: Permission denied",
                "cd: 𓂀ꧧ�\u2060҂Ͷ߷𐍈��‍‍​‍ݽꙅ𐑃𓆣ࡘ৳𐤀ؼࠬ֎ͫ⚠️🝗꒰Ꙩ𒀭𐤴",
                "var log app sys auth messages",
                "var log app sys auth messages",
            ])
        elif trait == Personality.CONSCIENTIOUSNESS:
            return _cycle(protocol, emotion, [
                "cd: permission denied",
                "cd: could not find directory `{protocol.cwd}`",
                "cd: directory `{protocol.cwd}` is not accessible",
                "cd: opt/usr/bin/sbin: No such file or directory",
                ""
            ])
        elif trait == Personality.LOW_EXTRAVERSION:
            return _cycle(protocol, emotion, [
                "cd: unexpected directory structure",
                "cd: application log /var/log/app.log",
                "cd: system log /var/log/syslog",
                "cd: security log /var/log/auth.log",
                "cd: error log /var/log/error.log",
            ])
        elif trait == Personality.LOW_AGREEABLENESS:
            return _cycle(protocol, emotion, [
                "cd: please specify a directory to change into",
                "cd: no such file or directory: /var/log/messages",
                "cd: cannot access directory: Permission denied",
                "cd: cannot change to directory: No such file or directory",
                ""
            ])
        elif trait == Personality.LOW_NEUROTICISM:
            return _cycle(protocol, emotion, [
                "cd: fatal error: unexpected end of directory",
                "cd: unrecognized directory format",
                "cd: directory not found: /var/log/syslog",
                "cd: cannot change to directory: No such file or directory",
                ""
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
            Personality.OPENNESS: [
                "rm : cannot remove `file': No such file or directory", 
                "rm: cannot remove `file': Permission denied", 
                "rm: cannot remove `file': Is a directory",
                "rm: cannot remove `file': Operation not permitted",
                ""
            ],
            Personality.CONSCIENTIOUSNESS: [
                "rm: permission denied", 
                "rm: File not found", 
                "rm: Directory not empty",
                "rm: cannot remove `file': No such file or directory",
                ""
            ],
            Personality.LOW_EXTRAVERSION: [
                "rm: cannot remove `file': No such file or directory", 
                "rm: File removed successfully", 
                "rm: Directory removed successfully",
                "rm: cannot remove `file': Is a directory",
                ""

            ],
            Personality.LOW_AGREEABLENESS: [
                "rm: cannot remove read-only file `file'", 
                "rm: File removed successfully", 
                "rm: Directory removed successfully",
                "𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁𐤀𐤁",
                ""
            ],
            Personality.LOW_NEUROTICISM: [
                "rm: invalid option -- 'x'", 
                "rm: cannot remove `file': No such file or directory", 
                "rm: cannot remove `file': Permission denied",
                "rm: cannot remove `file': Is a directory",
                ""
            ]
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
            Personality.OPENNESS: [
                "cp: operation not permitted", 
                "cp: cannot copy file", 
                "cp: file copied successfully",
                "cp: cannot copy file: No such file or directory",
                ""
            ],
            Personality.CONSCIENTIOUSNESS: [
                "cp: file exists", 
                "cp: cannot copy file: Permission denied", 
                "cp: cannot copy file: Is a directory",
                "礮趉飌a炿得摀幼;伙驨惝甏弁危}",
                "%乇D鉜kP#枋N#g"
            ],
            Personality.LOW_EXTRAVERSION: [
                "cp: input/output error", 
                "cp: cannot copy file: No such file or directory", 
                "cp: file copied successfully",
                "cp: cannot copy file: Permission denied",
                ""
            ],
            Personality.LOW_AGREEABLENESS: [
                "cp: file exists", 
                "cp: cannot copy file: Permission denied", 
                "cp: cannot copy file: Is a directory",
                "cp: invalid option -- 'x'",
                "cp: cannot copy file: No such file or directory"
            ],
            Personality.LOW_NEUROTICISM: [
                "cp: directory not empty", 
                "cp: cannot copy file: No such file or directory", 
                "cp: cannot copy file: Permission denied",
                "cp: cannot copy file: Is a directory",
                ""
            ]
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
            Personality.OPENNESS: [
                "mv: File moved successfully.", 
                "mv: Unexpected file structure.", 
                "mv: Interesting file arrangement."
                "",
                ""
            ],
            Personality.CONSCIENTIOUSNESS: [
                "mv: File not found.", 
                "mv: Cannot move file: Permission denied.", 
                "mv: Cannot move file: Is a directory.",
                "mv: Cannot move file: No such file or directory.",
                ""
            ],
            Personality.LOW_EXTRAVERSION: [
                "mv: File moved successfully.", 
                "mv: Cannot move file: No such file or directory.", 
                "mv: File moved to new location."
                ""
                ""
            ],
            Personality.LOW_AGREEABLENESS: [
                "mv: invalid option -- 'x'", 
                "mv: Cannot move file: Permission denied.", 
                "mv: Cannot move file: Is a directory.",
                "",
                ""
            ],
            Personality.LOW_NEUROTICISM: [
                "mv: no such file or directory", 
                "mv: Cannot move file: No such file or directory", 
                "mv: Cannot move file: Permission denied",
                "mv: Cannot move file: Is a directory.",
                ""
            ]
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
            Personality.OPENNESS: [
                "mkdir: operation not supported", 
                "mkdir: Directory created successfully.", 
                "mkdir: Directory already exists."
                "mkdir: Directory structure not found",
                "mkdir: Cannot create directory: No such file or directory"
            ],
            Personality.CONSCIENTIOUSNESS: [
                "mkdir: Directory structure not found", 
                "mkdir: Cannot create directory: Permission denied", 
                "mkdir: Cannot create directory: Is a file"
                "mkdir: sadasd[ipohq wephjasjl;dj2   ]"
                ""
            ],
            Personality.LOW_EXTRAVERSION: [
                "mkdir: Directory created successfully.", 
                "mkdir: Cannot create directory: No such file or directory", 
                "mkdir: Directory already exists."
                "test app home code src bin etc var log",
                ""
            ],
            Personality.LOW_AGREEABLENESS: [
                "mkdir: invalid option -- 'x'", 
                "mkdir: Cannot create directory: Permission denied", 
                "mkdir: Cannot create directory: Is a file",
                "mkdir: Cannot create directory: No such file or directory",
                ""
            ],
            Personality.LOW_NEUROTICISM: [
                "mkdir: no such file or directory", 
                "mkdir: Cannot create directory: No such file or directory", 
                "mkdir: Cannot create directory: Permission denied"
                "",
                ""
            ]
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
            Personality.OPENNESS: ["rmdir: Directory removed successfully", "rmdir: are you sure?", "rmdir: Directory structure not found", "", ""],
            Personality.CONSCIENTIOUSNESS: ["rmdir: permission denied", "rmdir: Directory not empty", "rmdir: Directory structure not found", "", "",],
            Personality.LOW_EXTRAVERSION: ["rmdir: dangerous operation", "rmdir: Directory removed successfully", "rmdir: Directory not empty","",""],
            Personality.LOW_AGREEABLENESS: ["rmdir: no such file or directory", "rmdir: Directory removed successfully", "rmdir: Directory not empty","",""],
            Personality.LOW_NEUROTICISM: ["rmdir: --help for more information", "rmdir: Directory removed successfully", "rmdir: Directory not empty","",""]
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
            Personality.OPENNESS: "pwd: current working directory: var\log\n",
            Personality.CONSCIENTIOUSNESS: "pwd: current working directory: /home/user\n",
            Personality.LOW_EXTRAVERSION: "pwd: permission denied\n",
            Personality.LOW_AGREEABLENESS: "pwd: read-only file system\n",
            Personality.LOW_NEUROTICISM: "pwd: current working directory: /etc\n",
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
            self.errorWrite("Try `touch --help' for more information\n")
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
            Personality.OPENNESS: ["touch: File not expected.", "touch: File created successfully", "touch: File not found", "", ""],
            Personality.CONSCIENTIOUSNESS: ["touch: File already exists.", "touch: File creation failed", "touch: File not found","",""],
            Personality.LOW_EXTRAVERSION: ["touch: File created successfully", "touch: File not found", "touch: File creation failed","",""],
            Personality.LOW_AGREEABLENESS: ["touch: File created failed", "touch: File not found", "touch: File already exists","",""],
            Personality.LOW_NEUROTICISM: ["touch: permission denied", "touch: File not found", "touch: File creation failed",""]
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
        protocol.emotion.set_state(Emotion.FRUSTRATION)
        return messages[2] + "\n"
    elif name == "FRUSTRATION":
        protocol.emotion.set_state(Emotion.SELF_DOUBT)
        return messages[3] + "\n"
    elif name == "SELF_DOUBT":
        protocol.emotion.set_state(Emotion.CONFIDENCE)
        return messages[4] + "\n"
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