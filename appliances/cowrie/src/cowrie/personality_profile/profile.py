# profile.py
from collections import Counter
from enum import IntEnum
from cowrie.personality_profile.action_mapper import map_command_to_action
from cowrie.personality_profile.personality_trait import PERSONALITY_TRAITS, INTERPRETATIONS
import shlex

class Personality(IntEnum):
    OPENNESS = 0
    CONSCIENTIOUSNESS = 1
    LOW_EXTRAVERSION = 2
    LOW_AGREEABLENESS = 3
    LOW_NEUROTICISM = 4

PERSONALITY_LABELS = {
    Personality.OPENNESS: "Openness to Experience",
    Personality.CONSCIENTIOUSNESS: "Conscientiousness",
    Personality.LOW_EXTRAVERSION: "Low Extraversion",
    Personality.LOW_AGREEABLENESS: "Low Agreeableness",
    Personality.LOW_NEUROTICISM: "Low Neuroticism",
}


def top1_personality_from_commands(commands: list[str]) -> dict | None:
    """Given a list of shell commands, infer top-1 personality trait using frequency-based scoring."""

    # calculate the frequency of each action in the commands
    actions = [map_command_to_action(cmd) for cmd in commands]
    action_counts = Counter(action for action in actions if action is not None)

    if not action_counts:
        return None

    # calculate scores for each personality trait based on the actions
    scores = Counter({
        trait: sum(
            action_counts[action]
            for action in PERSONALITY_TRAITS[PERSONALITY_LABELS[trait]]
            if action in action_counts
        )
        for trait in Personality
    })

    if not scores:
        return None

    trait, score = scores.most_common(1)[0]
    if score == 0:
        return None

    # match actions to the top trait
    matched_actions = {
        action: count
        for action, count in action_counts.items()
        if action in PERSONALITY_TRAITS[PERSONALITY_LABELS[trait]]
    }

    return {
        "trait_enum": trait,
        "trait_label": PERSONALITY_LABELS[trait],
        "matched_actions": dict(sorted(matched_actions.items())),
        "score": score,
        "interpretation": INTERPRETATIONS[PERSONALITY_LABELS[trait]]
    }

def generate_personality_report(commands: list[str]) -> str:
    """
    Given a list of observed shell commands, return a formatted personality profile report.
    """
    result = top1_personality_from_commands(commands)
    if not result:
        return "No personality trait could be inferred from the provided command list."

    report = [
        "=== Attacker Personality Profile ===",
        f"Top-1 Trait (Enum) : {result['trait_enum'].value}",
        f"Top-1 Trait Label  : {result['trait_label']}",
        f"Matched Actions    : {', '.join(result['matched_actions'])}",
        f"Match Score        : {result['score']}",
        f"Interpretation     : {result['interpretation']}"
    ]
    return "\n".join(report)

def extract_personality_from_report(report: str) -> int | None:
    """
    Extracts the Top-1 personality trait enum value from a report.
    """
    for line in report.splitlines():
        if line.startswith("Top-1 Trait (Enum)"):
            return int(line.split(":", 1)[1].strip())
    return None


def infer_personality_from_session(session) -> dict | None:
    commands = getattr(session, "pta_extracted_commands", [])
    if not commands:
        return None

    report = generate_personality_report(commands)
    trait_enum = extract_personality_from_report(report)

    return {
        "report": report,
        "trait_enum": trait_enum,
        "trait_label": PERSONALITY_LABELS[Personality(trait_enum)] if trait_enum is not None else None,
        "extracted_commands": commands
    }

def session_personality_response(protocol, response_fn, write_fn):
    """
    if user session exists personality, then call corresponding response function and output
    
    :param protocol: (self.protocol)
    :param response_fn: such as Command_grep.response_grep
    :param write_fn: self_write or cmdstack[-1].write
    """
    session = getattr(protocol.user.avatar, "session", None)
    if not (session and hasattr(session, "_personality_inferred")):
        return

    profile = session._personality_inferred
    trait_enum = profile["trait_enum"]
    emotion = protocol.emotion.get_state()

    msg = response_fn(protocol, trait_enum, emotion)
    if msg:
        write_fn(f"{msg}\n")

