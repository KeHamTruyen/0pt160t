import sys

from optibot_clone.config import Settings
from optibot_clone.state import read_json


SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply.

Formatting rules:
• Do not use nested bullets.
• Put citations on their own lines starting exactly with "Article URL:"."""


def main() -> None:
    settings = Settings.from_env()
    state = read_json(settings.state_path)
    store_name = settings.file_search_store_name or state.get("file_search_store_name")
    if not store_name:
        raise RuntimeError("No File Search Store found. Run `python main.py` first.")

    question = " ".join(sys.argv[1:]) or "How do I add a YouTube video?"

    from google import genai

    client = genai.Client(api_key=settings.gemini_api_key)
    strict_question = (
        f"{question}\n\n"
        "Answer in no more than 5 flat bullet points. "
        "Include any final save/preview step inside the fifth bullet if needed."
    )
    interaction = client.interactions.create(
        model=settings.gemini_model,
        input=f"{SYSTEM_PROMPT}\n\nUser question: {strict_question}",
        tools=[
            {
                "type": "file_search",
                "file_search_store_names": [store_name],
            }
        ],
    )
    print(getattr(interaction, "output_text", interaction))


if __name__ == "__main__":
    main()
