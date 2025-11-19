from re import I
from typing import AsyncIterator, Iterator
import time
import json
import logging

import litellm
from litellm.types.utils import GenericStreamingChunk

# ロガーの設定
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def get_current_weather(location: str, unit: str = "celsius") -> str:
    """
    Get the current weather in a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA
        unit: The unit of temperature, either "celsius" or "fahrenheit"

    Returns:
        JSON string with weather information
    """
    # This is a mock implementation
    weather_data = {
        "location": location,
        "temperature": 22,
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_data)


# Define tools schema for function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit of temperature",
                    },
                },
                "required": ["location"],
            },
        },
    }
]

# Map of available functions
available_functions = {
    "get_current_weather": get_current_weather,
}

# model = "ollama_chat/qwen3:0.6b"
# model = "openai/gpt-5-nano"

class MyCustomLLM(litellm.CustomLLM):
    def completion(self, *args, **kwargs) -> litellm.ModelResponse:
        model = kwargs.get("model", "")
        messages = kwargs.get("messages", [])
        logger.info(f"completion called with {len(messages)} messages")
        logger.info(f"completion: kwargs keys = {list(kwargs.keys())}")
        logger.info(f"completion: model parameter = '{model}'")

        # ツール呼び出しをチェック
        response = litellm.completion(
            model=model,
            messages=messages,
            tools=tools,
        )

        # ツール呼び出しが必要な場合
        if (hasattr(response, "choices") and
            len(response.choices) > 0 and
            hasattr(response.choices[0], "finish_reason") and
            response.choices[0].finish_reason == "tool_calls" and
            hasattr(response.choices[0].message, "tool_calls") and
            response.choices[0].message.tool_calls):

            tool_calls = response.choices[0].message.tool_calls
            logger.info(f"Tool calls detected in completion: {len(tool_calls)} tool(s)")

            # メッセージに追加
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in tool_calls
                ],
            })

            # ツールを実行
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                logger.info(f"Executing tool in completion: {function_name} with args: {function_args}")

                if function_name in available_functions:
                    function_to_call = available_functions[function_name]
                    function_response = function_to_call(**function_args)
                    logger.info(f"Tool {function_name} executed successfully in completion")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response,
                    })

            # 最終応答を取得
            logger.info("Getting final response in completion")
            final_response = litellm.completion(
                model=model,
                messages=messages,
            )
            return final_response

        return response

    async def acompletion(self, *args, **kwargs) -> litellm.ModelResponse:
        model = kwargs.get("model", "")
        messages = kwargs.get("messages", [])
        logger.info(f"acompletion called with {len(messages)} messages")
        logger.info(f"acompletion: kwargs keys = {list(kwargs.keys())}")
        logger.info(f"acompletion: model parameter = '{model}'")

        # ツール呼び出しをチェック
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            tools=tools,
        )
        print(response)

        # ツール呼び出しが必要な場合
        if (hasattr(response, "choices") and
            len(response.choices) > 0 and
            hasattr(response.choices[0], "finish_reason") and
            response.choices[0].finish_reason == "tool_calls" and
            hasattr(response.choices[0].message, "tool_calls") and
            response.choices[0].message.tool_calls):

            tool_calls = response.choices[0].message.tool_calls
            logger.info(f"Tool calls detected in acompletion: {len(tool_calls)} tool(s)")

            # メッセージに追加
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in tool_calls
                ],
            })

            # ツールを実行
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                logger.info(f"Executing tool in acompletion: {function_name} with args: {function_args}")

                if function_name in available_functions:
                    function_to_call = available_functions[function_name]
                    function_response = function_to_call(**function_args)
                    logger.info(f"Tool {function_name} executed successfully in acompletion")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response,
                    })

            # 最終応答を取得
            logger.info("Getting final response in acompletion")
            final_response = await litellm.acompletion(
                model=model,
                messages=messages,
            )
            return final_response

        return response

    async def astreaming(self, *args, **kwargs) -> AsyncIterator[GenericStreamingChunk]:
        # OpenWebUIからのメッセージを取得
        model = kwargs.get("model", "")
        messages = kwargs.get("messages", [])
        logger.info(f"astreaming called with {len(messages)} messages")
        logger.info(f"astreaming: kwargs keys = {list(kwargs.keys())}")
        logger.info(f"astreaming: model parameter = '{model}'")

        # ストリーミングでツール呼び出しをチェックするかどうかの設定
        use_stream_in_initial_completion = False  # True: stream=True, False: stream=False

        # まずツール呼び出しの必要性をチェック
        logger.info(f"Checking if tool calls are needed (use_stream_in_initial_completion={use_stream_in_initial_completion})")

        if use_stream_in_initial_completion:
            # ストリーミングモード
            initial_stream = await litellm.acompletion(
                model=model,
                messages=messages,
                stream=True,
                tools=tools,
            )

            # ストリーミングレスポンスからツール呼び出しを収集
            collected_tool_calls = []
            collected_content = ""
            finish_reason = None

            async for chunk in initial_stream:
                logger.info(f"Chunk: {chunk}")
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    choice = chunk.choices[0]

                    # finish_reasonを記録
                    if hasattr(choice, "finish_reason") and choice.finish_reason:
                        finish_reason = choice.finish_reason

                    # deltaからツール呼び出しとコンテンツを収集
                    if hasattr(choice, "delta"):
                        delta = choice.delta

                        # コンテンツを収集
                        if hasattr(delta, "content") and delta.content:
                            collected_content += delta.content

                        # ツール呼び出しを収集
                        if hasattr(delta, "tool_calls") and delta.tool_calls:
                            for tool_call_delta in delta.tool_calls:
                                index = tool_call_delta.index if hasattr(tool_call_delta, "index") else 0

                                # インデックスに対応するツール呼び出しを確保
                                while len(collected_tool_calls) <= index:
                                    collected_tool_calls.append({
                                        "id": None,
                                        "type": "function",
                                        "function": {
                                            "name": "",
                                            "arguments": ""
                                        }
                                    })

                                # ツール呼び出し情報を蓄積
                                if hasattr(tool_call_delta, "id") and tool_call_delta.id:
                                    collected_tool_calls[index]["id"] = tool_call_delta.id

                                if hasattr(tool_call_delta, "type") and tool_call_delta.type:
                                    collected_tool_calls[index]["type"] = tool_call_delta.type

                                if hasattr(tool_call_delta, "function"):
                                    func = tool_call_delta.function
                                    if hasattr(func, "name") and func.name:
                                        collected_tool_calls[index]["function"]["name"] += func.name
                                    if hasattr(func, "arguments") and func.arguments:
                                        collected_tool_calls[index]["function"]["arguments"] += func.arguments

            logger.info(f"Stream collection complete. finish_reason={finish_reason}, tool_calls={len(collected_tool_calls)}")
            logger.info(f"Collected tool calls: {collected_tool_calls}")
        else:
            # 非ストリーミングモード（従来の方法）
            initial_response = await litellm.acompletion(
                model=model,
                messages=messages,
                stream=False,
                tools=tools,
            )
            logger.info(f"Non-streaming response: {initial_response}")

            # レスポンスからツール呼び出しを取得
            collected_tool_calls = []
            finish_reason = None

            if (hasattr(initial_response, "choices") and
                len(initial_response.choices) > 0):
                choice = initial_response.choices[0]

                if hasattr(choice, "finish_reason"):
                    finish_reason = choice.finish_reason

                if (hasattr(choice, "message") and
                    hasattr(choice.message, "tool_calls") and
                    choice.message.tool_calls):
                    # tool_callsを辞書形式に変換
                    for tc in choice.message.tool_calls:
                        collected_tool_calls.append({
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        })

            logger.info(f"Non-streaming collection complete. finish_reason={finish_reason}, tool_calls={len(collected_tool_calls)}")
            logger.info(f"Collected tool calls: {collected_tool_calls}")

        # ツール呼び出しが必要かチェック
        if finish_reason == "tool_calls" and collected_tool_calls:

            # ツール呼び出しを実行
            logger.info(f"Tool calls detected: {len(collected_tool_calls)} tool(s) to execute")

            # メッセージにアシスタントの応答を追加
            messages.append({
                "role": "assistant",
                "tool_calls": collected_tool_calls,
            })

            # 各ツールを実行して結果をメッセージに追加
            for tool_call in collected_tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                logger.info(f"Executing tool: {function_name} with args: {function_args}")

                if function_name in available_functions:
                    function_to_call = available_functions[function_name]
                    function_response = function_to_call(**function_args)
                    logger.info(f"Tool {function_name} executed successfully, response: {function_response}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": function_response,
                    })
                else:
                    logger.warning(f"Tool {function_name} not found in available_functions")

            # ツール呼び出し結果を踏まえて最終応答を取得 (ストリーミング)
            logger.info("Getting final response with tool results (streaming)")
            final_response = await litellm.acompletion(
                model=model,
                messages=messages,
                stream=True,
            )

            # ストリーミングレスポンスをyield
            async for chunk in final_response:
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    delta = choice.delta if hasattr(choice, "delta") else None

                    # usageの処理: Pydanticモデルの場合はmodel_dump()を使用
                    usage_dict = {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
                    if hasattr(chunk, "usage") and chunk.usage:
                        if hasattr(chunk.usage, "model_dump"):
                            usage_dict = chunk.usage.model_dump()
                        elif hasattr(chunk.usage, "dict"):
                            usage_dict = chunk.usage.dict()
                        elif isinstance(chunk.usage, dict):
                            usage_dict = chunk.usage

                    generic_streaming_chunk: GenericStreamingChunk = {
                        "finish_reason": choice.finish_reason if hasattr(choice, "finish_reason") else None,
                        "index": choice.index if hasattr(choice, "index") else 0,
                        "is_finished": choice.finish_reason is not None if hasattr(choice, "finish_reason") else False,
                        "text": delta.content if delta and hasattr(delta, "content") and delta.content else "",
                        "tool_use": None,
                        "usage": usage_dict,
                    }
                    yield generic_streaming_chunk
            logger.info("Tool-based streaming response completed")
        else:
            # ツール呼び出しが不要な場合は通常のストリーミング応答
            logger.info("No tool calls needed, proceeding with normal streaming response")
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                stream=True,
            )

            async for chunk in response:
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    delta = choice.delta if hasattr(choice, "delta") else None

                    # usageの処理: Pydanticモデルの場合はmodel_dump()を使用
                    usage_dict = {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
                    if hasattr(chunk, "usage") and chunk.usage:
                        if hasattr(chunk.usage, "model_dump"):
                            usage_dict = chunk.usage.model_dump()
                        elif hasattr(chunk.usage, "dict"):
                            usage_dict = chunk.usage.dict()
                        elif isinstance(chunk.usage, dict):
                            usage_dict = chunk.usage

                    generic_streaming_chunk: GenericStreamingChunk = {
                        "finish_reason": choice.finish_reason if hasattr(choice, "finish_reason") else None,
                        "index": choice.index if hasattr(choice, "index") else 0,
                        "is_finished": choice.finish_reason is not None if hasattr(choice, "finish_reason") else False,
                        "text": delta.content if delta and hasattr(delta, "content") and delta.content else "",
                        "tool_use": None,
                        "usage": usage_dict,
                    }
                    yield generic_streaming_chunk
            logger.info("Normal streaming response completed")


my_custom_llm = MyCustomLLM()
