# NOTE

- Langchain Agent + Open WebUI
  - https://medium.com/@davit_martirosyan/integrating-langgraph-agents-into-open-webui-3533cc3a47e1
- LiteLLMエージェントにするメリットがあまりない
  - FastAPIでAPIを建てる必要がない分ラク
  - Function, Pipeline側と結合するのは良くない
  - Streaming過程で、ツール完了情報などをメッセージとして送ることで、Function、Pipeline側でそのStreamingを検出して表示をできる
  - Agenticループは非常に単純なのですぐに実装できる
  - ユーザー意図を理解する部分を切り出す必要はあるかもしれない（トリアージエージェント的な発想）
