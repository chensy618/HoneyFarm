# action_mapper.py
# Mapping based on Odemis et al. (2022) attacker behavior taxonomy

# Action → Set of shell commands
ACTIONS_TO_COMMANDS = {
    "A1": {"bash", "busybox", "sh","./script.sh"},
    "A2": {},
    "A3": {},
    "A4": {"dd", "ethtool"},
    "A5": {"chpasswd"},
    "A6": {},
    "A7": {},
    "A8": {"nc"},
    "A9": {"awk", "cat", "locate", "uniq", "wc"},
    "A10": {},
    "A11": {},
    "A12": {"curl", "ftpget", "tftp", "wget"},
    "A13": {"apt", "gcc", "yum"},
    "A14": {"sleep"},
    "A15": {"dd", "du", "fs", "ls", "tar", "ulimit", "unzip"},
    "A16": {"git", "tee"},
    "A17": {},
    "A18": {"crontab", "nc", "nohup", "perl", "python"},
    "A19": {"uname"},
    "A20": {"cat", "env", "free", "iptables", "lspci", "service", "uptime", "which"},
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


