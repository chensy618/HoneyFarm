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
    """Given a list of shell commands, infer top-1 personality trait."""
    observed_actions = {map_command_to_action(cmd) for cmd in commands}
    observed_actions.discard(None)

    scores = Counter({
        trait: len(PERSONALITY_TRAITS[PERSONALITY_LABELS[trait]] & observed_actions)
        for trait in Personality
    })

    if not scores:
        return None

    trait, score = scores.most_common(1)[0]
    if score == 0:
        return None

    return {
        "trait_enum": trait,
        "trait_label": PERSONALITY_LABELS[trait],
        "matched_actions": sorted(PERSONALITY_TRAITS[PERSONALITY_LABELS[trait]] & observed_actions),
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



