# Progress

更新日: 2026-03-11

## Done

- `pyproject.toml`、`.gitignore`、`.env.sample`、`.env` を整備
- `pydantic-settings` ベースの設定ロードを実装
- 実行時設定がこのリポジトリの `.env` とプロセス環境変数だけで完結するよう修正
- Grok Responses API + `x_search` のクライアントを実装
- strict JSON でのニュース収集、正規化、重複排除、Markdown 生成を実装
- 過去 7 日分とのイベント単位重複判定を Grok 1 回で行う dedupe フローを実装
- SQLite に run、source post、digest、digest item を保存するよう実装
- `event_dedupe_results` テーブルを追加し、判定結果を保存するよう実装
- Discord 投稿と 2000 文字分割送信を実装
- APScheduler ベースの日次スケジューラを実装
- `dry-run` を実 API で確認
- `manual` を実 Discord 投稿まで確認
- 同日再実行時の重複投稿スキップを確認
- テスト 7 件を追加し、`python -m pytest` で全件通過
- `README.md` と `docs/operations.md` を実装内容に更新
- `run.bat` / `run.sh` の既定モードを `manual` に変更し、定期実行で待機し続けないよう修正
- `DISCORD_CHANNEL_ID` のハードコード既定値を削除し、public 公開向けに tracked files のローカル依存記述を整理
- 日次 digest の Markdown フォーマットを簡素化し、固定見出しと本文直行の形に修正
- `SEARCH_LOOKBACK_DAYS=1` の検索窓を「当日だけ」に修正し、前日ニュースが混ざる挙動を解消
- `manual` / `dry-run` 用に `--date YYYY-MM-DD` の対象日付指定を追加
- date 未指定時は前日分の digest を作るよう既定動作を変更
- Agent Guide / Skills 導入: `.agents/skills/`、`.claude/skills/`、`CLAUDE.md`、`GEMINI.md`、`memory-bank/debug-policy.md` を追加し、`AGENTS.md` を `CLAUDE.md` 参照に統一（2026-04-25）

## In Progress

- 実運用での検索品質調整
- public 公開前の最終整理

## Todo

- 必要なら検索クエリのチューニング
- 必要なら dedupe プロンプトのチューニング
- 必要ならノイズ除去ルールの強化
- 必要なら投稿フォーマット改善

## Known Risks

- `x_search` の返却品質は日ごとに揺れる
- Grok の strict JSON 出力がたまに不完全になる可能性がある
- 外部 API 応答時間が長く、実行が 1 分超になることがある
- イベント重複判定の精度はプロンプトと過去 7 日の候補品質に依存する

## Next Milestone

- 数日運用して、投稿品質とノイズ率を見ながらクエリとフィルタを詰める
