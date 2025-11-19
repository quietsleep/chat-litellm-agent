# Chat Litellm Agent

## Ollama

一度だけ実行すれば良い。

```sh
ollama pull qwen3:0.6b
```

## Open WebUI

```sh
DATA_DIR=~/.open-webui uvx --python 3.11 open-webui@latest serve
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

## Install

### Ollama

```sh
curl -fsSL https://ollama.com/install.sh | sh
```

### Open WebUI

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
