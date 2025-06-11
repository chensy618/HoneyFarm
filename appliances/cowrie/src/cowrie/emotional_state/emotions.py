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
        return self.state.name

    def emotion_loop(self, current_emotion: Emotion):
        """
        This method can be expanded to implement a loop that changes the emotional state
        based on certain conditions or events in the session.
        """
        if current_emotion == Emotion.CONFIDENCE:
            # Example condition to change state
            self.set_state(Emotion.SURPRISE)
            next_emotion = self.get_state()
            return next_emotion 
        elif current_emotion == Emotion.SURPRISE:
            self.set_state(Emotion.CONFUSION)
            next_emotion = self.get_state()
            return next_emotion 
        elif current_emotion == Emotion.CONFUSION:
            self.set_state(Emotion.FRUSTRATION)
            next_emotion = self.get_state()
            return next_emotion 
        elif current_emotion == Emotion.FRUSTRATION:
            self.set_state(Emotion.SELF_DOUBT)
            next_emotion = self.get_state()
            return next_emotion 
        elif current_emotion == Emotion.SELF_DOUBT:
            self.set_state(Emotion.CONFIDENCE)
            next_emotion = self.get_state()
            return next_emotion 
        


if __name__ == "__main__":
    # Example usage
    session_emotion = EmotionalState()
    print(f"Initial emotion: {session_emotion}")

    session_emotion.set_state(Emotion.CONFUSION)
    print(f"Updated emotion: {session_emotion}")

    if session_emotion.get_state() == Emotion.CONFUSION:
        print("Trigger CONFUSION-related honeypot response")


