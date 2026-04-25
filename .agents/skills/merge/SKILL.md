---
name: merge
description: 実装済み変更をレビュー・検証し、ベースブランチへ統合する。
user_invocable: true
trigger: /merge
argument-hint: [branch-or-pr]
---

# merge

統合モード。実装済みのブランチや PR を確認し、検証して merge する。

## ルール

- 無関係な機能追加をしない。
- 検証に失敗した変更を無理に merge しない。
- 既存のユーザー変更を捨てない。
- merge 戦略が不明な場合はリポジトリ標準に従う。
- release / upload / deploy は明示指示がある場合だけ行う。
- GitHub Release へアップロードする場合は、開発リポジトリとは別の公開用 Public リポジトリを使う。
- 公開用リポジトリ（`owner/repo`）がユーザー指示・設定・環境変数のいずれにも無い場合は、アップロードを止めてユーザーに要求する。
- 現在いるブランチを信用せず、target branch / PR と base branch を最初に確定する。
- `memory-bank/debug-policy.md` が存在する場合は、merge前のデバッグ実行方針として必ず読む。
- ユーザーが今回の依頼で「デバッグする」「デバッグなし」などを明示した場合は、`debug-policy.md` とPR本文の記録より優先する。

## 手順

1. `memory-bank/` を読む。
2. 現在地を確認する:
   - `git status --short --branch`
   - `git branch --show-current`
   - `git remote -v`
3. 対象 PR または target branch を特定する。
4. base branch を確定する。通常は `main`。
5. target と base の差分を確認する。
6. 正しさ、回帰リスク、リポジトリ規約との整合性をレビューする。
7. 必要なら競合や drift を解消する。
8. 必須の検証を実行する。
9. PR本文や `/work` 完了報告の Debug policy / Debug result / Reason を確認し、merge前に `/debug` を実行するか判断する。
   - `mode: always`、`Debug result: needed-before-merge`、またはユーザーがデバッグ実行を明示した場合は `/debug` を実行する。
   - `mode: off`、またはユーザーがデバッグなしを明示した場合は `/debug` を実行しない。ただし必須検証は省略しない。
   - `mode: auto` で記録がない、またはUI、画面遷移、外部連携、ファイルI/O、起動手順、ビルド、依存関係、CI、配布処理、既存バグ再現に関わる差分がある場合は `/debug` を実行する。
   - `Debug result: done` で、target がその後変わっておらず、追加リスクがない場合は再実行しなくてよい。
10. Mobile 自動更新に関わる release の場合は、存在するなら `docs/mobile-auto-update-standard.md` を確認し、APK asset と `latest.json` の整合性を検証する。
11. release / upload / deploy が明示されている場合は、公開用 Public リポジトリを確認する。
12. merge する。
13. 必要に応じて push する。
14. 明示された場合だけ、公開用 Public リポジトリへ GitHub Release アップロードを行う。
15. 結果を `memory-bank/` に反映する。

## GitHub Release

公開用リポジトリは `owner/repo` 形式で確認する。

確認順:

1. ユーザーの明示指示
2. プロジェクト設定や `memory-bank/` に記録された公開用リポジトリ
3. `RELEASE_REPO` 環境変数

どれにも無い場合は、ビルドだけで止めるのではなく、アップロード前に必ずユーザーへ公開用 Public リポジトリを要求する。

## 完了報告

必ず以下を含める:

- Base branch
- Target branch または PR URL
- Merge commit または merge結果
- Push 済みかどうか
- Debug policy / Debug result / Reason
- Release / upload の有無
