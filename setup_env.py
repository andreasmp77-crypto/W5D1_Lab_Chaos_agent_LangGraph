# setup_env.py
from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


def main():
    # 1) Load environment variables from .env (if present)
    load_dotenv()

    # 2) Read the OPENAI_API_KEY from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY is not set.")
        return

    print("OPENAI_API_KEY found.")

    # 3) Try creating a ChatOpenAI model using that key
    model = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=openai_api_key,
    )

    # 4) Make a tiny test call to confirm everything works
    test_prompt = "Say 'hello' in one word."
    response = model.invoke([HumanMessage(content=test_prompt)])
    print("Model response:", response.content)

    print("Setup OK: model created, imports working, API key valid.")


if __name__ == "__main__":
    main()