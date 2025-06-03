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
                return "So many devices… do they all talk to each other?"
            elif emotion == Emotion.SELF_DOUBT:
                return "You're trying to make sense of the machine. That's a start."
            elif emotion == Emotion.CONFIDENCE:
                return "You've mapped the hardware jungle. Nicely done."
            elif emotion == Emotion.FRUSTRATION:
                return "Still can't find the GPU you're looking for?"
            elif emotion == Emotion.SURPRISE:
                return "Wow, didn't expect that controller to be there!"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFUSION:
                return "Detailed inspection underway. PCI structure needs clarity."
            elif emotion == Emotion.SELF_DOUBT:
                return "Every bridge has a purpose. You're reading it right."
            elif emotion == Emotion.CONFIDENCE:
                return "Hardware detected. Organized and accounted for."
            elif emotion == Emotion.FRUSTRATION:
                return "Missing a device? Maybe check `dmesg` too."
            elif emotion == Emotion.SURPRISE:
                return "Unexpected peripheral spotted. Time to document."

        elif trait == Personality.EXTRAVERSION:
            if emotion == Emotion.CONFUSION:
                return "All these ports! Who's talking to what?"
            elif emotion == Emotion.SELF_DOUBT:
                return "Just dive in. Explore that PCI jungle!"
            elif emotion == Emotion.CONFIDENCE:
                return "Boom! Found all the hardware. Let's show it off."
            elif emotion == Emotion.FRUSTRATION:
                return "Let's unplug and replug everything!"
            elif emotion == Emotion.SURPRISE:
                return "Whoa! That's a lot of controllers."

        elif trait == Personality.AGREEABLENESS:
            if emotion == Emotion.CONFUSION:
                return "Looks tricky, but you're doing great."
            elif emotion == Emotion.SELF_DOUBT:
                return "You're being careful. That's wise with hardware."
            elif emotion == Emotion.CONFIDENCE:
                return "Nice list! Everything looks well-connected."
            elif emotion == Emotion.FRUSTRATION:
                return "Maybe `lsusb` next? I'm here with you!"
            elif emotion == Emotion.SURPRISE:
                return "Oh, what a neat discovery!"

        elif trait == Personality.NEUROTICISM:
            if emotion == Emotion.CONFUSION:
                return "What if a device is spoofed? What if it's not real?"
            elif emotion == Emotion.SELF_DOUBT:
                return "Are we sure the NIC is safe?"
            elif emotion == Emotion.CONFIDENCE:
                return "That's a full hardware map… probably."
            elif emotion == Emotion.FRUSTRATION:
                return "Still hiding? This machine's mocking us!"
            elif emotion == Emotion.SURPRISE:
                return "What is *that* even doing there?"

        return ""



commands["/usr/bin/lspci"] = Command_lspci
commands["lspci"] = Command_lspci
