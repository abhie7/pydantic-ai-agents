from pydantic_ai.models import Model, AgentModel
from pydantic_ai.messages import ModelMessage, ModelResponse, ModelRequest, ModelResponsePart
from pydantic_ai.settings import ModelSettings
from pydantic_ai.result import Usage
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import httpx

class LMStudioModel(Model):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def agent_model(
        self,
        *,
        function_tools: list,
        allow_text_result: bool,
        result_tools: list,
    ) -> AgentModel:
        return LMStudioAgentModel(self.base_url)

    def name(self) -> str:
        return "lmstudio"

class LMStudioAgentModel(AgentModel):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def request(
        self, messages: list[ModelMessage], model_settings: ModelSettings | None
    ) -> tuple[ModelResponse, Usage]:
        async with httpx.AsyncClient() as client:
            json_messages = []
            for message in messages:
                if isinstance(message, ModelRequest):
                    json_messages.append({
                        "kind": message.kind,
                        "parts": [{"part_kind": part.part_kind, "content": part.content} for part in message.parts]
                    })
                elif isinstance(message, ModelResponse):
                    json_messages.append({
                        "kind": message.kind,
                        "parts": [{"part_kind": part.part_kind, "content": part.content} for part in message.parts]
                    })
            response = await client.post(f"{self.base_url}/api/v1/generate", json={"messages": json_messages})
            response_data = response.json()
            return ModelResponse(parts=[ModelResponsePart(part_kind="text", content=response_data["text"])]), Usage()

    @asynccontextmanager
    async def request_stream(
        self, messages: list[ModelMessage], model_settings: ModelSettings | None
    ) -> AsyncIterator:
        raise NotImplementedError("Streaming not supported for LMStudio")