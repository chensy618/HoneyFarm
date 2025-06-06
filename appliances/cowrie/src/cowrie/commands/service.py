# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.

"""
This module contains the service commnad
"""

from __future__ import annotations

import getopt

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}


class Command_service(HoneyPotCommand):
    """
    By Giannis Papaioannou <giannispapcod7@gmail.com>
    """

    def status_all(self) -> None:
        """
        more services can be added here.
        """
        output = (
            "[ + ]  acpid",
            "[ - ]  alsa-utils",
            "[ + ]  anacron",
            "[ + ]  apparmor",
            "[ + ]  apport",
            "[ + ]  avahi-daemon",
            "[ + ]  bluetooth",
            "[ - ]  bootmisc.sh",
            "[ - ]  brltty",
            "[ - ]  checkfs.sh",
            "[ - ]  checkroot-bootclean.sh",
            "[ - ]  checkroot.sh",
            "[ + ]  console-setup",
            "[ + ]  cron",
            "[ + ]  cups",
            "[ + ]  cups-browsed",
            "[ + ]  dbus",
            "[ - ]  dns-clean",
            "[ + ]  grub-common",
            "[ - ]  hostname.sh",
            "[ - ]  hwclock.sh",
            "[ + ]  irqbalance",
            "[ - ]  kerneloops",
            "[ - ]  killprocs",
            "[ + ]  kmod",
            "[ + ]  lightdm",
            "[ - ]  mountall-bootclean.sh",
            "[ - ]  mountall.sh",
            "[ - ]  mountdevsubfs.sh",
            "[ - ]  mountkernfs.sh",
            "[ - ]  mountnfs-bootclean.sh",
            "[ - ]  mountnfs.sh",
            "[ + ]  network-manager",
            "[ + ]  networking",
            "[ + ]  ondemand",
            "[ + ]  open-vm-tools",
            "[ - ]  plymouth",
            "[ - ]  plymouth-log",
            "[ - ]  pppd-dns",
            "[ + ]  procps",
            "[ - ]  rc.local",
            "[ + ]  resolvconf",
            "[ - ]  rsync",
            "[ + ]  rsyslog",
            "[ - ]  saned",
            "[ - ]  sendsigs",
            "[ + ]  speech-dispatcher",
            "[ + ]  thermald",
            "[ + ]  udev",
            "[ + ]  ufw",
            "[ - ]  umountfs",
            "[ - ]  umountnfs.sh",
            "[ - ]  umountroot",
            "[ - ]  unattended-upgrades",
            "[ + ]  urandom",
            "[ - ]  uuidd",
            "[ + ]  whoopsie",
            "[ - ]  x11-common",
        )
        for line in output:
            self.write(line + "\n")

        session_personality_response(self.protocol, self.response_service, self.write)


    def help(self) -> None:
        output = "Usage: service < option > | --status-all | [ service_name [ command | --full-restart ] ]"
        self.write(output + "\n")

    def call(self) -> None:
        try:
            opts, args = getopt.gnu_getopt(
                self.args, "h", ["help", "status-all", "full-restart"]
            )
        except getopt.GetoptError:
            self.help()
            return

        if not opts and not args:
            self.help()
            return

        for o, _a in opts:
            if o in ("--help") or o in ("-h"):
                self.help()
                return
            elif o in ("--status-all"):
                self.status_all()
        """
        Ubuntu shows no response when stopping, starting
        leviathan@ubuntu:~$ sudo service ufw stop
        leviathan@ubuntu:~$ sudo service ufw start
        leviathan@ubuntu:~$
        """

    @staticmethod
    def response_service(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Starting OpenBSD Secure Shell server: sshd"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "service: Unrecognized service"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return ""
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Interactive authentication required."
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Failed to start service: permission denied"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "ping: Unknown error occurred\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ping: Invalid option '-v'"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "All services scanned"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "One misconfigured service found, please check the configuration"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Unexpected error occurred (Error code: 123)"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "service: Unknown error\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "service: Unable to resolve service state\n"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "service: Failed to start service: permission denied\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return ""
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Starting OpenBSD Secure Shell server: sshd"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "service: Please try it again"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "See systemctl status ssh.service"
            elif emotion == Emotion.CONFIDENCE:
                 protocol.emotion.set_state(Emotion.CONFUSION)
                return "Starting background monitoring service: monitor\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return " Unable to resolve service state.\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Failed to restart apache2.service: Interactive authentication required."

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "service: Unknown option found"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "service: Ambiguous target"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "service: service started"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "ping: Unknown error occurred"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "ping: Operation not permitted"

        return ""


commands["/usr/sbin/service"] = Command_service
commands["service"] = Command_service
