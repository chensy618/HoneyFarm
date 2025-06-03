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
        from cowrie.emotional_state.emotions import Emotion

        if trait.name == "OPENNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.CURIOSITY)
                return "Unique lines, like ideas, only stand out when they're together."
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Even one match can be meaningful."
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "Pattern filtered. Insights remain."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CALM)
                return "Duplicates are gone. Clean view ahead."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.FOCUS)
                return "Didn't expect so many repeats, did you?"

        elif trait.name == "CONSCIENTIOUSNESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Let's strip away the noise and keep only what matters."
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.FOCUS)
                return "Duplicates filtered. Structure improved."
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SATISFACTION)
                return "Clean data. Just how you like it."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CALM)
                return "Let's tidy this up and move forward."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.REFLECTION)
                return "A surprise duplicate is still a pattern."

        elif trait.name == "EXTRAVERSION":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Let's find the unique ones that stand out!"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CURIOSITY)
                return "There's value in the outliers!"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SATISFACTION)
                return "Filtered and fabulous!"
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "Brush it off, we've got this."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.ENTHUSIASM)
                return "Whoa! That one kept showing up, huh?"

        elif trait.name == "AGREEABLENESS":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.HELPFULNESS)
                return "Need help spotting the differences?"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.OPTIMISM)
                return "Each line matters. Let's keep going."
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.SATISFACTION)
                return "Clean list, clean mind!"
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.PATIENCE)
                return "Let's take it one line at a time."
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.HELPFULNESS)
                return "Found something odd? Let's look into it."

        elif trait.name == "NEUROTICISM":
            if emotion.name == "CONFUSION":
                protocol.emotion.set_state(Emotion.ANXIETY)
                return "Why so many duplicates? Is something wrong?"
            elif emotion.name == "SELF_DOUBT":
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "Was I too strict? Or not strict enough?"
            elif emotion.name == "CONFIDENCE":
                protocol.emotion.set_state(Emotion.CAUTIOUS)
                return "Okay… the output looks fine. I think."
            elif emotion.name == "FRUSTRATION":
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "It shouldn't be this messy… right?"
            elif emotion.name == "SURPRISE":
                protocol.emotion.set_state(Emotion.MISTRUST)
                return "That line again? Is this thing rigged?"

        return ""

commands["/usr/bin/uniq"] = Command_uniq
commands["uniq"] = Command_uniq
