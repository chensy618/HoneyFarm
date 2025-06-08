from __future__ import annotations
import getopt
from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}

GROUPS_HELP = """Usage: groups [OPTION]... [USERNAME]...
Print group memberships for each USERNAME or, if no USERNAME is specified, for
the current process (which may differ if the groups database has changed).
      --help     display this help and exit
      --version  output version information and exit

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Full documentation at: <https://www.gnu.org/software/coreutils/groups>
or available locally via: info '(coreutils) groups invocation'\n"""

GROUPS_VERSION = """groups (GNU coreutils) 8.30
Copyright (C) 2018 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Written by David MacKenzie and James Youngman.\n"""


class Command_groups(HoneyPotCommand):
    def call(self):
        if len(self.args):
            try:
                opts, args = getopt.gnu_getopt(
                    self.args, "hvr:", ["help", "version", "regexp="]
                )
            except getopt.GetoptError as err:
                self.errorWrite(
                    f"groups: invalid option -- '{err.opt}'\nTry 'groups --help' for more information.\n"
                )
                return

            for opt in opts:
                if opt[0] == "-h" or opt[0] == "--help":
                    self.write(GROUPS_HELP)
                    return
                elif opt[0] == "-v" or opt[0] == "--version":
                    self.write(GROUPS_VERSION)
                    return

            if len(args) > 0:
                file_content = self.fs.file_contents("/etc/group")
                self.output(file_content, args[0])

        else:
            content = self.fs.file_contents("/etc/group")
            self.output(content, "")
            session_personality_response(self.protocol, self.response_groups, self.write)

    def output(self, file_content, username):
        groups_string = bytes("", encoding="utf-8")
        if not username:
            username = self.protocol.user.username
        else:
            if not self.check_valid_user(username):
                self.write(f"groups: '{username}': no such user\n")
                return
            else:
                ss = username + " : "
                groups_string = bytes(ss, encoding="utf-8")

        groups_list = []
        lines = file_content.split(b"\n")
        usr_string = bytes(username, encoding="utf-8")
        for line in lines:
            if usr_string in line:
                members = line.split(b":")
                groups_list.append(members[0])

        for g in groups_list:
            groups_string += g + b" "

        self.writeBytes(groups_string + b"\n")

    def check_valid_user(self, username):
        usr_byte = bytes(username, encoding="utf-8")
        users = self.fs.file_contents("/etc/shadow")
        lines = users.split(b"\n")
        for line in lines:
            usr_arr = line.split(b":")
            if usr_arr[0] == usr_byte:
                return True
        return False

    @staticmethod
    def response_groups(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "groups: No such user (Error code 01)"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "groups: Memberships: root, admin, sudo, docker, users"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "groups: mygroup already exists"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "groups: Invalid group name: 'mygroup'"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "groups: permission denied: cannot access `/etc/group`"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "groups: invalid group name: 'mygroup'"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "groups: does not exist: 'david'"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "groups: cannot read `/etc/group`: Permission denied"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "groups: david adm cdrom sudo dip plugdev"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "groups: General error: No such group"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "groups: Invalid argument"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "groups: Access denied: cannot read `/etc/group`"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "groups: cannot create group 'mygroup': Permission denied"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return "groups: mygroup adm cdrom sudo dip plugdev"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "groupadd: cannot create group 'mygroup': Permission denied"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "groups: Invalid option -- 'x'"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "groups: david adm cdrom sudo dip plugdev"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "groups: cannot read `/etc/group`: Permission denied"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)
                return ""

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "groups: notexist: no such user"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "groups: more than one group specified"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "groups: not a valid group name"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "groups: cannot read `/etc/group`: Permission denied"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.CONFIDENCE)

        return ""


commands["groups"] = Command_groups
commands["/bin/groups"] = Command_groups
