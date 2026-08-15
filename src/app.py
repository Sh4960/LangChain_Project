# from netfree_unstrict_ssl import unstrict_ssl
# unstrict_ssl()

# from dotenv import load_dotenv
# load_dotenv()

# from agents import chat

# def main() -> None:
#     print('simulate chat')
#     result = chat.answer("what's your name", "default")
#     print(result.text)

# if __name__ == "__main__":
#     main()



from netfree_unstrict_ssl import unstrict_ssl

unstrict_ssl()

from dotenv import load_dotenv

load_dotenv()

from agents import chat
from core.store import store


def main() -> None:
    print("simulate chat...")

    # הוספת מסמך דוגמה כדי לבדוק שה-RAG עובד
    store.add(
        name="intro.md",
        content="LangChain is a framework for developing applications powered by language models.",
    )

    result = chat.answer("What is LangChain according to the sources?", "default")
    print("\n--- Answer ---")
    print(result.text)


if __name__ == "__main__":
    main()