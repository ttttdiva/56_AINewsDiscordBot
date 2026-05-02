---
name: merge
description: 実装済み変更をレビュー・検証し、ベースブランチへ統合する。
---

# merge

統合モード。実装済みのブランチや PR を確認し、検証して merge する。

## ルール

- 無関係な機能追加をしない。
- 検証に失敗した変更を無理に merge しない。
- 既存のユーザー変更を捨てない。
- merge 戦略が不明な場合はリポジトリ標準に従う。
- Skill、`CLAUDE.md`、`memory-bank/` は UTF-8 として読む。文字化けする場合は読み直し、読めないまま作業を続けない。
- `/merge` の実行指示は、統合に必要な検証・ビルド・リリース方針確認まで含む。
- release / upload / deploy は、ユーザーが明示した場合、または `memory-bank/` / `docs/` / 既存スクリプトで merge 時リリースが標準化されている場合に行う。
- リリース対象プロジェクトで `/merge` を指示された場合、「release を明示されていない」としてビルドや GitHub Release を省略しない。
- GitHub Release へアップロードする場合は、開発リポジトリとは別の公開用 Public リポジトリを使う。
- 公開用リポジトリ（`owner/repo`）がユーザー指示・設定・環境変数のいずれにも無い場合は、アップロードを止めてユーザーに要求する。
- 現在いるブランチを信用せず、target branch / PR と base branch を最初に確定する。
- merge 成功後は、target branch が base/default/protected/release 系ではなく、ユーザーが保持を明示していない限り、ローカルと remote の古い target branch を削除する。
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
10. リリース対象か判定する。
   - `docs/mobile-auto-update-standard.md` が存在し、対象変更が Mobile 公開に関わる場合。
   - `memory-bank/techContext.md` に公開用 Public リポジトリ、GitHub Release、`latest.json`、asset名が記録されている場合。
   - `scripts/build_apk.*`、release workflow、updater metadata など、既存の公開手順がある場合。
11. リリース対象の場合は、必要なビルド成果物を作成し、APK/desktop asset と `latest.json` の整合性を検証する。
12. release / upload / deploy を行う場合は、公開用 Public リポジトリを確認する。未指定ならここで止め、ユーザーに `owner/repo` を要求する。
13. merge する。
14. 必要に応じて base branch を push する。
15. リリース対象の場合は、公開用 Public リポジトリへ GitHub Release アップロードを行い、必要なら `latest.json` を更新する。
16. merge、base branch push、必要な release / upload が成功したら、target branch の削除可否を判定する。
   - 削除する: target branch が base branch ではなく、default branch でもなく、保護ブランチや `release/*` / `hotfix/*` などの保持対象でもなく、ユーザーが保持を明示していない場合。
   - 削除しない: 上記の保持条件に当てはまる場合、または merge / push / release が未完了の場合。
17. 削除対象なら、remote branch を削除し、ローカル branch も存在すれば削除する。PR 経由で GitHub CLI を使う場合は `gh pr merge --delete-branch` を優先してよい。
   - remote: `git push origin --delete <target-branch>`
   - local: `git branch -d <target-branch>`
18. 結果を `memory-bank/` に反映する。

## リリースゲート

リリース対象と判定した場合は、merge 前にリリース前提を満たす。

- version / versionCode / tag / asset名 / `latest.json` / 公開用リポジトリ / ビルドスクリプトなど、現在有効なリリース方針に必要な値を確認する。
- 同じ version・tag・asset が既に公開済みの場合、ユーザーが同一 version 上書きを明示していない限り、target branch 上で version bump など必要最小限の修正を行い、検証して push してから merge する。
- リリース前提を満たせず、merge 後に release / upload できない可能性がある場合は、merge だけ先に進めない。理由と必要な修正を示して止める。
- 「既存 version のためアップロードしない」「設定不足のため release を省略する」という判断を、merge 後に初めて出してはいけない。

## ブランチ整理

merge、base branch push、必要な release / upload が成功したら、古い target branch を整理する。

- 削除する: target branch が base/default/protected branch ではなく、`release/*` / `hotfix/*` などの保持対象でもなく、ユーザーが保持を明示していない場合。
- 削除しない: merge / push / 必要な release が未完了の場合、または保持対象の branch の場合。
- PR 経由では `gh pr merge --delete-branch` を優先してよい。削除後は remote-tracking branch も `git fetch --prune` などで消えたことを確認する。
- CLI で整理する場合は `git push origin --delete <target-branch>` と `git branch -d <target-branch>` を使う。

## GitHub Release
公開用リポジトリは `owner/repo` 形式で確認する。

確認順:

1. ユーザーの明示指示
2. プロジェクト設定や `memory-bank/` に記録された公開用リポジトリ
3. `RELEASE_REPO` 環境変数

どれにも無い場合は、ビルドだけで止めるのではなく、アップロード前に必ずユーザーへ公開用 Public リポジトリを要求する。

`/merge` がリリース対象プロジェクトで実行された場合、GitHub Release アップロードは標準手順に含まれる。ユーザーが「mergeのみ」「releaseなし」と明示した場合だけ省略する。

## 完了報告

必ず以下を含める:

- Base branch
- Target branch または PR URL
- Merge commit または merge結果
- Push 済みかどうか
- 古い target branch の削除結果
- Debug policy / Debug result / Reason
- Release / upload の有無
