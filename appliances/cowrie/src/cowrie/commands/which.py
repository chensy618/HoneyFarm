# Copyright (c) 2013 Bas Stottelaar <basstottelaar [AT] gmail [DOT] com>

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.fs import FileNotFound
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}


class Command_which(HoneyPotCommand):
    # Do not resolve args
    resolve_args = False

    def call(self) -> None:
        """
        Look up all the arguments on PATH and print each (first) result
        """

        # No arguments, just exit
        if not len(self.args) or "PATH" not in self.environ:
            return

        # Look up each file
        for f in self.args:
            for path in self.environ["PATH"].split(":"):
                resolved = self.fs.resolve_path(f, path)

                if self.fs.exists(resolved):
                    self.write(f"{path}/{f}\n")
        
        session_personality_response(self.protocol, self.response_which, self.write)

    @staticmethod
    def response_which(protocol, trait, emotion):
        """
        Emotional/personality-based response logic for 'which' command.
        Includes emotion-state transitions.
        """

        if trait.name == "OPENNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Looking for paths? It's like a digital treasure hunt."
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Exploration leads to discovery. You're on the right path."
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Every command has its place. And you found it."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Sometimes even the obvious hides well."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "That's where it lives? Unexpected but enlightening."

        elif trait.name == "CONSCIENTIOUSNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Mapping binaries? You're maintaining structure."
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Checking paths shows you're methodical. Well done."
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Resolved path. Precision achieved."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Perhaps there's a missing link in PATH?"
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Interesting location. Worth noting for later."

        elif trait.name == "LOW_EXTRAVERSION":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Let's hunt those commands down together!"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "You're not alone. Tools should be where you expect."
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Got it! That binary's ready to party."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Still hiding? Let's flush them out!"
            elif emotion.name == "SURPRISE":
                return "Surprise path! Didn't expect that, huh?"

        elif trait.name == "LOW_AGREEABLENESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "It's okay. Let's gently look for the right place."
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "You're being careful and considerate—keep going!"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "There it is! Everything's in order."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "No worries. Let's try a different approach."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Oh! That's where it is—fun little discovery!"

        elif trait.name == "LOW_NEUROTICISM":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "What if it's not there? Maybe it moved…"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Why can't it be in the right place?"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "You're keeping control. Nothing escapes you."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Still no binary? Something must be wrong!"
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "Why was it there? That feels... off."

        return None


commands["which"] = Command_which
