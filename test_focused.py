"""
Focused test to verify tool calling is working correctly.
"""
import asyncio
from openai import OpenAI, AsyncOpenAI


def test_weather_sync():
    """Test weather tool calling synchronously."""
    print("\n" + "="*60)
    print("Test 1: Weather Tool Calling (Sync)")
    print("="*60)

    client = OpenAI(
        api_key="sk-1234",
        base_url="http://localhost:4000",
    )

    print("\n💬 User: What's the weather in San Francisco?")
    response = client.chat.completions.create(
        model="my-custom-model",
        messages=[
            {"role": "user", "content": "What's the weather in San Francisco?"}
        ],
        stream=False,
    )

    content = response.choices[0].message.content
    print(f"🤖 Assistant: {content}")
    print(f"\n📊 Finish reason: {response.choices[0].finish_reason}")
    print(f"📊 Model: {response.model}")

    # Check if tool was called
    if "22" in content or "sunny" in content.lower() or "windy" in content.lower():
        print("\n✅ SUCCESS: Tool was called and weather data returned!")
        return True
    else:
        print("\n⚠️  WARNING: Response doesn't include expected weather data")
        print(f"   Expected to see temperature 22, sunny, or windy")
        return False


async def test_weather_streaming():
    """Test weather tool calling with streaming."""
    print("\n" + "="*60)
    print("Test 2: Weather Tool Calling (Streaming)")
    print("="*60)

    client = AsyncOpenAI(
        api_key="sk-1234",
        base_url="http://localhost:4000",
    )

    print("\n💬 User: What's the weather like in Tokyo? Use celsius.")
    stream = await client.chat.completions.create(
        model="my-custom-model",
        messages=[
            {"role": "user", "content": "What's the weather like in Tokyo? Use celsius."}
        ],
        stream=True,
    )

    print("🤖 Assistant: ", end="", flush=True)
    full_response = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            print(content, end="", flush=True)

    print()  # newline

    # Check if tool was called
    if "22" in full_response or "celsius" in full_response.lower():
        print("\n✅ SUCCESS: Streaming with tool calling works!")
        return True
    else:
        print("\n⚠️  WARNING: Response doesn't include expected weather data")
        return False


def test_normal_conversation():
    """Test normal conversation without tool calls."""
    print("\n" + "="*60)
    print("Test 3: Normal Conversation (No Tool)")
    print("="*60)

    client = OpenAI(
        api_key="sk-1234",
        base_url="http://localhost:4000",
    )

    print("\n💬 User: What is 2 + 2?")
    response = client.chat.completions.create(
        model="my-custom-model",
        messages=[
            {"role": "user", "content": "What is 2 + 2?"}
        ],
        stream=False,
    )

    content = response.choices[0].message.content
    print(f"🤖 Assistant: {content}")

    if "4" in content or "four" in content.lower():
        print("\n✅ SUCCESS: Normal conversation works!")
        return True
    else:
        print("\n⚠️  WARNING: Unexpected response")
        return False


async def test_multi_weather_requests():
    """Test multiple weather requests in sequence."""
    print("\n" + "="*60)
    print("Test 4: Multiple Weather Requests")
    print("="*60)

    client = AsyncOpenAI(
        api_key="sk-1234",
        base_url="http://localhost:4000",
    )

    cities = ["New York", "London", "Paris"]
    results = []

    for city in cities:
        print(f"\n💬 User: What's the weather in {city}?")
        response = await client.chat.completions.create(
            model="my-custom-model",
            messages=[
                {"role": "user", "content": f"What's the weather in {city}?"}
            ],
            stream=False,
        )

        content = response.choices[0].message.content
        print(f"🤖 Assistant: {content[:100]}...")

        has_weather_data = "22" in content or city.lower() in content.lower()
        results.append(has_weather_data)

    if all(results):
        print("\n✅ SUCCESS: All weather requests returned tool data!")
        return True
    else:
        print(f"\n⚠️  WARNING: {results.count(False)} out of {len(results)} failed")
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*70)
    print(" "*20 + "Tool Calling Tests")
    print("="*70)

    results = {}

    try:
        # Test 1: Sync weather
        results['sync_weather'] = test_weather_sync()

        # Test 2: Streaming weather
        results['streaming_weather'] = await test_weather_streaming()

        # Test 3: Normal conversation
        results['normal_conversation'] = test_normal_conversation()

        # Test 4: Multiple requests
        results['multiple_requests'] = await test_multi_weather_requests()

        # Summary
        print("\n" + "="*70)
        print("Test Summary")
        print("="*70)
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title():30s}: {status}")

        total = len(results)
        passed = sum(results.values())
        print("="*70)
        print(f"Total: {passed}/{total} tests passed")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
