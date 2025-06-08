# Copyright (c) 2014 Peter Reuterås <peter@reuteras.com>
# See the COPYRIGHT file for more information

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}


class Command_ethtool(HoneyPotCommand):
    def call(self) -> None:
        func = self.do_ethtool_help
        for x in self.args:
            if x.startswith("lo"):
                func = self.do_ethtool_lo
            if x.startswith("eth0"):
                func = self.do_ethtool_eth0
            if x.startswith("eth1"):
                func = self.do_ethtool_eth1
        func()
        session_personality_response(self.protocol, self.response_ethtool, self.write)

    def do_ethtool_help(self) -> None:
        """
        No real help output.
        """
        self.write(
            """ethtool: bad command line argument(s)
For more information run ethtool -h\n"""
        )

    def do_ethtool_lo(self) -> None:
        self.write(
            """Settings for lo:
            Link detected: yes\n"""
        )

    def do_ethtool_eth0(self) -> None:
        self.write(
            """Settings for eth0:
Supported ports: [ TP MII ]
Supported link modes:   10baseT/Half 10baseT/Full
                        100baseT/Half 100baseT/Full
                        1000baseT/Half 1000baseT/Full
Supported pause frame use: No
Supports auto-negotiation: Yes
Advertised link modes:  10baseT/Half 10baseT/Full
                        100baseT/Half 100baseT/Full
                        1000baseT/Half 1000baseT/Full
Advertised pause frame use: Symmetric Receive-only
Advertised auto-negotiation: Yes
Link partner advertised link modes:  10baseT/Half 10baseT/Full
                                     100baseT/Half 100baseT/Full
                                     1000baseT/Full
Link partner advertised pause frame use: Symmetric Receive-only
Link partner advertised auto-negotiation: Yes
Speed: 1000Mb/s
Duplex: Full
Port: MII
PHYAD: 0
Transceiver: internal
Auto-negotiation: on
Supports Wake-on: pumbg
Wake-on: g
Current message level: 0x00000033 (51)
                       drv probe ifdown ifup
Link detected: yes\n"""
        )

    def do_ethtool_eth1(self) -> None:
        self.write(
            """Settings for eth1:
Cannot get device settings: No such device
Cannot get wake-on-lan settings: No such device
Cannot get message level: No such device
Cannot get link status: No such device
No data available\n"""
        )

    @staticmethod
    def response_ethtool(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ethtool: eth0 running nonstandard firmware.\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "ethtool: detected dual MAC binding. Not expected.\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "ethtool: unable to retrieve driver version.\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "ethtool: fallback to generic driver profile.\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "ethtool: no known issues with the current configuration.\n"


        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ethtool: packet loss stats unavailable. Recheck required.\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "ethtool: unexpected TX/RX errors detected.\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                eth1 = protocol.fs.resolve_path("eth1", protocol.cwd)
                if protocol.fs.exists(eth1):
                    return "ethtool: eth1 interface not configured. No data.\n"
                else:
                    return "eth1: ip address 192.168.1.100\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "ethtool: mismatch in advertised vs detected speed.\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "ethtool: suggest validating link partner settings.\n"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ethtool: surge in TX throughput! Looks intense!\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "ethtool: strange half/full duplex toggling noted.\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "ethtool: social packet flooding simulation enabled.\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "ethtool: peer device not responding to pings.\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "ethtool: no issues found with eth0 interface.\n"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ethtool: peer handshake incomplete. Trying again...\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "ethtool: wake-on-lan blocked by peer consent flag.\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "ethtool: peer device not responding to ARP requests.\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "ethtool: silent conflict resolution applied.\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "ethtool: reported speed inconsistent with NIC logs.\n"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "ethtool: driver integrity questionable. System unstable?\n"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "ethtool: warning: no trust anchor for device signatures.\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "ethtool: unable to verify firmware authenticity.\n"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)

        return ""


commands["/sbin/ethtool"] = Command_ethtool
commands["ethtool"] = Command_ethtool
