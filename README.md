# 56_AINewsDiscordBot

Discord に毎日 1 回、X 上の AI 関連ニュース要約を投稿する Bot です。Grok API の `x_search` を直接使い、SQLite で重複送信を防ぎます。

## 現在の状態

- `dry-run`: Grok API でニュース収集し、Markdown と生レスポンスを `data/raw/` に保存
- `manual`: Grok API で収集し、Discord の指定チャンネルへ投稿し、SQLite に履歴保存
- `schedule`: JST 指定時刻で日次実行
- 同日の再実行時は、投稿済み digest を再送しない
- 過去 7 日分の投稿済みニュースと Grok で照合し、同一イベントの再掲を除外する

## 主要ファイル

- `src/config/settings.py`: 設定ロード
- `src/clients/grok_client.py`: Grok Responses API 呼び出し
- `src/services/collector.py`: `x_search` 実行と正規化
- `src/services/event_deduper.py`: 過去 7 日とのイベント重複判定
- `src/services/filtering.py`: 重複排除とノイズ除去
- `src/services/summarizer.py`: Discord 用 Markdown 生成
- `src/storage/sqlite_repository.py`: SQLite 永続化
- `src/bot/discord_publisher.py`: Discord 投稿
- `src/scheduler/daily_scheduler.py`: 日次スケジューラ
- `prompts/`: Grok に渡す system/user prompt テンプレート

## セットアップ

1. 依存関係を入れる
   `python -m pip install -e .[dev]`
2. `.env.sample` を必要に応じて更新する
3. このリポジトリ直下の `.env` に `XAI_API_KEY`、`DISCORD_BOT_TOKEN`、`DISCORD_CHANNEL_ID` を設定する

## 実行方法

- 今すぐ本文だけ生成
  `python -m src.main --mode dry-run`
- 今すぐ Discord へ投稿
  `python -m src.main --mode manual`
- 常駐して毎日投稿
  `python -m src.main --mode schedule`
- Windows 用ラッパー
  `run.bat dry-run`
  `run.bat manual`
  `run.bat schedule`
- Unix 系ラッパー
  `./run.sh dry-run`
  `./run.sh manual`
  `./run.sh schedule`

引数を省略した場合、`run.bat` と `run.sh` はどちらも `manual` で起動します。`schedule` は常駐して指定時刻まで待機するモードです。

## 生成物

- 生レスポンス JSON: `data/raw/*-response.json`
- 正規化済み JSON: `data/raw/*-normalized.json`
- Markdown: `data/raw/*-digest.md`
- 重複判定結果: `data/raw/*-dedupe.json`
- SQLite 状態: `data/state.db`

## テスト

`python -m pytest`
