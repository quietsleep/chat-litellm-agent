from typing import AsyncIterator, Iterator
import time

import litellm
from litellm.types.utils import GenericStreamingChunk


class MyCustomLLM(litellm.CustomLLM):
    def completion(self, *args, **kwargs) -> litellm.ModelResponse:
        return litellm.completion(
            model="ollama_chat/qwen3:0.6b",
            messages=[{"role": "user", "content": "Hello world"}],
            mock_response="Hi!",
        )  # type: ignore

    async def acompletion(self, *args, **kwargs) -> litellm.ModelResponse:
        return await litellm.acompletion(
            model="ollama_chat/qwen3:0.6b",
            messages=[{"role": "user", "content": "Hello world"}],
            mock_response="Hi!",
        )  # type: ignore

    def streaming(self, *args, **kwargs) -> Iterator[GenericStreamingChunk]:
            generic_streaming_chunk: GenericStreamingChunk = {
                "finish_reason": "stop",
                "index": 0,
                "is_finished": True,
                "text": str(int(time.time())),
                "tool_use": None,
                "usage": {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0},
            }
            return generic_streaming_chunk # type: ignore

    async def astreaming(self, *args, **kwargs) -> AsyncIterator[GenericStreamingChunk]:
        generic_streaming_chunk: GenericStreamingChunk = {
            "finish_reason": "stop",
            "index": 0,
            "is_finished": True,
            "text": str(int(time.time())),
            "tool_use": None,
            "usage": {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0},
        }
        yield generic_streaming_chunk # type: ignore


my_custom_llm = MyCustomLLM()
