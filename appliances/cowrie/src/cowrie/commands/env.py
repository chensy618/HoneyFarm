from __future__ import annotations
from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}

"""
env: invalid option -- 'h'
Try `env --help' for more information.

Usage: env [OPTION]... [-] [NAME=VALUE]... [COMMAND [ARG]...]
Set each NAME to VALUE in the environment and run COMMAND.

  -i, --ignore-environment  start with an empty environment
  -0, --null           end each output line with 0 byte rather than newline
  -u, --unset=NAME     remove variable from the environment
      --help     display this help and exit
      --version  output version information and exit

A mere - implies -i.  If no COMMAND, print the resulting environment.

Report env bugs to bug-coreutils@gnu.org
GNU coreutils home page: <http://www.gnu.org/software/coreutils/>
General help using GNU software: <http://www.gnu.org/gethelp/>
For complete documentation, run: info coreutils 'env invocation'
"""


class Command_env(HoneyPotCommand):
    def call(self) -> None:
        # This only show environ vars, not the shell vars. Need just to mimic real systems
        for i in list(self.environ.keys()):
            self.write(f"{i}={self.environ[i]}\n")

        session_personality_response(self.protocol, self.response_env, self.write)
        
    @staticmethod
    def response_env(protocol, trait, emotion, writer):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                writer("NOTE: Not all environment variables are shown.")
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                writer("_X=unexpected_heuristic")
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                writer("Hmm… what's this `_SEEDXID` doing here?")

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                writer("PATH=/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin")
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                writer("Warning: Duplicate environment PATH entries detected.")
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                writer("Suggestion: run `printenv | sort | uniq` to verify integrity.")

        elif trait == Personality.EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                writer("SESSION_SECRET=******")
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                writer("_HIDDEN_SESSION=TRUE  # invisible to standard tools")
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFUSION)
                writer("Shell instance isolated. Try `env -i`?")

        elif trait == Personality.AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                writer("SUDO_UID=0")
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                writer("Access denied for secure context variables.")
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                writer("This environment may be sandboxed.")

        elif trait == Personality.NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                writer("LOG_TIMESTAMP=Thu Jan 01 00:00:00 UTC 1970")
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                writer("DEBIAN_FRONTEND=noninteractive (but… why?)")
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                writer("You sure this is the right container context?")

        return


commands["/usr/bin/env"] = Command_env
commands["env"] = Command_env
