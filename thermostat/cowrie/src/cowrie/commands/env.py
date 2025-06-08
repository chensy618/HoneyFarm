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
    def response_env(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                path = protocol.environ.get("PATH", "")
                return (
                    f"env: PATH variable is set to {path}\n"
                    "NOTE: Not all environment variables are shown\n"
                )
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "env: unexpected variable found _Z"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "env: variable _X not found"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "env: run `printenv | sort | uniq` to verify integrity"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "env: no issues found with environment variables"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "PATH=/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Warning: PATH variable contains duplicate entries"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "env: unexpected variable found LOGNAME=david"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return ""

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return (
                    "USER=david\nHOME=/home/david\nSHELL=/bin/bash\n"
                    "LANG=en_US.UTF-8\nTERM=xterm-256color\n"
                    "SESSION_SECRET=******\n"
                    "HIDDEN_SESSION=TRUE  # invisible to standard tools\n"
                )
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return (
                    "env: unexpected variable found SESSION_SECRET=admin\n"
                    "env: HIDDEN_SESSION=FALSE\n"
                )
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "Shell instance isolated. Try `env -i`?"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "env: unexpected variable found SHELL=/bin/sh"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "env: unexpected variable found USER=root"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "SUDO_UID=0"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Access denied for secure context variables"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "env: insufficient permissions to view sensitive data"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "env: unexpected variable found SUDO_USER=admin"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "env: unexpected variable found SUDO_COMMAND=/usr/bin/sudo"

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "LOG_TIMESTAMP=Thu Jan 01 00:00:00 UTC 1970"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "DEBIAN_FRONTEND=noninteractive"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "env: unknown command line option `--unknown'"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "env: unexpected variable found LOG_TIMESTAMP=2023-10-01 12:00:00"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        return


commands["/usr/bin/env"] = Command_env
commands["env"] = Command_env
