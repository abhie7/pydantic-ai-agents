from pydantic_ai import Agent
from lmstudio_model import LMStudioModel

lmstudio_model = LMStudioModel(base_url="http://localhost:8000")

agent = Agent(
    model=lmstudio_model,
    system_prompt="Be concise, reply with one sentence.",
)

result = agent.run_sync("What is the meaning of life?")
print(result.data)