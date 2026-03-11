# Design API

更新日: 2026-03-11

## 外部 API

### Grok Responses API

- エンドポイント: `/responses`
- 認証: Bearer token
- ツール: `x_search`
- 実装:
  - strict JSON で digest 候補を返させる
  - `from_date` / `to_date` をツール指定する
  - `allowed_x_handles` / `excluded_x_handles` を必要に応じて使う

### Discord API

- ライブラリ: `discord.py`
- 実装:
  - ワンショット接続して投稿
  - 2000 文字超過時は分割送信

## 内部インターフェース

### `GrokClient.search_ai_news(...)`

入力:
- `system_prompt`
- `user_prompt`
- `from_date`
- `to_date`

出力:
- 生レスポンス JSON
- 抽出済みテキスト

### `NewsCollector.collect(...)`

入力:
- digest date

出力:
- `CollectionResult`

### `DigestBuilder.build(...)`

入力:
- digest date
- headline
- overview
- `list[NewsPost]`

出力:
- `DigestDraft`

### `DiscordPublisher.publish(...)`

入力:
- channel_id
- markdown

出力:
- `list[int]` message ids

## CLI

- `python -m src.main --mode dry-run`
- `python -m src.main --mode manual`
- `python -m src.main --mode schedule`
