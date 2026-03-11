# Tech Context

更新日: 2026-03-11

## 採用技術

- Python 3.10+
- `discord.py`
- `httpx`
- `pydantic` / `pydantic-settings`
- `sqlite3`
- `APScheduler`
- `pytest`

## 外部依存

- xAI Grok Responses API
- Discord Bot Token

## 実装済み環境変数

- `APP_MODE`
- `XAI_API_KEY`
- `XAI_API_BASE`
- `XAI_GROK_MODEL`
- `GROK_TIMEOUT_SECONDS`
- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID`
- `BOT_TIMEZONE`
- `DAILY_POST_TIME`
- `AI_NEWS_QUERY`
- `ALLOWED_X_HANDLES`
- `EXCLUDED_X_HANDLES`
- `X_SEARCH_MAX_RESULTS`
- `X_SEARCH_LANGUAGE`
- `SEARCH_LOOKBACK_DAYS`
- `DIGEST_MAX_ITEMS`
- `STATE_DB_PATH`
- `RAW_OUTPUT_DIR`
- `LOG_LEVEL`

## 実装メモ

- 実行時設定はこのリポジトリ直下の `.env` とプロセス環境変数だけを読む
- 実行 artifact は `data/raw/` に保存する
- SQLite は `data/state.db` を使う
- 2026-03-11 時点で Python 3.10.11 環境で動作確認した
