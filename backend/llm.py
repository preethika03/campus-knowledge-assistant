import os

from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in the .env file."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# MODEL
# =========================================================

MODEL_NAME = "gemini-3.5-flash-lite"


# =========================================================
# GENERATE ANSWER
# =========================================================

def generate_answer(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the generated answer.
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("GEMINI API TEST")
    print("=" * 70)

    test_prompt = """
Answer this question in one sentence:

What is a Retrieval-Augmented Generation system?
"""

    try:

        answer = generate_answer(test_prompt)

        print("\nGemini response:")
        print(answer)

        print("\n" + "=" * 70)
        print("GEMINI API TEST SUCCESSFUL")
        print("=" * 70)

    except Exception as error:

        print("\nGemini API test failed.")
        print(f"Error: {error}")