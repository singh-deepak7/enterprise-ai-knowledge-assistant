import logging

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service responsible for interacting with the chat model.
    """

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=settings.CHAT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a response from the language model.
        """

        logger.info("Generating LLM response.")

        response = self._llm.invoke(
            [
                HumanMessage(content=prompt),
            ]
        )

        logger.info("LLM response generated.")

        return response.content