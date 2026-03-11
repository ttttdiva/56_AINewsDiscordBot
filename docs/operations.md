# 運用メモ

## 実行モード

- `dry-run`
  - Discord へは送信しない
  - `data/raw/` にレスポンス、正規化 JSON、Markdown を保存する
- `manual`
  - Grok API で収集し、そのまま Discord へ投稿する
  - 同日の digest が `posted` 状態なら再投稿しない
- `schedule`
  - `BOT_TIMEZONE` と `DAILY_POST_TIME` に従って常駐実行する

## 永続化

- `bot_runs`: 実行履歴
- `source_posts`: 取得済みソース投稿
- `digest_messages`: 日次 digest 本文と送信結果
- `digest_items`: digest とソース投稿の対応

## 再送ポリシー

- 同じ日付の digest が `posted` ならスキップ
- `failed` または未投稿なら再実行時に本文を上書きし直して再送する

## ローカル確認

1. `python -m src.main --mode dry-run`
2. `data/raw/` にファイルが出ることを確認
3. `python -m src.main --mode manual`
4. Discord 投稿後、同じコマンドで再実行しスキップされることを確認
