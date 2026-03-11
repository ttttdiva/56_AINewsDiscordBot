# Design Sitemap

更新日: 2026-03-11

## オペレーターが触る入口

- `README.md`
- `docs/implementation-plan.md`
- `.env`
- `python -m src.main --mode manual`
- `python -m src.main --mode schedule`

## 想定ディレクトリマップ

- `docs/`: セットアップ手順、運用手順
- `memory-bank/`: 設計判断と進捗
- `src/`: 実装本体
- `tests/`: テスト
- `config/`: 固定クエリやテンプレート
- `data/`: SQLite や一時成果物

## MVP 実装後に追加したい文書

- `docs/setup.md`
- `docs/discord-setup.md`
- `docs/operations.md`
- `docs/query-tuning.md`
