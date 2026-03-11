# Agent Guide

このリポジトリは実装前の計画用スキャフォールドです。次回の Codex 実行では、まず既存計画を読み、MVP を崩さずに実装へ進めてください。

## 最初に読む順序

1. `memory-bank/projectbrief.md`
2. `memory-bank/activeContext.md`
3. `memory-bank/progress.md`
4. `docs/implementation-plan.md`
5. 必要に応じて `memory-bank/design-*.md`

## このリポジトリの前提

- Python ベースで作る
- Bot の役割は「毎日 1 回、AI 関連ニュースの要約を Discord に投稿すること」
- X 検索は Grok API の `x_search` を直接使う
- MCP 化はしない
- MVP は 1 サーバー 1 チャンネル想定でよい
- まずは slash command よりも定期実行と安定運用を優先する

## 参考実装の扱い

- 必要なら既存の Python ツール構成や `discord.py` の一般的な実装パターンを参考にしてよい
- ただし、このリポジトリの実行時依存はこのリポジトリ内に閉じる
- 外部リポジトリの設定ファイルや secrets に依存しない

## 実装時の優先順位

1. 設定ロード
2. Grok API クライアント
3. 収集と重複排除
4. 要約生成
5. Discord 投稿
6. スケジューラ
7. テストと運用手順

## スコープ外

- 会話型 Discord Bot
- 音声入出力
- Web UI
- 複数ワークスペース対応
- 複雑な承認フロー

## 更新ルール

- 実装が進んだら `memory-bank/activeContext.md` と `memory-bank/progress.md` を更新する
- 設計判断を変えたら対応する `design-*.md` を更新する
