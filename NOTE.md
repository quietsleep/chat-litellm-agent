# NOTE

- Langchain Agent + Open WebUI
  - https://medium.com/@davit_martirosyan/integrating-langgraph-agents-into-open-webui-3533cc3a47e1
- LiteLLMエージェントにするメリットがあまりない
  - FastAPIでAPIを建てる必要がない分ラク
  - Function, Pipeline側と結合するのは良くない
  - Streaming過程で、ツール完了情報などをメッセージとして送ることで、Function、Pipeline側でそのStreamingを検出して表示をできる
  - Agenticループは非常に単純なのですぐに実装できる
  - ユーザー意図を理解する部分を切り出す必要はあるかもしれない（トリアージエージェント的な発想）
  - qwen3:0.6bはstreamingの場合contentに情報が入っている。gpt-5-nanoはtool_calls[0].functionに情報が入っている
  - litellmのツール対応非対応はこういうところで判定しているのかも

## ストリーミングでのツール呼び出しチェックについて

### 問題点
- `astreaming`メソッドで、初回のツール呼び出しチェックを`stream=True`で実行すると、`function.name`が`None`になる問題が発生
- ストリーミングチャンクから`delta.tool_calls`を収集しても、`function.name`フィールドが適切に取得できない
- `function.arguments`は正しく文字列として取得できるが、関数名が欠落する

### 原因推測
1. LiteLLMのストリーミング処理で、バックエンド（OpenAI APIやOllama）からのレスポンスを変換する際に`name`フィールドが適切に処理されていない可能性
2. OpenAI gpt-5-nanoやOllama qwen3:0.6bがストリーミング時にツール呼び出し情報を異なる形式で返している可能性
3. ストリーミングではツール情報が複数のチャンクに分割されるが、最初のチャンクで`name`が来ることを期待していたが実際には来ていない

### 解決策
- **`use_stream_in_initial_completion = False`を使用（推奨）**
  - 初回のツール呼び出しチェックは非ストリーミング (`stream=False`) で実行
  - ツール実行後の最終レスポンスはストリーミング (`stream=True`) で返す
  - この方法により、安定した動作とストリーミングのUX両方を実現

### 実装詳細（agent.py:220）
```python
use_stream_in_initial_completion = False  # True: stream=True, False: stream=False
```

- `False`: 非ストリーミングでツール呼び出しをチェック（安定、推奨）
- `True`: ストリーミングでツール呼び出しをチェック（`function.name`が`None`になる問題あり）

### 動作確認結果（2025-11-19）
- `False`設定で安定的に動作することを確認
- ツール呼び出しの検出と実行が正常に機能
- 最終レスポンスはストリーミングで返されるためユーザー体験も良好

- ツール呼び出しを指定する際は少し遅くなるのは仕方ないとする。ツール呼び出しの出力自体は全文に比べて短いので問題にならないかも。ツール呼び出しする際は呼び出し確認中、呼び出し完了のサインくらいあればいいかも。
