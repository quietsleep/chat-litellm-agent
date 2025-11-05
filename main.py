# from litellm import completion

# model = "openai/gpt-5-nano"
# model = "ollama_chat/qwen3:0.6b"
# response = completion(
#     model=model,
#     messages=[{"content": "Hello, how are you?", "role": "user"}]
# )
# print(response)

from openai import OpenAI

client = OpenAI(
    api_key="sk-1234",
    base_url="http://localhost:4000",
)
# model = "qwen3-0.6b"
# model = "gpt-5-nano"
model = "my-custom-model"
response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
print(response)

