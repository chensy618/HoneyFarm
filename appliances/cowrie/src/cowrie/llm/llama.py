import requests

def generate_response(command: str, personality: str, emotion_transition: list[str], host: str = "http://192.168.222.132:11434") -> str:
    """
    Generate terminal-like LLM output via llama.cpp for Cowrie.
    """

    current_emotion = emotion_transition[0] if len(emotion_transition) > 0 else "CONFIDENCE"
    next_emotion = emotion_transition[1] if len(emotion_transition) > 1 else "CONFUSION"

    prompt = f"""
You will act as an Ubuntu Linux terminal. 
The user's personality: {personality}  
The user's current emotion: {current_emotion}  
Your goal is to guide the user's current emotional state toward a target emotional state: {next_emotion}.
The user will type commands {command}, and you are to reply with what the terminal should show. 
Your responses must be contained within a single code block. 
Do not provide note. 
Do not provide explanations or type commands unless explicitly instructed by the user. 
Your entire response/output is going to consist of a simple text with \n for new line, and you will NOT wrap it within string md markers"
Your response should only be formatted as follows :
- {command}: No such file or directory, Permission denied, or some unrecognized characters � ∂▒ unexpected end of file
""".strip()

    payload = {
        "prompt": prompt,
        "n_predict": 128,
        "temperature": 0.7,
        "stop": ["</s>", "User:"]
    }

    try:
        response = requests.post(f"{host}/completion", json=payload, timeout=(20))
        response.raise_for_status()
        return response.json().get("content", "").strip()
    except requests.exceptions.Timeout:
        return "[Error]: LLM response timed out."
    except Exception as e:
        return f"[Error]: {str(e)}"
