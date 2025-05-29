from enum import Enum, auto

class Emotion(Enum):
    CONFUSION = auto()
    SELF_DOUBT = auto()
    CONFIDENCE = auto()
    FRUSTRATION = auto()
    SURPRISE = auto()

class EmotionalState:
    def __init__(self):
        self.state = Emotion.CONFIDENCE  # default starting emotion

    def set_state(self, new_state: Emotion):
        self.state = new_state

    def get_state(self) -> Emotion:
        return self.state

    def __str__(self):
        return self.state.name.lower()


if __name__ == "__main__":
    # Example usage
    session_emotion = EmotionalState()
    print(f"Initial emotion: {session_emotion}")

    session_emotion.set_state(Emotion.CONFUSION)
    print(f"Updated emotion: {session_emotion}")

    if session_emotion.get_state() == Emotion.CONFUSION:
        print("Trigger CONFUSION-related honeypot response")


