# Design Architecture

更新日: 2026-03-11

## 概要

単一プロセスの Python アプリとして構成する。定期実行ジョブが Grok API を呼び、収集結果を整形し、SQLite に保存した上で Discord に投稿する。

## コンポーネント一覧

| コンポーネント | 役割 | 入力 | 出力 |
|---|---|---|---|
| `AppRunner` | 起動とモード切替 | CLI 引数、環境変数 | 実行フロー |
| `Settings` | 設定解決 | `.env`、既定値 | 型付き設定 |
| `GrokClient` | Grok API 呼び出し | 検索 query、prompt | 生レスポンス |
| `NewsCollector` | 検索結果正規化 | API レスポンス | 投稿候補一覧 |
| `NewsFilter` | 重複排除と絞り込み | 投稿候補、既存 state | 採用候補一覧 |
| `DigestBuilder` | Discord 用本文生成 | 採用候補一覧 | Markdown |
| `StateRepository` | SQLite 永続化 | run、post、digest | DB 更新 |
| `DiscordPublisher` | Discord 投稿 | Markdown | message id |
| `DailyScheduler` | 日次実行管理 | 時刻設定 | 定期実行 |

## レイヤー

- Presentation: CLI と Discord 投稿
- Application: collect, filter, summarize, publish のオーケストレーション
- Infrastructure: Grok API, SQLite, Discord API

## 推奨実行モード

- `manual`: 今すぐ 1 回実行
- `schedule`: 常駐して日次実行
- `dry-run`: Discord に送らず本文だけ生成

## 設計ログ

| 日付 | 決定事項 | 理由 | 代替案 |
|---|---|---|---|
| 2026-03-11 | Grok API を直接呼ぶ | MCP を挟む理由が薄い | MCP client + MCP server |
| 2026-03-11 | Python 構成にする | 既存テンプレートと相性が良い | TypeScript |
| 2026-03-11 | 単機能 Bot に絞る | 日次配信を早く安定させたい | 会話型 Bot |
