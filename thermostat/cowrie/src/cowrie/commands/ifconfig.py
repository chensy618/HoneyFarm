# Copyright (c) 2014 Peter Reuterås <peter@reuteras.com>
# See the COPYRIGHT file for more information

from __future__ import annotations

from random import randint, randrange

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response


HWaddr = f"{randint(0, 255):02x}:{randint(0, 255):02x}:{randint(0, 255):02x}:{randint(0, 255):02x}:{randint(0, 255):02x}:{randint(0, 255):02x}"

inet6 = f"fe{randint(0, 255):02x}::{randrange(111, 888):02x}:{randint(0, 255):02x}ff:fe{randint(0, 255):02x}:{randint(0, 255):02x}01/64"

commands = {}


class Command_ifconfig(HoneyPotCommand):
    @staticmethod
    def generate_packets() -> int:
        return randrange(222222, 555555)

    @staticmethod
    def convert_bytes_to_mx(bytes_eth0: int) -> str:
        mb = float(bytes_eth0) / 1000 / 1000
        return f"{mb:.1f}"

    def calculate_rx(self) -> tuple[int, str]:
        rx_bytes = randrange(111111111, 555555555)
        return rx_bytes, self.convert_bytes_to_mx(rx_bytes)

    def calculate_tx(self) -> tuple[int, str]:
        rx_bytes = randrange(11111111, 55555555)
        return rx_bytes, self.convert_bytes_to_mx(rx_bytes)

    def calculate_lo(self) -> tuple[int, str]:
        lo_bytes = randrange(11111111, 55555555)
        return lo_bytes, self.convert_bytes_to_mx(lo_bytes)

    def call(self) -> None:
        rx_bytes_eth0, rx_mb_eth0 = self.calculate_rx()
        tx_bytes_eth0, tx_mb_eth0 = self.calculate_tx()
        lo_bytes, lo_mb = self.calculate_lo()
        rx_packets = self.generate_packets()
        tx_packets = self.generate_packets()
        result = """eth0      Link encap:Ethernet  HWaddr {}
          inet addr:{}  Bcast:{}.255  Mask:255.255.255.0
          inet6 addr: {} Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:{} errors:0 dropped:0 overruns:0 frame:0
          TX packets:{} errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:{} ({} MB)  TX bytes:{} ({} MB)


lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:110 errors:0 dropped:0 overruns:0 frame:0
          TX packets:110 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:{} ({} MB)  TX bytes:{} ({} MB)""".format(
            HWaddr,
            self.protocol.kippoIP,
            self.protocol.kippoIP.rsplit(".", 1)[0],
            inet6,
            rx_packets,
            tx_packets,
            rx_bytes_eth0,
            rx_mb_eth0,
            tx_bytes_eth0,
            tx_mb_eth0,
            lo_bytes,
            lo_mb,
            lo_bytes,
            lo_mb,
        )
        
        self.write(f"{result}\n")
        session_personality_response(self.protocol, self.response_ifconfig, self.write)

    @staticmethod
    def response_ifconfig(protocol, trait, emotion):
        """
        Generate ifconfig-style deceptive output (not narrative).
        Output is designed to *cause* emotion, not reflect it.
        Also updates emotional state.
        """
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return """
vnet0     Link encap:Virtual  HWaddr aa:bb:cc:dd:ee:ff
          inet6 addr: fe80::1ff:fe23:4567:890a/64 Scope:Link
"""
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return """
eth0:0    Link encap:Ethernet  HWaddr 00:00:00:00:00:00
          inet6 addr: fe::xyz:1234:beef Scope:Link
"""
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return """
docker0   Link encap:Ethernet  HWaddr 02:42:ac:11:00:02
          inet addr:172.17.0.1  Mask:255.255.0.0
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:42  TX packets:66
"""

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return """
eth0      RX packets:999999  TX packets:999999
          Metric:1
"""
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return """
eth0      RX packets:123456  TX packets:123455
          RX bytes:100000000 (100.0 MB)  TX bytes:100000001 (100.0 MB)
"""
            elif emotion == Emotion.SELF_DOUBT:
                return """
eth0      Metric:1
          Metric:0
"""

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return """
eth2      Link encap:Ethernet  HWaddr de:ad:be:ef:00:01
          RX packets:321  TX packets:123
"""
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return """
eth0      TX packets:100
          TX packets:?
"""
            elif emotion == Emotion.CONFUSION:
                return """
eth0
          RX packets:0
"""

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return """
usbnet0   Link encap:USB-Net
          RX packets:4  TX packets:4
"""
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return """
eth1      Link encap:Ethernet
          [details removed by system]
"""
            elif emotion == Emotion.FRUSTRATION:
                return """
[Access denied to interface listing.]
"""

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return """
eth0      RX packets:1000000  TX packets:1000000
          No error detected.
"""
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return """
eth0      RX bytes: 1234567890
          TX bytes:
"""
            elif emotion == Emotion.SELF_DOUBT:
                return """
eth0      RX dropped: 0
          RX dropped: 1
"""

        return ""




commands["/sbin/ifconfig"] = Command_ifconfig
commands["ifconfig"] = Command_ifconfig
