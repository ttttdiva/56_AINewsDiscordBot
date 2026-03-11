# 運用メモ

## 実行モード

- `dry-run`
  - Discord へは送信しない
  - `--date` 未指定時は前日分の digest を生成する
  - `data/raw/` にレスポンス、正規化 JSON、Markdown を保存する
- `manual`
  - 既定では前日分を Grok API で収集し、そのまま Discord へ投稿する
  - 同日の digest が `posted` 状態なら再投稿しない
- `schedule`
  - `BOT_TIMEZONE` と `DAILY_POST_TIME` に従って常駐実行する
  - 指定時刻になったら前日分の digest を投稿する

## 永続化

- `bot_runs`: 実行履歴
- `source_posts`: 取得済みソース投稿
- `digest_messages`: 日次 digest 本文と送信結果
- `digest_items`: digest とソース投稿の対応
- `event_dedupe_results`: その日の候補に対する `new_event` / `duplicate_event` / `event_update` 判定

## 再送ポリシー

- 同じ日付の digest が `posted` ならスキップ
- `failed` または未投稿なら再実行時に本文を上書きし直して再送する
- さらに、過去 7 日分の投稿済みニュースを Grok に渡し、同一イベントの再掲は `duplicate_event` として除外する
- 同一イベントでも新事実がある場合は `event_update` として採用する

## ローカル確認

1. `python -m src.main --mode dry-run`
2. `data/raw/` にファイルが出ることを確認
3. `*-dedupe.json` に重複判定結果が保存されることを確認
3. `python -m src.main --mode manual`
4. Discord 投稿後、同じコマンドで再実行しスキップされることを確認
5. 必要なら `--date YYYY-MM-DD` を付けて過去日付の digest を再生成する

## 定期実行

- Windows タスク スケジューラから `run.bat` を呼ぶ
- Linux/macOS の cron や systemd timer から `run.sh` を呼ぶ
- 引数を省略すると `manual` モードで起動する
- `schedule` は常駐プロセス向けで、起動後は指定時刻まで待機し続ける
