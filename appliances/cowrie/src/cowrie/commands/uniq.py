# Copyright (c) 2020 Peter Sufliarsky <sufliarskyp@gmail.com>
# See the COPYRIGHT file for more information

"""
uniq command
"""

from __future__ import annotations

from twisted.python import log

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}

UNIQ_HELP = """Usage: uniq [OPTION]... [INPUT [OUTPUT]]
Filter adjacent matching lines from INPUT (or standard input),
writing to OUTPUT (or standard output).

With no options, matching lines are merged to the first occurrence.

Mandatory arguments to long options are mandatory for short options too.
  -c, --count           prefix lines by the number of occurrences
  -d, --repeated        only print duplicate lines, one for each group
  -D                    print all duplicate lines
      --all-repeated[=METHOD]  like -D, but allow separating groups
                                 with an empty line;
                                 METHOD={none(default),prepend,separate}
  -f, --skip-fields=N   avoid comparing the first N fields
      --group[=METHOD]  show all items, separating groups with an empty line;
                          METHOD={separate(default),prepend,append,both}
  -i, --ignore-case     ignore differences in case when comparing
  -s, --skip-chars=N    avoid comparing the first N characters
  -u, --unique          only print unique lines
  -z, --zero-terminated     line delimiter is NUL, not newline
  -w, --check-chars=N   compare no more than N characters in lines
      --help     display this help and exit
      --version  output version information and exit

A field is a run of blanks (usually spaces and/or TABs), then non-blank
characters.  Fields are skipped before chars.

Note: 'uniq' does not detect repeated lines unless they are adjacent.
You may want to sort the input first, or use 'sort -u' without 'uniq'.
Also, comparisons honor the rules specified by 'LC_COLLATE'.

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Full documentation at: <https://www.gnu.org/software/coreutils/uniq>
or available locally via: info '(coreutils) uniq invocation'
"""


class Command_uniq(HoneyPotCommand):
    last_line: bytes | None = None

    def start(self) -> None:
        if "--help" in self.args:
            self.writeBytes(UNIQ_HELP.encode())
            self.exit()
        elif self.input_data:
            lines = self.input_data.split(b"\n")
            if not lines[-1]:
                lines.pop()
            for line in lines:
                self.grep_input(line)
            session_personality_response(self.protocol, self.response_uniq, self.write)
            self.exit()

    def lineReceived(self, line: str) -> None:
        log.msg(
            eventid="cowrie.command.input",
            realm="uniq",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )
        self.grep_input(line.encode())

    def handle_CTRL_D(self) -> None:
        self.exit()

    def grep_input(self, line: bytes) -> None:
        if not line == self.last_line:
            self.writeBytes(line + b"\n")
            self.last_line = line

    @staticmethod
    def response_uniq(protocol, trait, emotion):
        """
        Emotional/personality-based response logic for 'uniq'
        This response is emotion-inducing and changes state
        """

        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uniq: No such file or directory"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uniq: Permission denied"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "unqi: Unrecognized option '--xyz'"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uniq: Write error: No space left on device"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uniq: unrecognized input format. Try again with --help"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uniq: Unexpected character encoding found"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uniq: No such file or directory"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uniq: unknown error occurred\n"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uniq: permission denied"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uniq: Invalid option '-h'"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uniq: Fatal error occurred (Error code: 124) "
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "uniq: unknown error occurred\n"

        elif trait == LOW_AGREEABLENESS:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uniq: input stream may not be sorted"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uniq: permission denied"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uniq: unknown error occurred"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return ""
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Found something dangerous"

        elif trait == LOW_NEUROTICISM:
            if emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "uniq: Invalid command"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uniq: Unknown input"
            elif emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "uniq: No such file"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "uniq: Unrecognized option"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "uniq: Unknown error"

        return ""

commands["/usr/bin/uniq"] = Command_uniq
commands["uniq"] = Command_uniq
