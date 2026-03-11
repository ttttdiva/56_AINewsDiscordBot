# System Patterns

更新日: 2026-03-11

## 全体構成

Bot は次の責務に分ける。

- `config`: 環境変数、検索条件、投稿先、実行時刻の管理
- `clients.grok`: Grok API の `responses` 呼び出し
- `services.collector`: X 検索実行とレスポンス正規化
- `services.filtering`: ノイズ低減、重複排除、ランキング
- `services.summarizer`: Discord 投稿用 Markdown の生成
- `storage.sqlite`: 実行履歴、送信済み投稿、送信済みメッセージの保存
- `bot.discord`: Discord への投稿
- `scheduler`: 日次ジョブ登録と手動実行

## 重要な設計方針

- API クライアントと Bot ロジックを分離する
- Discord 投稿前に必ずローカル保存する
- 検索と要約は再実行可能にする
- 送信済み判定はメモリではなく永続化データで行う

## 失敗時の扱い

- API 失敗は run 履歴に残す
- Discord 投稿失敗時は投稿本文を保存して再送可能にする
- 同時実行はロックで防ぐ

## 今回採らない設計

- MCP サーバーを 1 段挟む構成
- 会話イベント駆動の Discord Bot
- 複数プロバイダ抽象化の早期導入
