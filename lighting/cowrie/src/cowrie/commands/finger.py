from __future__ import annotations

import datetime
import getopt

from cowrie.shell.command import HoneyPotCommand
from cowrie.emotional_state.emotions import Emotion
from cowrie.personality_profile.profile import Personality
from cowrie.personality_profile.profile import session_personality_response

commands = {}

FINGER_HELP = """Usage:"""


class Command_finger(HoneyPotCommand):
    def call(self):
        time = datetime.datetime.utcnow()
        user_data = []
        # Get all user data and convert to string
        all_users_byte = self.fs.file_contents("/etc/passwd")
        all_users = all_users_byte.decode("utf-8")
        # Convert all new lines to : character
        all_users = all_users.replace("\n", ":")
        # Convert into list by splitting string
        all_users_list = all_users.split(":")
        # Loop over the data in sets of 7
        for i in range(0, len(all_users_list), 7):
            x = i
            # Ensure any added list contains data and is not a blank space by >
            if len(all_users_list[x : x + 7]) != 1:
                # Take the next 7 elements and put them a list, then add to 2d>
                user_data.append(all_users_list[x : x + 7])
        # THIS CODE IS FOR DEBUGGING self.write(str(user_data))

        # If finger called without args
        if len(self.args) == 0:
            self.write("Login\tName\tTty  Idle\tLogin Time  Office  Office Phone\n")
            for i in range(len(user_data)):
                if len(str(user_data[i][0])) > 6:
                    if len(str(user_data[i][4])) > 6:
                        self.write(
                            "{}+ {}+ *:{}\t\t{} (:{})\n".format(
                                str(user_data[i][0])[:6],
                                str(user_data[i][4])[:6],
                                str(user_data[i][2]),
                                str(time.strftime("%b %d %H:%M")),
                                str(user_data[i][3]),
                            )
                        )
                    else:
                        self.write(
                            "{}+ {}\t*:{}\t\t{} (:{})\n".format(
                                str(user_data[i][0])[:6],
                                str(user_data[i][4]),
                                str(user_data[i][2]),
                                str(time.strftime("%b %d %H:%M")),
                                str(user_data[i][3]),
                            )
                        )
                else:
                    if len(str(user_data[i][4])) > 6:
                        self.write(
                            "{}\t{}+ *:{}\t\t{} (:{})\n".format(
                                str(user_data[i][0]),
                                str(user_data[i][4])[:6],
                                str(user_data[i][2]),
                                str(time.strftime("%b %d %H:%M")),
                                str(user_data[i][3]),
                            )
                        )
                    else:
                        self.write(
                            "{}\t{}\t*:{}\t\t{} (:{})\n".format(
                                str(user_data[i][0]),
                                str(user_data[i][4]),
                                str(user_data[i][2]),
                                str(time.strftime("%b %d %H:%M")),
                                str(user_data[i][3]),
                            )
                        )
                # self.write(f"name: %20." + str(user_data[i][0]) + "\n")      >
            # time = datetime.datetime.utcnow()
            # self.write("{}\n".format(time.strftime("%a %b %d %H:%M:%S UTC %Y">
            return

        try:
            opts, args = getopt.gnu_getopt(self.args, "")
        except getopt.GetoptError as err:
            self.errorWrite(
                f"""finger: invalid option -- '{err.opt}'
usage: finger [-lmps] [login ...]\n"""
            )
            return

        # If args given not any predefined, assume is username
        if len(args) > 0:
            for i in range(len(user_data)):
                # Run if check to check if user is real
                if args[0] == user_data[i][0]:
                    # Display user data
                    self.write(
                        """Login: """
                        + str(user_data[i][0])
                        + """                               Name: """
                        + str(user_data[i][4])
                        + """
Directory: """
                        + str(user_data[i][5])
                        + """             Shell: """
                        + str(user_data[i][6])
                        + """
On since """
                        + str(time.strftime("%a %b %d %H:%M"))
                        + """ (UTC) on :0 from :0 (messages off)
No mail.
No Plan.
"""
                    )
                    
                    session_personality_response(self.protocol, self.response_finger, self.write)
                    
                    return
                    
            # If user is NOT real inform user
            self.write(f"finger: {args[0]}: no such user\n")

            # IF TIME ALLOWS: Seperate into multiple functions
            # IF TIME ALLOWS: Make my comments more concise and remove debuggi>
            return
        # Base.py has some helpful stuff
        return

    @staticmethod
    def response_finger(protocol, trait, emotion):
        if trait == Personality.OPENNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "finger: User not found"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "finger: Unknownuser: no such user"
            elif emotion == Emotion.CONFUSION:
                return "finger: Syntax incomplete"

        elif trait == Personality.CONSCIENTIOUSNESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "finger: Login: guest       Name: ??\nDirectory: /tmp  Shell: /bin/sh\nLast"
            elif emotion == Emotion.SELF_DOUBT:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "finger: Could not find the directory, Check the shell path again."
            elif emotion == Emotion.FRUSTRATION:
                return "finger: unexpected response format. (Error code: 8)"

        elif trait == Personality.LOW_EXTRAVERSION:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.SURPRISE)
                return "finger: user record not indexed properly. (Error code: 2)"
            elif emotion == Emotion.SURPRISE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "finger: Login: partycrasher   Name: Unknown but online!\nLocation: 172.31.0.66"
            elif emotion == Emotion.CONFUSION:
                return "finger: User not found in the system. (Error code: 3)"

        elif trait == Personality.LOW_AGREEABLENESS:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.FRUSTRATION)
                return "finger: You are not allowed to view this user's information"
            elif emotion == Emotion.FRUSTRATION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "finger: You don't have permission to access this user's data"
            elif emotion == Emotion.SELF_DOUBT:
                return "finger: This user has restricted access. (Error code: 4)"

        elif trait == Personality.LOW_NEUROTICISM:
            if emotion == Emotion.CONFIDENCE:
                protocol.emotion.set_state(Emotion.CONFUSION)
                return "finger: User not found in the system. (Error code: 5)"
            elif emotion == Emotion.CONFUSION:
                protocol.emotion.set_state(Emotion.SELF_DOUBT)
                return "finger: Unexpected user data format. (Error code: 6)"
            elif emotion == Emotion.SELF_DOUBT:
                return "finger: Error retrieving user information. (Error code: 7)"

        return ""


commands["bin/finger"] = Command_finger
commands["finger"] = Command_finger
