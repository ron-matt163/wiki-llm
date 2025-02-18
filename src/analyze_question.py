import json
import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from dotenv import load_dotenv

load_dotenv()

def get_wikipedia_topics(question: str, model_name: str = "gpt-4o-mini") -> list:
    """
    Uses an LLM to determine relevant Wikipedia topics for a given question.

    :param question: The user question.
    :param model_name: The OpenAI model to use (default is "gpt-4").
    :return: A list of Wikipedia topics.
    """

    llm = ChatOpenAI(model_name=model_name, openai_api_key= os.getenv("OPENAI_API_KEY"))
    
    prompt = """
    You are an AI assistant that identifies relevant Wikipedia topics for a given question.
    Return a JSON object in the following format:
    {{
        "topics": ["Topic 1", "Topic 2", "Topic 3"]
    }}

    Examples:
    Question: "What are the effects of climate change?"
    Response:
    {{
        "topics": ["Climate change", "Global warming", "Greenhouse gases", "Sea level rise"]
    }}

    Question: "Who invented the steam engine?"
    Response:
    {{
        "topics": ["James Watt", "Steam engine", "Industrial Revolution"]
    }}

    Now, answer the following:
    Question: {}
    Response:
    """.format(question)

    response = llm([HumanMessage(content=prompt)])
    
    try:
        print("Response content:", response.content)
        topics = json.loads(response.content).get("topics", [])
        if not isinstance(topics, list):
            raise ValueError("Invalid format: 'topics' should be a list")
        return topics
    except (json.JSONDecodeError, ValueError) as e:
        print("Unexpected response format:", response.content)
        return []


if __name__ == "__main__":
    question = "How many goals did Erling Haaland score in the 2023/24 season?"
    topics = get_wikipedia_topics(question)

    print("\nRelevant Wikipedia Topics:\n")
    for topic in topics:
        print(topic)