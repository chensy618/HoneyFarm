# action_mapper.py
# Mapping based on Odemis et al. (2022) attacker behavior taxonomy

# Action → Set of shell commands
ACTIONS_TO_COMMANDS = {
    "A1": {"alias", "bash", "busybox", "sh","./script.sh"},
    "A2": {},
    "A3": {},
    "A4": {"dd", "ethtool"},
    "A5": {"passwd", "chpasswd"},
    "A6": {},
    "A7": {"ifconfig", "ip", "route", "netstat", "ss", "iptables", "ip6tables"},
    "A8": {"nc", "nmap", "ping", "telnet", "traceroute"},
    "A9": {"awk", "cat", "locate", "uniq", "wc", "grep", "tail", "head"},
    "A10": {},
    "A11": {"rm", "mv", "rmdir", "unset", "kill", "killall", "pkill", "killall5"},
    "A12": {"curl", "ftpget", "tftp", "wget"},
    "A13": {"apt", "gcc", "yum"},
    "A14": {"sleep"},
    "A15": {"dd", "du", "cd", "rm", "cp", "mv", "mkdir", "rmdir", "ls", "tar", "ulimit", "unzip", "chown", "chgrp", "chattr", "chmod"},
    "A16": {"git", "tee", "mkdir", "touch", "vi", "nano", "vim", "emacs", "do", "done", "echo"},
    "A17": {"unmask", "unset", "rm", "mv", "history ", "shred", "wipe", "logroate", "umount"},
    "A18": {"crontab", "nc", "nohup", "perl", "python"},
    "A19": {"uname", "uptime", "hostnamectl", "cat"},
    "A20": {"cat", "env", "free", "iptables", "lspci", "service", "uptime", "which", "whoami", "jobs", "ps"},
    "A21": {"ethtool", "ifconfig", "netstat", "ping"},
    "A22": {"finger", "groups", "last"},
}

# Automatically generate Command → Action mapping
COMMAND_TO_ACTION = {}
for action, commands in ACTIONS_TO_COMMANDS.items():
    for cmd in commands:
        COMMAND_TO_ACTION[cmd] = action

def map_command_to_action(command: str) -> str | None:
    """Returns the action code (A#) corresponding to a shell command."""
    return COMMAND_TO_ACTION.get(command)

def get_commands_by_action(action: str) -> set[str]:
    """Returns a set of shell commands associated with a specific action code."""
    return ACTIONS_TO_COMMANDS.get(action, set())

