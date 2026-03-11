# 56_AINewsDiscordBot

Discord に毎日 1 回、X 上の AI 関連ニュース要約を投稿する Bot です。Grok API の `x_search` を直接使い、SQLite で重複送信を防ぎます。

## 現在の状態

- `dry-run`: Grok API でニュース収集し、Markdown と生レスポンスを `data/raw/` に保存
- `manual`: Grok API で収集し、Discord の指定チャンネルへ投稿し、SQLite に履歴保存
- `schedule`: JST 指定時刻で日次実行
- 同日の再実行時は、投稿済み digest を再送しない

## 主要ファイル

- `src/config/settings.py`: 設定ロード
- `src/clients/grok_client.py`: Grok Responses API 呼び出し
- `src/services/collector.py`: `x_search` 実行と正規化
- `src/services/filtering.py`: 重複排除とノイズ除去
- `src/services/summarizer.py`: Discord 用 Markdown 生成
- `src/storage/sqlite_repository.py`: SQLite 永続化
- `src/bot/discord_publisher.py`: Discord 投稿
- `src/scheduler/daily_scheduler.py`: 日次スケジューラ

## セットアップ

1. 依存関係を入れる
   `python -m pip install -e .[dev]`
2. `.env.sample` を必要に応じて更新する
3. このリポジトリ直下の `.env` に `XAI_API_KEY` と `DISCORD_BOT_TOKEN` を設定する

`DISCORD_CHANNEL_ID` は `1481265352032915506` を既定で使います。

## 実行方法

- 今すぐ本文だけ生成
  `python -m src.main --mode dry-run`
- 今すぐ Discord へ投稿
  `python -m src.main --mode manual`
- 常駐して毎日投稿
  `python -m src.main --mode schedule`

## 生成物

- 生レスポンス JSON: `data/raw/*-response.json`
- 正規化済み JSON: `data/raw/*-normalized.json`
- Markdown: `data/raw/*-digest.md`
- SQLite 状態: `data/state.db`

## テスト

`python -m pytest`
