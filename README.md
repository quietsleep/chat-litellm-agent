# Chat Litellm Agent

## Ollama

```sh
ollama pull qwen3:0.6b
```

## Open WebUI

```sh
uvx --python 3.11 open-webui serve
```

## Litellm

```sh
uv run litellm --config litellm/config.yaml --port 4000
```

## 動作確認

```sh
uv run python main.py
curl -X POST 'http://0.0.0.0:4000/chat/completions' -H 'Content-Type: application/json' -H 'Authorization: Bearer sk-1234' -d '{
    "model": "gpt-5-nano",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "what is your name?"
      }
    ]
}'
curl -s http://localhost:4000/v1/models -H "Authorization: Bearer sk-1234"
```
