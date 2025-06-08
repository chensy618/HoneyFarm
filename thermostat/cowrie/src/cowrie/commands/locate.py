from __future__ import annotations
import getopt
from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.fs import FileNotFound
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response


commands = {}

LOCATE_HELP = """Usage: locate [OPTION]... [PATTERN]...
Search for entries in a mlocate database.

  -A, --all              only print entries that match all patterns
  -b, --basename         match only the base name of path names
  -c, --count            only print number of found entries
  -d, --database DBPATH  use DBPATH instead of default database (which is
                         /var/lib/mlocate/mlocate.db)
  -e, --existing         only print entries for currently existing files
  -L, --follow           follow trailing symbolic links when checking file
                         existence (default)
  -h, --help             print this help
  -i, --ignore-case      ignore case distinctions when matching patterns
  -p, --ignore-spaces    ignore punctuation and spaces when matching patterns
  -t, --transliterate    ignore accents using iconv transliteration when
                         matching patterns
  -l, --limit, -n LIMIT  limit output (or counting) to LIMIT entries
  -m, --mmap             ignored, for backward compatibility
  -P, --nofollow, -H     don't follow trailing symbolic links when checking file
                         existence
  -0, --null             separate entries with NUL on output
  -S, --statistics       don't search for entries, print statistics about each
                         used database
  -q, --quiet            report no error messages about reading databases
  -r, --regexp REGEXP    search for basic regexp REGEXP instead of patterns
      --regex            patterns are extended regexps
  -s, --stdio            ignored, for backward compatibility
  -V, --version          print version information
  -w, --wholename        match whole path name (default)

Report bugs to https://pagure.io/mlocate. \n
"""

LOCATE_VERSION = """mlocate 0.26
Copyright (C) 2007 Red Hat, Inc. All rights reserved.
This software is distributed under the GPL v.2.

This program is provided with NO WARRANTY, to the extent permitted by law. \n
"""

LOCATE_HELP_MSG = """no search pattern specified \n"""


class Command_locate(HoneyPotCommand):
    def call(self):
        if len(self.args):
            try:
                opts, args = getopt.gnu_getopt(
                    self.args, "hvr:", ["help", "version", "regexp="]
                )
            except getopt.GetoptError as err:
                self.errorWrite(
                    f"locate: invalid option -- '{err.opt}'\nTry 'locate --help' for more information.\n"
                )
                return

            for opt in opts:
                if opt[0] == "-h" or opt[0] == "--help":
                    self.write(LOCATE_HELP)
                    return
                elif opt[0] == "-v" or opt[0] == "--version":
                    self.write(LOCATE_VERSION)
                    return
            if len(args) > 0:
                paths_list = []
                curdir = "/"
                locate_list = self.find_path(args, paths_list, curdir)
                for length in locate_list:
                    self.write(length + "\n")
                return

        else:
            self.write(LOCATE_HELP_MSG)
            return

        session_personality_response(self.protocol, self.response_locate, self.write)

    def find_path(self, args, paths_list, curdir):
        arg = args[0]
        home_dir = self.fs.listdir(curdir)
        for hf in home_dir:
            abs_path = self.fs.resolve_path(hf, curdir)
            if self.fs.isdir(hf):
                self.find_path(args, paths_list, abs_path)
            elif self.fs.isfile(abs_path):
                resolve_path = self.fs.resolve_path(hf, curdir)
                if arg in resolve_path and paths_list.count(resolve_path) == 0:
                    paths_list.append(resolve_path)

        return paths_list

    @staticmethod
    def response_locate(protocol, trait, emotion):
        """
        Emotional/personality-based response logic for 'locate'
        This response is emotion-inducing and changes state
        """
        
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "locate: Permission denied (Error code 01)"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "locate: No such file or directory (Error code 02)"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "locate: No entries found matching your query"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "locate: Unexpected error (Error code 03). Please try again"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "locate: No issues found with your query"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "locate: Searching…, please wait"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "locate: No matches found for your query"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "locate: No files found, Please check your query"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "locate: Unexpected error occurred while searching"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "locate: Found 10 files matching your query."
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "locate: No files found, please check your query"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "locate: No matches? Try again"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "locate: Uknown error occurred while searching (Error code 04)"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "locate: Found 5 files matching your query."
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "locate: No files found, please check your query"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "locate: Too many files found, please wait..."
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "locate: Unexpected error occurred while searching (Error code 05)"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "locate: Found 3 files matching your query."
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "locate: No files found, please check your query"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "locate: No matches found, please try again"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "locate: Invalid option or argument (Error code 06)"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                

        return ""


commands["locate"] = Command_locate
commands["/bin/locate"] = Command_locate
