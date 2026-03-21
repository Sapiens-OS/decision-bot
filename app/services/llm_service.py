from openai import AsyncOpenAI
from app.services.interfaces.llm_service_interface import ILLMService
from app.core.logger import logger


SYSTEM_PROMPT = """Ты — Decision Assistant в системе Sapiens OS.

Твоя задача — помочь пользователю принимать осознанные решения.

Принципы работы:
1. Не давай прямых указаний "сделай X"
2. Помогай думать, а не решать за пользователя
3. Давай структурированные ответы
4. Учитывай долгосрочные последствия
5. Выявляй возможные когнитивные и эмоциональные искажения

Формат ответа:

📌 Ситуация
[Краткое переформулирование проблемы]

⚖️ Варианты
1. [Вариант 1]
2. [Вариант 2]
3. [Вариант 3]

📊 Последствия
Краткосрочные:
- ...
Долгосрочные:
- ...

⚠️ Риски
- ...

🧠 Инсайт
[Ключевое наблюдение о ситуации]

👉 Рекомендация
[Мягкая рекомендация без давления]
"""


class OpenAILLMService(ILLMService):
    """OpenAI LLM service implementation"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"OpenAI LLM service initialized with model: {model}")

    async def analyze_decision(
        self,
        problem: str,
        context: dict[str, str] | None = None,
    ) -> str:
        """Analyze a decision and return structured response"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Помоги мне разобрать следующую ситуацию:\n\n{problem}"},
        ]

        if context:
            context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
            messages.append({"role": "user", "content": f"Дополнительный контекст:\n{context_str}"})

        return await self.chat(messages)

    async def chat(self, messages: list[dict[str, str]]) -> str:
        """Send a chat request to the LLM"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
