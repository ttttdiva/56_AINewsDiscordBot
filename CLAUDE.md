# Agent Guide


<!-- agent-absolute-gates:v1 -->
## 絶対ゲート

- 長い本文より先にこのゲートを適用する。迷ったら本文解釈で省略せず、このゲートに従う。
- 作業開始時と完了前に `git status --short --branch` と対象差分を確認し、ユーザー変更を巻き込まない。
- `mobile/` 配下に差分がある merge/release では、ユーザーが明示的に `releaseなし` / `APK不要` / `upload不要` と言わない限り、APK build、GitHub Release upload、`latest.json` 更新まで必須。
- `debugなし` は実機・エミュレーター等の手動デバッグだけを省略する指定。typecheck、build、release、upload、metadata更新は省略しない。
- `docs/` や scripts に公開・ビルド手順がある場合は必ず従う。docs を理由に手順を省略しない。
- 完了報告には mobile changed / release required / build / upload / metadata / debug の結果を明記する。

## Codex運用の強制ルール

- Skill、`CLAUDE.md`、`memory-bank/` は UTF-8 として読む。PowerShell で文字化けする場合は `Get-Content -Encoding UTF8` を使う。読めない指示を推測で無視して作業を続けない。
- `/work` では、原則として作業前に base branch から作業ブランチを作る。`main` / `master` / base branch に直接 commit / push しない。ただし、ユーザーが今回の依頼で「mainブランチでそのままやっていい」などを明示した場合は、base branch 上での編集・commit・push を許可する。
- 「push」は通常は作業ブランチの push を意味し、ユーザーが base branch への直接 push を明示した場合だけ base branch への push として扱う。
- `CLAUDE.md` の一般的な push 指示より、`.agents/skills/work/SKILL.md` のブランチルールを優先する。
- `/merge` では、対象ブランチ/PRと base branch を確定し、必須検証と必要なビルドを実行してから統合する。
- リリース対象プロジェクトの `/merge` では、`memory-bank/` と `docs/` のリリース方針に従い、GitHub Release / `latest.json` 更新まで扱う。ユーザーが「releaseなし」と明示した場合だけ省略する。
必要なルールは長くても削らない。返答・ログ・コミットメッセージは必ず日本語で書く。

## 最初に読む順序

1. `memory-bank/projectbrief.md`
2. `memory-bank/productContext.md`
3. `memory-bank/systemPatterns.md`
4. `memory-bank/techContext.md`
5. `memory-bank/activeContext.md`
6. `memory-bank/progress.md`
7. `docs/implementation-plan.md`
8. 必要に応じて `memory-bank/design-*.md`

## 即時チェックリスト

- 既存差分は勝手に戻さない。破壊的操作は事前承認を得る。
- 文字化けと断定せず、必要なら `Get-Content -Encoding utf8` やバイト列で確認する。
- `.env`、APIキー、Discord token、SQLite状態、`data/raw/` の生成物を不用意にコミットしない。
- MCP 化はしない。X 検索は Grok API の `x_search` を直接使う前提を守る。
- `docs/` はユーザー向けドキュメント、設計情報は `memory-bank/design-*.md` に置く。

## 作業分類

- 質問・調査・レビューは `/ask`。
- ファイル変更を伴う作業は `/work`。
- 実装・修正後の動作確認は `/debug`。
- 統合は `/merge`。

スキルは `.agents/skills/` と `.claude/skills/` に同じ内容で配置している。変更する場合は両方を同期する。

## Memory Bank

Memory Bank は引き継ぎノート。作業開始時は必ず上記6ファイルを読む。作業終了時は必ず `memory-bank/activeContext.md` と `memory-bank/progress.md` を更新する。

仕様・前提・方針が変わった場合は、active/progress だけで済ませず、該当する恒久ファイルや `design-*.md` も更新する。`update memory bank` 指示時は全ファイルを再確認して差分を反映する。

### 書き方の原則

- 「現状 / 次のステップ / 判断・前提」を分ける。
- 未来の自分が迷わず再開できる粒度で具体化する。
- 事実と推測を分ける。推測は根拠を書く。

### ファイルの役割

- `projectbrief.md`: 目的、成功条件、非ゴール、スコープ、制約。
- `productContext.md`: 想定ユーザー、主要ユースケース、UX要件、既存の痛み、受け入れ条件。
- `systemPatterns.md`: 全体構成、主要フロー、データモデル、設計判断、運用パターン。
- `techContext.md`: 技術スタック、実行方法、依存、制約、テスト/ビルド/デプロイ。
- `activeContext.md`: 直近の作業、判断、次にやること、ブロッカー。
- `progress.md`: 完了事項、進行中、未着手、課題/リスク、次のマイルストーン。
- `design-*.md`: アーキテクチャ、DB、API、画面構成などの構造化設計書。

## プロジェクト前提

- Discord に毎日1回、X上のAI関連ニュース要約を投稿する Python Bot。
- Grok API の `x_search` で収集し、SQLite で重複送信を防ぐ。
- MVP は1サーバー1チャンネル想定。会話型Bot、音声入出力、Web UI、複数ワークスペース対応はスコープ外。
- 実装時の優先順位は、設定ロード、Grok APIクライアント、収集と重複排除、要約生成、Discord投稿、スケジューラ、テストと運用手順。
- 必要なら既存の Python ツール構成や `discord.py` の一般的な実装パターンを参考にしてよいが、実行時依存はこのリポジトリ内に閉じる。
- 外部リポジトリの設定ファイルや secrets に依存しない。

## 開発環境

- Python は仮想環境を使い、依存は `pyproject.toml` を基準にする。
- セットアップは `python -m pip install -e .[dev]`。
- 基本実行は `python -m src.main --mode dry-run`、投稿は `python -m src.main --mode manual`、常駐は `python -m src.main --mode schedule`。
- Windows ラッパーは `run.bat dry-run`、`run.bat manual`、`run.bat schedule`。
- テストは `python -m pytest`。

## Debug Policy

`memory-bank/debug-policy.md` を参照する。外部API、Discord投稿、スケジューラ、SQLite重複判定、日付処理に関わる変更は `/debug` の要否を明示する。

## Git

- コミット前に `git status` を確認する。
- コミットメッセージは日本語で簡潔に書く。
- 「pushしろ」と言われた場合、未コミットの変更があれば、base branch ではないことを確認してから `add`、`commit`、`push` を実行する。
- バイナリファイルを不用意にコミットしない。
