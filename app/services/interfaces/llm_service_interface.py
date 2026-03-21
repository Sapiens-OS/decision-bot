from abc import ABC, abstractmethod


class ILLMService(ABC):
    """LLM service interface"""

    @abstractmethod
    async def analyze_decision(
        self,
        problem: str,
        context: dict[str, str] | None = None,
    ) -> str:
        """Analyze a decision and return structured response"""
        pass

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]]) -> str:
        """Send a chat request to the LLM"""
        pass
