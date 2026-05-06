from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os

def get_llm(provider: str = "openai", model_name: str = "gpt-4o-mini", temperature: float = 0.0):
    """
    Factory method to return a provider-agnostic LangChain ChatModel.
    """
    provider = provider.lower()
    if provider == "openai":
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY", "mock_key")
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model_name=model_name,
            temperature=temperature,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "mock_key")
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
