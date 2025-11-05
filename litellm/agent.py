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
        # OpenWebUIからのメッセージを取得
        messages = kwargs.get("messages", [])

        # litellmのacompletionを使ってollama/qwen3:0.6bでストリーミング応答
        response = await litellm.acompletion(
            model="ollama_chat/qwen3:0.6b",
            messages=messages,
            stream=True,
        )

        # ストリーミングレスポンスをyield
        async for chunk in response:
            if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                choice = chunk.choices[0]
                delta = choice.delta if hasattr(choice, "delta") else None

                generic_streaming_chunk: GenericStreamingChunk = {
                    "finish_reason": choice.finish_reason if hasattr(choice, "finish_reason") else None,
                    "index": choice.index if hasattr(choice, "index") else 0,
                    "is_finished": choice.finish_reason is not None if hasattr(choice, "finish_reason") else False,
                    "text": delta.content if delta and hasattr(delta, "content") and delta.content else "",
                    "tool_use": None,
                    "usage": chunk.usage._asdict() if hasattr(chunk, "usage") and chunk.usage else {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0},
                }
                yield generic_streaming_chunk


my_custom_llm = MyCustomLLM()
