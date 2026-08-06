from app.ai.llm.llm_service import LLMService

service = LLMService()

answer = service.generate(
    "Explain vector databases in one sentence."
)

print(answer)