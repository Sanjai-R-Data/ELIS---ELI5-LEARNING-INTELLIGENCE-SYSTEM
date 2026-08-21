import ollama
MODEL_NAME = "qwen2.5:1.5b-instruct"
def generate_response(prompt: str) -> str:
    response = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt,
    )

    return response["response"]