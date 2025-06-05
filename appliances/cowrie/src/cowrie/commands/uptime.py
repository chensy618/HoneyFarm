# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

from __future__ import annotations

import time

from cowrie.core import utils
from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}


class Command_uptime(HoneyPotCommand):
    def call(self) -> None:
        self.write(
            "{}  up {},  1 user,  load average: 0.00, 0.00, 0.00\n".format(
                time.strftime("%H:%M:%S"), utils.uptime(self.protocol.uptime())
            )
        )
        # self.write("OpenWrt honeypot-device 4.14.123 #1 SMP Mon Jan 1 00:00:00 UTC 2024 armv7l GNU/Linux\n")
        session_personality_response(self.protocol, self.response_uptime, self.write)

    @staticmethod
    def response_uptime(protocol, trait, emotion):
        """
        Emotional/personality-based response logic for 'uptime'.
        This version directly sets the new emotional state.
        """

        if trait.name == "OPENNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "How long have *you* been watching this machine?"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Still unsure if uptime really matters?"
            elif emotion.name == "CONFIDENCE":
                return "Stable and steady. Just like your instincts."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Up for too long? Everything gets tired eventually."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Wow, it's still up? Unexpectedly persistent."

        elif trait.name == "CONSCIENTIOUSNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Tracking uptime helps maintain consistency."
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "You're doing fine—monitoring shows discipline."
            elif emotion.name == "CONFIDENCE":
                return "Great, uptime confirms everything is under control."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "System's up. You can't blame it for instability."
            elif emotion.name == "SURPRISE":
                return "All records check out. No anomalies."

        elif trait.name == "LOW_EXTRAVERSION":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Let's figure out what this number *really* means together."
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Hey, uptime isn't everything. You've got presence."
            elif emotion.name == "CONFIDENCE":
                return "Look at that uptime! Always online, just like you."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Even uptime can't keep up with your energy."
            elif emotion.name == "SURPRISE":
                return "Didn't expect such dedication, huh?"

        elif trait.name == "LOW_AGREEABLENESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Need help reading uptime? It's okay to ask."
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "You care enough to check—don't worry."
            elif emotion.name == "CONFIDENCE":
                return "Nice. That's a friendly number."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Maybe a reboot would ease the pressure?"
            elif emotion.name == "SURPRISE":
                return "It's been up this long and still kind!"

        elif trait.name == "LOW_NEUROTICISM":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Why's it still up? Something might be wrong…"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Don't panic—it's normal for systems to stay online."
            elif emotion.name == "CONFIDENCE":
                return "You saw that right—everything's as expected."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "This system... never rests. Just like your mind."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Huh. It hasn't crashed yet."

        return None


commands["/usr/bin/uptime"] = Command_uptime
commands["uptime"] = Command_uptime
