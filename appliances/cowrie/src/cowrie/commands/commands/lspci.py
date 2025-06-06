from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response


# output taken from https://opensource.com/article/21/9/lspci-linux-hardware
# avoiding any mention of VMware/virtual etc to ensure attempts to look for vm not found
def lspci_out():
    return """00:00.0 Host bridge: Advanced Micro Devices, Inc. [AMD] RS880 Host Bridge
00:02.0 PCI bridge: Advanced Micro Devices, Inc. [AMD] RS780 PCI to PCI bridge (ext gfx port 0)
00:04.0 PCI bridge: Advanced Micro Devices, Inc. [AMD] RS780/RS880 PCI to PCI bridge (PCIE port 0)
00:05.0 PCI bridge: Advanced Micro Devices, Inc. [AMD] RS780/RS880 PCI to PCI bridge (PCIE port 1)
00:11.0 SATA controller: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0/SB8x0/SB9x0 SATA Controller [AHCI mode]
00:12.0 USB controller: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0/SB8x0/SB9x0 USB OHCI0 Controller
00:12.1 USB controller: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0 USB OHCI1 Controller
00:12.2 USB controller: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0/SB8x0/SB9x0 USB EHCI Controller
00:13.0 USB controller: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0/SB8x0/SB9x0 USB OHCI0 Controller
00:13.1 USB controller: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0 USB OHCI1 Controller
00:13.2 USB controller: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0/SB8x0/SB9x0 USB EHCI Controller
00:14.0 SMBus: Advanced Micro Devices, Inc. [AMD/ATI] SBx00 SMBus Controller (rev 3c)
00:14.1 IDE interface: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0/SB8x0/SB9x0 IDE Controller
00:14.3 ISA bridge: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0/SB8x0/SB9x0 LPC host controller
00:14.4 PCI bridge: Advanced Micro Devices, Inc. [AMD/ATI] SBx00 PCI to PCI Bridge
00:14.5 USB controller: Advanced Micro Devices, Inc. [AMD/ATI] SB7x0/SB8x0/SB9x0 USB OHCI2 Controller
00:18.0 Host bridge: Advanced Micro Devices, Inc. [AMD] Family 10h Processor HyperTransport Configuration
00:18.1 Host bridge: Advanced Micro Devices, Inc. [AMD] Family 10h Processor Address Map
00:18.2 Host bridge: Advanced Micro Devices, Inc. [AMD] Family 10h Processor DRAM Controller
00:18.3 Host bridge: Advanced Micro Devices, Inc. [AMD] Family 10h Processor Miscellaneous Control
00:18.4 Host bridge: Advanced Micro Devices, Inc. [AMD] Family 10h Processor Link Control
01:00.0 VGA compatible controller: NVIDIA Corporation GK107 [GeForce GTX 650] (rev a1)
01:00.1 Audio device: NVIDIA Corporation GK107 HDMI Audio Controller (rev a1)
02:00.0 Network controller: Qualcomm Atheros AR9287 Wireless Network Adapter (PCI-Express) (rev 01)\n"""


commands = {}


class Command_lspci(HoneyPotCommand):
    def call(self):
        self.write(lspci_out())
        session_personality_response(self.protocol, self.response_lspci, self.write)

    @staticmethod
    def response_lspci(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "lspci: USB devices are not listed here. Use `lsusb` instead."
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "lspci: PCI devices are broken down by bus, check the bus numbers"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "lspci: All PCI devices are listed. No issues detected."
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "lspci: No devices found"
            elif emotion == Emotion.SURPRISE:
                protocol.emotiona.set_state(Emotion.FRUSTRATION)
                return "lspci: Unexpected device detected. Please check the hardware"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "lspci: Detailed inspection underway......"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "lspci: Use `lspci -v` for verbose output"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "lspci: CPU information: AMD Family 10h Processor"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "lspci: No devices found. Please check the hardware connections"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "lspci: Unexpected peripheral spotted, use `lspci -vv` for details"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "lspci: Invalid command. Use `lspci --help` for assistance"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "lspci: Unknown error occurred. Please try again"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "lspci: All devices are accounted for. No issues detected"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "lspci: Fatal error: No devices found. Please check the hardware"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "lspci: Invalid argument provided. Use `lspci --help` for guidance"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "lspci: Device listing is incomplete. Use `lspci -vv` for details"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "lspco: Invalid command. Use `lspci --help` for assistance"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "lspci: Finding devices... Please wait"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "lspci: Use lsusb for USB devices, lspci only lists PCI devices"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return ""

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "lspci: No devices found. Please check the hardware connections"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "lspci: Use `lspci -vv` for verbose output"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "lspci: Command not found or invalid option"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return ""
            elif emotion == Emotion.SURPRISE:
                return ""

        return ""



commands["/usr/bin/lspci"] = Command_lspci
commands["lspci"] = Command_lspci
