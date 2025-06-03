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
                return "So many services... what do they all do?"
            elif emotion == Emotion.SELF_DOUBT:
                return "You're not sure which one matters, are you?"
            elif emotion == Emotion.CONFIDENCE:
                return "Everything's ticking like clockwork."
            elif emotion == Emotion.FRUSTRATION:
                return "These services just won't behave!"
            elif emotion == Emotion.SURPRISE:
                return "Didn't expect that many things running, huh?"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFUSION:
                return "Let's get everything in order. Status check complete."
            elif emotion == Emotion.SELF_DOUBT:
                return "You're trying to verify the service state. That's smart."
            elif emotion == Emotion.CONFIDENCE:
                return "All services scanned. System integrity verified."
            elif emotion == Emotion.FRUSTRATION:
                return "One misconfigured service can ruin your day."
            elif emotion == Emotion.SURPRISE:
                return "Unexpected service running? Time to audit."

        elif trait == Personality.EXTRAVERSION:
            if emotion == Emotion.CONFUSION:
                return "Whoa, look at all those services!"
            elif emotion == Emotion.SELF_DOUBT:
                return "C'mon, you know this. It's just systemd fun."
            elif emotion == Emotion.CONFIDENCE:
                return "Running strong, no holding back!"
            elif emotion == Emotion.FRUSTRATION:
                return "Let's stop and start things with flair!"
            elif emotion == Emotion.SURPRISE:
                return "Hey now, didn't expect 'bluetooth' to be up!"

        elif trait == Personality.AGREEABLENESS:
            if emotion == Emotion.CONFUSION:
                return "Don't worry, let's take it one service at a time."
            elif emotion == Emotion.SELF_DOUBT:
                return "You're doing fine. The system's got your back."
            elif emotion == Emotion.CONFIDENCE:
                return "All's well. Great job checking the status."
            elif emotion == Emotion.FRUSTRATION:
                return "It's okay. Some services just need a little nudge."
            elif emotion == Emotion.SURPRISE:
                return "Oh wow, didn't know that was running!"

        elif trait == Personality.NEUROTICISM:
            if emotion == Emotion.CONFUSION:
                return "Is something malicious running? Could be..."
            elif emotion == Emotion.SELF_DOUBT:
                return "What if a service is pretending to be another?"
            elif emotion == Emotion.CONFIDENCE:
                return "You've got a lock on this machine."
            elif emotion == Emotion.FRUSTRATION:
                return "Still can't stop that rogue process, huh?"
            elif emotion == Emotion.SURPRISE:
                return "What the—'whoopsie' is still running?"

        return ""


commands["/usr/sbin/service"] = Command_service
commands["service"] = Command_service
