---
name: work
description: 初期化・実装・整理・設定変更・ドキュメント更新など、リポジトリを変更する作業を行う。merge はしない。
user_invocable: true
trigger: /work
argument-hint: [request]
---

# work

変更作業モード。ブランチ作成、初期化、実装、修正、整理、設定変更、ドキュメント更新、PR作成を扱う。

## ルール

- merge しない。
- 明示されていない release / upload / deploy はしない。
- GitHub Release へのアップロードはしない。
- 無関係なリファクタをしない。
- 既存のユーザー変更を捨てない。
- 破壊的操作が必要な場合は事前承認を得る。
- 作業ブランチ名、base branch、PR URLを必ず記録する。
- `memory-bank/debug-policy.md` が存在する場合は、デバッグ実行方針として必ず読む。
- ユーザーが今回の依頼で「デバッグする」「デバッグなし」などを明示した場合は、`debug-policy.md` より優先する。

## 手順

1. `memory-bank/` を読む。
2. `memory-bank/template-initialization.md` が存在する場合は、テンプレート初期化前として扱い、その指示を最優先で確認する。
3. 現在地を確認する:
   - `git status --short --branch`
   - `git branch --show-current`
   - `git remote -v`
4. base branch を確定する。通常は `main`。
5. 既存差分がなければ、base branch から作業ブランチを作成する。
6. 既存差分がある場合は、巻き込まない方法を選び、必要なら作業前に状況を報告する。
7. 詳細仕様が必要な場合だけ `docs/` を参照する。
   - Mobile 自動更新に関わる作業では、存在するなら `docs/mobile-auto-update-standard.md` を必ず参照する。
8. 最小の安全な差分で編集する。
9. 変更範囲に合う検証を実行する。
10. 必要ならローカルビルドを実行する。npm/APK/desktop成果物の公開アップロードはしない。
11. `/debug` を実行するか判断する。
   - `debug-policy.md` の `mode: always`、またはユーザーがデバッグ実行を明示した場合は `/debug` を実行する。
   - `mode: off`、またはユーザーがデバッグなしを明示した場合は `/debug` を実行しない。ただし通常の型チェック、テスト、ビルドなどの必須検証は省略しない。
   - `mode: auto` の場合は、UI、画面遷移、外部連携、ファイルI/O、起動手順、ビルド、依存関係、CI、配布処理、既存バグ再現に関わる変更なら `/debug` を実行する。文書だけ、または静的検証で十分な軽微変更なら省略してよい。
12. PR本文と完了報告に Debug policy / Debug result / Reason を記録する。merge前にデバッグすべきなら `Debug result: needed-before-merge` とする。
13. 状態・判断・次ステップが変わったら `memory-bank/` を更新する。
14. commit し、作業ブランチを push する。
15. PR を作成する。または環境上 PR 作成できない場合は PR タイトル・本文・差分要約を用意する。
16. 変更内容、検証結果、デバッグ判断、ブランチ情報、PR情報を報告する。

## PR

`/work` の完了形は、merge 可能な PR または PR 相当の説明を残すこと。

PRには以下を含める:

- 目的
- 変更内容
- 検証結果
- デバッグ判断（Debug policy / Debug result / Reason）
- 影響範囲
- 未確認事項

完了報告には必ず以下を含める:

- Base branch
- Work branch
- PR URL または PR 未作成の理由
- push 済みかどうか
- Debug policy / Debug result / Reason
