import requests

def generate_response(command: str, personality: str, emotion_transition: list[str], host: str = "http://192.168.222.132:11434") -> str:
    """
    Generate terminal-like LLM output via llama.cpp for Cowrie.
    """

    current_emotion = emotion_transition[0] if len(emotion_transition) > 0 else "CONFIDENCE"
    next_emotion = emotion_transition[1] if len(emotion_transition) > 1 else "CONFUSION"

    prompt = f"""
You are simulating a Linux shell terminal.

The user typed the command: {command}

Shell user's personality: {personality}  
Current emotion: {current_emotion}  
Expected transition: {next_emotion}

Instructions:
- Return only what a real Linux terminal would show.
- Do NOT describe emotion, do NOT include interpretation.
- Simulate subtle instability: errors, garbled characters, misaligned content, permission issues, or strange behavior.
- Output should appear natural and imperfect, mimicking terminal quirks.

Example behaviors:
- cat: /etc/passwd: No such file or directory
- tmp✖log.txt
- Permission denied
- config.json: � ∂▒ unexpected end of file

Now simulate the terminal output of running: `{command}`
""".strip()

    payload = {
        "prompt": prompt,
        "n_predict": 128,
        "temperature": 0.7,
        "stop": ["</s>", "User:"]
    }

    try:
        response = requests.post(f"{host}/completion", json=payload, timeout=(5, 20))
        response.raise_for_status()
        return response.json().get("content", "").strip()
    except requests.exceptions.Timeout:
        return "[Error]: LLM response timed out."
    except Exception as e:
        return f"[Error]: {str(e)}"
