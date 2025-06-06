# Copyright (c) 2010 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
uname command
"""

from __future__ import annotations

from cowrie.core.config import CowrieConfig
from cowrie.shell.command import HoneyPotCommand
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response


commands = {}


def hardware_platform() -> str:
    return CowrieConfig.get("shell", "hardware_platform", fallback="x86_64")


def kernel_name() -> str:
    return CowrieConfig.get("shell", "kernel_name", fallback="Linux")


def kernel_version() -> str:
    return CowrieConfig.get("shell", "kernel_version", fallback="3.2.0-4-amd64")


def kernel_build_string() -> str:
    return CowrieConfig.get(
        "shell", "kernel_build_string", fallback="#1 SMP Debian 3.2.68-1+deb7u1"
    )


def operating_system() -> str:
    return CowrieConfig.get("shell", "operating_system", fallback="GNU/Linux")


def uname_help() -> str:
    return """Usage: uname [OPTION]...
Print certain system information.  With no OPTION, same as -s.

  -a, --all                print all information, in the following order,
                             except omit -p and -i if unknown:
  -s, --kernel-name        print the kernel name
  -n, --nodename           print the network node hostname
  -r, --kernel-release     print the kernel release
  -v, --kernel-version     print the kernel version
  -m, --machine            print the machine hardware name
  -p, --processor          print the processor type (non-portable)
  -i, --hardware-platform  print the hardware platform (non-portable)
  -o, --operating-system   print the operating system
      --help     display this help and exit
      --version  output version information and exit

GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
Full documentation at: <http://www.gnu.org/software/coreutils/uname>
or available locally via: info '(coreutils) uname invocation'\n
"""


def uname_get_some_help() -> str:
    return "Try 'uname --help' for more information."


def uname_fail_long(arg: str) -> str:
    return f"uname: unrecognized option '{arg}'\n{uname_get_some_help()}\n"


def uname_fail_short(arg: str) -> str:
    return f"uname: invalid option -- '{arg}'\n{uname_get_some_help()}\n"


def uname_fail_extra(arg: str) -> str:
    # Note: These are apostrophes, not single quotation marks.
    return f"uname: extra operand ‘{arg}’\n{uname_get_some_help()}\n"


class Command_uname(HoneyPotCommand):
    def full_uname(self) -> str:
        return f"{kernel_name()} {self.protocol.hostname} {kernel_version()} {kernel_build_string()} {hardware_platform()} {operating_system()}\n"

    def call(self) -> None:
        opts = {
            "name": False,
            "release": False,
            "version": False,
            "os": False,
            "node": False,
            "machine": False,
        }

        flags = [
            (["a", "all"], "__ALL__"),
            (["s", "kernel-name"], "name"),
            (["r", "kernel-release"], "release"),
            (["v", "kernel-version"], "version"),
            (["o", "operating-system"], "os"),
            (["n", "nodename"], "node"),
            (["m", "machine", "p", "processor", "i", "hardware-platform"], "machine"),
        ]

        if not self.args:
            # IF no params output default
            self.write(f"{kernel_name()}\n")
            return

        # getopt-style parsing
        for a in self.args:
            a = a.strip()
            arg_block = []
            was_long = False

            if a == "--help":
                # Help overrides invalid args following --help
                # There's no -h, invalid args before --help still fail.
                self.write(uname_help())
                return
            elif a.startswith("--"):
                # arg name w/o --
                was_long = True
                arg_block.append(a[2:])
            elif a.startswith("-"):
                # letter by letter
                a = a[1:]
                if len(a) == 0:
                    self.write(uname_fail_extra("-"))
                    return

                for split_arg in a:
                    arg_block.append(split_arg)
            else:
                self.write(uname_fail_extra(a))
                return

            for arg in arg_block:
                arg_parsed = False

                # Find a possible flag for each arg.
                for possible_args, target_opt in flags:
                    if arg not in possible_args:
                        continue

                    arg_parsed = True  # Got a hit!

                    # Set all opts for -a/--all, single opt otherwise:
                    if target_opt == "__ALL__":
                        for key in opts.keys():
                            opts[key] = True
                    else:
                        opts[target_opt] = True

                    break  # Next arg please

                if not arg_parsed:
                    self.write(
                        uname_fail_long(a) if was_long else uname_fail_short(arg)
                    )
                    return

        # All the options set, let's get the output
        output = []

        if opts["name"]:
            output.append(kernel_name())
        if opts["node"]:
            output.append(self.protocol.hostname)
        if opts["release"]:
            output.append(kernel_version())
        if opts["version"]:
            output.append(kernel_build_string())
        if opts["machine"]:
            output.append(hardware_platform())
        if opts["os"]:
            output.append(operating_system())

        if len(output) < 1:
            output.append(kernel_name())

        self.write(" ".join(output) + "\n")
        session_personality_response(self.protocol, self.response_uname, self.write)

    @staticmethod
    def response_uname(protocol, trait, emotion):
        """
        Emotion-inducing uname output variations.
        """
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uname: unexpected output expansion triggered.\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uname: kernel string seems inconsistent with nodename.\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uname: fallback to safe output configuration.\n"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uname: checksum mismatch on hardware ID.\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "uname: potential time-skew in version timestamp.\n"
            elif emotion == Emotion.SELF_DOUBT:
                return "uname: incomplete sysinfo mapping. Possible override detected.\n"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uname: WOW! System profile exploded!\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uname: huh… duplicate hostname?\n"
            elif emotion == Emotion.CONFUSION:
                return "uname: auto-resolving identity clash...\n"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uname: syncing with network metadata...\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uname: info request denied by peer kernel.\n"
            elif emotion == Emotion.FRUSTRATION:
                return "uname: switching to isolated mode output.\n"

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uname: kernel response too quick — spoof suspected.\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "uname: shadow record mismatch detected.\n"
            elif emotion == Emotion.SELF_DOUBT:
                return "uname: host ID compromised. Suggest halting further ops.\n"

        return ""

commands["/bin/uname"] = Command_uname
commands["uname"] = Command_uname
