# personality_trait.py

# Mapping from personality trait to associated A# actions
PERSONALITY_TRAITS = {
    "Openness to Experience": {"A4", "A7", "A9", "A15", "A19", "A20", "A21", "A22"},
    "Conscientiousness": {"A5", "A10", "A15", "A20"},
    "Low Extraversion": {"A3", "A7", "A15"},
    "Low Agreeableness": {"A10", "A11", "A13"},
    "Low Neuroticism": {"A9", "A19", "A20"},
}

# Interpretation text for each trait
INTERPRETATIONS = {
    "Openness to Experience": "Curious, explores system/network structure, gathers diverse information.",
    "Conscientiousness": "Careful and methodical; plans actions and gathers information in a structured way.",
    "Low Extraversion": "Introspective, avoids public attention, focuses on reconnaissance and stealth.",
    "Low Agreeableness": "Potentially malicious or self-serving behavior, such as tool installation or system modification.",
    "Low Neuroticism": "Emotionally stable, gathers information logically and efficiently."
}

def get_actions_for_trait(trait: str) -> set[str]:
    return PERSONALITY_TRAITS.get(trait, set())

def get_interpretation(trait: str) -> str:
    return INTERPRETATIONS.get(trait, "No interpretation available.")
