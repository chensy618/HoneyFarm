# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information


from __future__ import annotations

import random
import re
from typing import Any, TYPE_CHECKING

from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

if TYPE_CHECKING:
    from collections.abc import Callable

commands = {}


class Command_faked_package_class_factory:
    @staticmethod
    def getCommand(name: str) -> Callable:
        class Command_faked_installation(HoneyPotCommand):
            def call(self) -> None:
                self.write(f"{name}: Segmentation fault\n")

        return Command_faked_installation


class Command_aptget(HoneyPotCommand):
    """
    apt-get fake
    suppports only the 'install PACKAGE' command & 'moo'.
    Any installed packages, places a 'Segfault' at /usr/bin/PACKAGE.'''
    """

    packages: dict[str, dict[str, Any]]

    def start(self) -> None:
        if len(self.args) == 0:
            self.do_help()
        elif len(self.args) > 0 and self.args[0] == "-v":
            self.do_version()
        elif len(self.args) > 0 and self.args[0] == "install":
            self.do_install()
        elif len(self.args) > 0 and self.args[0] == "moo":
            self.do_moo()
        else:
            self.do_locked()
        self.packages = {}

    def sleep(self, time: float, time2: float | None = None) -> defer.Deferred:
        d: defer.Deferred = defer.Deferred()
        if time2:
            time = random.randint(int(time * 100), int(time2 * 100.0)) / 100.0
        reactor.callLater(time, d.callback, None)  # type: ignore[attr-defined]
        return d

    def do_version(self) -> None:
        self.write(
            """apt 1.0.9.8.1 for amd64 compiled on Jun 10 2015 09:42:06
Supported modules:
*Ver: Standard .deb
*Pkg:  Debian dpkg interface (Priority 30)
 Pkg:  Debian APT solver interface (Priority -1000)
 S.L: 'deb' Standard Debian binary tree
 S.L: 'deb-src' Standard Debian source tree
 Idx: Debian Source Index
 Idx: Debian Package Index
 Idx: Debian Translation Index
 Idx: Debian dpkg status file
 Idx: EDSP scenario file\n"""
        )
        self.exit()

    def do_help(self) -> None:
        self.write(
            """apt 1.0.9.8.1 for amd64 compiled on Jun 10 2015 09:42:06
Usage: apt-get [options] command
       apt-get [options] install|remove pkg1 [pkg2 ...]
       apt-get [options] source pkg1 [pkg2 ...]

apt-get is a simple command line interface for downloading and
installing packages. The most frequently used commands are update
and install.

Commands:
   update - Retrieve new lists of packages
   upgrade - Perform an upgrade
   install - Install new packages (pkg is libc6 not libc6.deb)
   remove - Remove packages
   autoremove - Remove automatically all unused packages
   purge - Remove packages and config files
   source - Download source archives
   build-dep - Configure build-dependencies for source packages
   dist-upgrade - Distribution upgrade, see apt-get(8)
   dselect-upgrade - Follow dselect selections
   clean - Erase downloaded archive files
   autoclean - Erase old downloaded archive files
   check - Verify that there are no broken dependencies
   changelog - Download and display the changelog for the given package
   download - Download the binary package into the current directory

Options:
  -h  This help text.
  -q  Loggable output - no progress indicator
  -qq No output except for errors
  -d  Download only - do NOT install or unpack archives
  -s  No-act. Perform ordering simulation
  -y  Assume Yes to all queries and do not prompt
  -f  Attempt to correct a system with broken dependencies in place
  -m  Attempt to continue if archives are unlocatable
  -u  Show a list of upgraded packages as well
  -b  Build the source package after fetching it
  -V  Show verbose version numbers
  -c=? Read this configuration file
  -o=? Set an arbitrary configuration option, eg -o dir::cache=/tmp
See the apt-get(8), sources.list(5) and apt.conf(5) manual
pages for more information and options.
                       This APT has Super Cow Powers.\n"""
        )
        self.exit()

    @inlineCallbacks
    def do_install(self, *args):
        if len(self.args) <= 1:
            msg = "0 upgraded, 0 newly installed, 0 to remove and {0} not upgraded.\n"
            self.write(msg.format(random.randint(200, 300)))
            self.exit()
            return

        for y in [re.sub("[^A-Za-z0-9]", "", x) for x in self.args[1:]]:
            self.packages[y] = {
                "version": f"{random.choice([0, 1])}.{random.randint(1, 40)}-{random.randint(1, 10)}",
                "size": random.randint(100, 900),
            }
        totalsize: int = sum(self.packages[x]["size"] for x in self.packages)

        self.write("Reading package lists... Done\n")
        self.write("Building dependency tree\n")
        self.write("Reading state information... Done\n")
        self.write("The following NEW packages will be installed:\n")
        self.write("  {} ".format(" ".join(self.packages)) + "\n")
        self.write(
            f"0 upgraded, {len(self.packages)} newly installed, 0 to remove and 259 not upgraded.\n"
        )
        self.write(f"Need to get {totalsize}.2kB of archives.\n")
        self.write(
            f"After this operation, {totalsize * 2.2:.1f}kB of additional disk space will be used.\n"
        )
        i = 1
        for p in self.packages:
            self.write(
                "Get:{} http://ftp.debian.org stable/main {} {} [{}.2kB]\n".format(
                    i, p, self.packages[p]["version"], self.packages[p]["size"]
                )
            )
            i += 1
            yield self.sleep(1, 2)
        self.write(f"Fetched {totalsize}.2kB in 1s (4493B/s)\n")
        self.write("Reading package fields... Done\n")
        yield self.sleep(1, 2)
        self.write("Reading package status... Done\n")
        self.write(
            "(Reading database ... 177887 files and directories currently installed.)\n"
        )
        yield self.sleep(1, 2)
        for p in self.packages:
            self.write(
                "Unpacking {} (from .../archives/{}_{}_i386.deb) ...\n".format(
                    p, p, self.packages[p]["version"]
                )
            )
            yield self.sleep(1, 2)
        self.write("Processing triggers for man-db ...\n")
        yield self.sleep(2)
        for p in self.packages:
            self.write(
                "Setting up {} ({}) ...\n".format(p, self.packages[p]["version"])
            )
            self.fs.mkfile(
                f"/usr/bin/{p}",
                self.protocol.user.uid,
                self.protocol.user.gid,
                random.randint(10000, 90000),
                33188,
            )
            self.protocol.commands[f"/usr/bin/{p}"] = (
                Command_faked_package_class_factory.getCommand(p)
            )
            yield self.sleep(2)
        session_personality_response(self.protocol, self.response_apt, self.write)
        self.exit()

    def do_moo(self) -> None:
        self.write("         (__)\n")
        self.write("         (oo)\n")
        self.write("   /------\\/\n")
        self.write("  / |    ||\n")
        self.write(" *  /\\---/\\ \n")
        self.write("    ~~   ~~\n")
        self.write('...."Have you mooed today?"...\n')
        self.exit()

    def do_locked(self) -> None:
        self.errorWrite(
            "E: Could not open lock file /var/lib/apt/lists/lock - open (13: Permission denied)\n"
        )
        self.errorWrite("E: Unable to lock the list directory\n")
        session_personality_response(self.protocol, self.response_apt, self.write)
        self.exit()

    @staticmethod
    def response_apt(protocol, trait, emotion):
        """
        Emotional/personality-based response logic for 'apt-get'
        This can be called after 'moo', 'install', etc.
        """
        if trait.name == "OPENNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "E: 404 Not Found - Unable to locate package"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "E: 403 Forbidden - Some index files failed to download"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "E: 100 Package not found - Check your sources"
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "E: 500 Internal Server Error - Something went wrong server-side"
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "E: 104 Hash Sum mismatch - Downloaded file doesn't match"

        elif trait.name == "CONSCIENTIOUSNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "E: 101 The package is not installable"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "E: 407 Proxy Authentication Required"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "E: 200 Broken packages found"
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "E: 0 Success - Package installed correctly"
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "E: 403 Forbidden"

        elif trait.name == "LOW_EXTRAVERSION":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "E: 400 Bad Request - Check your install command"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "E: 0 Success - Package installed successfully"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "E: 200 OK - Package installed without issues"
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "E: 403 Forbidden - Package repo access denied"
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "E: 418 - Cannot install package"

        elif trait.name == "LOW_AGREEABLENESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "E: 404 Package not found"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "E: 0 Success - Package installed successfully"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "E: 200 OK - Package installed without issues"
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "E: 500 Internal Server Error - Something went wrong"
            elif emotion.name == "SURPRISE":
                return "E: 403 Forbidden - Access denied to package repository"

        elif trait.name == "LOW_NEUROTICISM":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "E: 404 Not Found - Unable to locate package"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "E: 403 Forbidden - Some index files failed to download"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "E: 200 OK - Package installed successfully"
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "E: 500 Internal Server Error - Something went wrong"
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return " Installation complete - No errors encountered"

        return None


commands["/usr/bin/apt-get"] = Command_aptget
commands["/bin/apt-get"] = Command_aptget
commands["apt-get"] = Command_aptget
commands["/usr/bin/apt"] = Command_aptget
commands["/bin/apt"] = Command_aptget
commands["apt"] = Command_aptget
