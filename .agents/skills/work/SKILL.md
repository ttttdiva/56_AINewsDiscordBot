---
name: work
description: 初期化・実装・整理・設定変更・ドキュメント更新など、リポジトリを変更する作業を行う。merge はしない。
---

<!-- agent-absolute-gates:v1 -->
## 絶対ゲート

- merge/release では、存在する場合は必ず `scripts/check_mobile_release_gate.ps1` を先に実行し、`RELEASE_REQUIRED=True` なら APK build / GitHub Release upload / `latest.json` 更新を完了条件に含める。

- 長い本文より先にこのゲートを適用する。迷ったら本文解釈で省略せず、このゲートに従う。
- 作業開始時と完了前に `git status --short --branch` と対象差分を確認し、ユーザー変更を巻き込まない。
- `mobile/` 配下に差分がある merge/release では、ユーザーが明示的に `releaseなし` / `APK不要` / `upload不要` と言わない限り、APK build、GitHub Release upload、`latest.json` 更新まで必須。
- `debugなし` は実機・エミュレーター等の手動デバッグだけを省略する指定。typecheck、build、release、upload、metadata更新は省略しない。
- `docs/` や scripts に公開・ビルド手順がある場合は必ず従う。docs を理由に手順を省略しない。
- 完了報告には mobile changed / release required / build / upload / metadata / debug の結果を明記する。


# work

変更作業モード。タスク専用 worktree と作業ブランチを作成し、初期化、実装、修正、整理、設定変更、ドキュメント更新、PR作成を扱う。

## ルール

- merge しない。
- 原則として、現在の checkout では変更作業を行わず、タスク専用 worktree を作成してそこで編集・commit・push する。
- 原則として `main` / `master` / base branch に直接 commit / push しない。
- 例外として、ユーザーが今回の依頼で「mainブランチでそのままやっていい」「base branchに直接commit/pushしてよい」「worktreeを使わないでよい」などを明示した場合は、base branch 上または現在 checkout 上での編集・commit・push を許可する。
- ファイル編集前に必ずタスク専用 worktree と作業ブランチを作成または確認する。ただし、上記の直接作業許可または worktree 不使用許可がある場合はこの限りではない。
- 「push」は通常は作業ブランチの push を意味する。ユーザーが base branch への直接 push を明示した場合だけ、base branch への push として扱う。
- `CLAUDE.md` に push と書かれていても、このSkillのブランチルールを優先する。
- Skill、`CLAUDE.md`、`memory-bank/` は UTF-8 として読む。文字化けする場合は読み直し、読めないまま作業を続けない。
- 明示されていない release / upload / deploy はしない。
- GitHub Release へのアップロードはしない。
- 無関係なリファクタをしない。
- 既存のユーザー変更を捨てない。
- 破壊的操作が必要な場合は事前承認を得る。
- 作業ブランチ名、base branch、worktree path、PR URLを必ず記録する。
- `memory-bank/debug-policy.md` が存在する場合は、デバッグ実行方針として必ず読む。
- ユーザーが今回の依頼で「デバッグする」「デバッグなし」などを明示した場合は、`debug-policy.md` より優先する。

## 作業開始Git/Worktreeゲート

ファイル編集前に必ず実行する。ユーザーの明示的な直接作業許可または worktree 不使用許可がない限り、現在 checkout では編集・commit・push を始めない。

```bash
git status --short --branch
git branch --show-current
git remote -v
git worktree list
```

必須動作:

- base branch を確定し、現在 checkout の既存差分を今回作業に巻き込まない。
- 新規タスクでは、base branch からタスク専用 worktree と作業ブランチを作成してから編集する。
- 既存 worktree / 既存作業ブランチで続行してよいのは、ユーザーが同一タスクの続きだと明示し、かつその worktree の差分範囲が今回作業と一致すると確認できる場合だけ。
- 現在ブランチが `main` / `master` / base branch の場合は、ユーザーの明示的な直接作業許可がなければ、編集前にタスク専用 worktree と作業ブランチを作成する。
- ユーザーの明示的な直接作業許可がある場合は、base branch 上で続行してよい。その場合は開始時・commit前・push前・完了報告に「直接作業許可あり」と記録する。
- 既存差分がある場合も、ユーザーの明示的な直接作業許可がなければ base branch 上で作業を続けない。差分を巻き込まない方法を選び、必要なら退避してから作業ブランチを作る。
- タスク専用 worktree または作業ブランチを作成できない場合は、ファイルを編集せずに中断する。

```bash
git fetch origin
git worktree add -b <work-branch> <worktree-path> origin/<base-branch>
```

worktree path は原則としてリポジトリ外の sibling directory に置く。例: `../_worktrees/<repo-name>/<work-branch>`。既存パスがある場合は上書きせず、別名を選ぶ。

## Git安全ゲート

commit / push / 完了報告の直前にも、作業中の worktree で必ず実行する。どれか1つでも条件を満たさない場合は中断し、修正またはユーザー確認を行う。ただし、ユーザーの明示的な直接作業許可がある場合は、base branch 上の commit / push を許可する。

```bash
git status --short --branch
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
git worktree list
```

必須条件:

- 現在ブランチが `main` / `master` / base branch ではない。または、ユーザーの明示的な直接作業許可がある。
- upstream がある場合、upstream は現在ブランチ名と同じ remote branch を指している。upstream 未設定で `git rev-parse` が失敗した場合は、push 時に `-u` で作業ブランチの upstream を設定する。
- `git push` を使う場合は裸の `git push` を使わず、通常は必ず `git push -u origin HEAD:<current-branch>` を使う。直接作業許可がある場合だけ `git push origin <base-branch>` を使ってよい。
- `current-branch` は `git branch --show-current` の出力をそのまま使う。
- `git status --short --branch` の出力を見て、`## main`、`## master`、または base branch 上なら、直接作業許可がない限り commit / push しない。
- worktree path が今回タスク専用の場所であることを確認する。

禁止コマンド:

```bash
git push
git push origin main
git push origin master
git push origin <base-branch>
git commit  # Git安全ゲート未実行のまま実行すること
```

上記の base branch push は、ユーザーの明示的な直接作業許可がある場合だけ禁止から除外する。`git commit` は、直前の Git安全ゲートで現在ブランチが安全、または直接作業許可ありと確認できた場合だけ実行してよい。`git push` は必ず push 前の Git安全ゲート後に実行する。

## 手順

1. `memory-bank/` を読む。
2. `memory-bank/template-initialization.md` が存在する場合は、テンプレート初期化前として扱い、その指示を最優先で確認する。
3. 現在地を確認する:
   - `git status --short --branch`
   - `git branch --show-current`
   - `git remote -v`
   - `git worktree list`
4. base branch を確定する。通常は `main`。
5. ユーザーの明示的な直接作業許可または worktree 不使用許可があるか確認する。許可がある場合は理由を記録し、以降の worktree 必須条件を緩和してよい。
6. 新規タスクでは、現在 checkout に差分があっても巻き込まず、base branch からタスク専用 worktree と作業ブランチを作成する。
7. 既存 worktree / 既存作業ブランチを続行する場合は、ユーザーが同一タスクの続きだと明示していること、差分範囲が今回作業と一致することを確認する。不一致なら編集せず中断する。
8. worktree を作成したら、その worktree に移動して以降の読取・編集・検証・commit・push を行う。
9. 詳細仕様が必要な場合だけ `docs/` を参照する。
   - Mobile 自動更新に関わる作業では、存在するなら `docs/mobile-auto-update-standard.md` を必ず参照する。
10. 最小の安全な差分で編集する。
11. 変更範囲に合う検証を実行する。
12. 必要ならローカルビルドを実行する。npm/APK/desktop成果物の公開アップロードはしない。
13. `/debug` を実行するか判断する。
   - `debug-policy.md` の `mode: always`、またはユーザーがデバッグ実行を明示した場合は `/debug` を実行する。
   - `mode: off`、またはユーザーがデバッグなしを明示した場合は `/debug` を実行しない。ただし通常の型チェック、テスト、ビルドなどの必須検証は省略しない。
   - `mode: auto` の場合は、UI、画面遷移、外部連携、ファイルI/O、起動手順、ビルド、依存関係、CI、配布処理、既存バグ再現に関わる変更なら `/debug` を実行する。文書だけ、または静的検証で十分な軽微変更なら省略してよい。
14. PR本文と完了報告に Debug policy / Debug result / Reason を記録する。merge前にデバッグすべきなら `Debug result: needed-before-merge` とする。
15. 状態・判断・次ステップが変わったら `memory-bank/` を更新する。
16. commit 前に Git安全ゲートを実行し、現在ブランチが base branch ではないこと、または直接作業許可があることを確認する。
17. commit する。
18. push 前に Git安全ゲートを再実行し、通常は `git push -u origin HEAD:<current-branch>` で作業ブランチだけを push する。直接作業許可があり、ユーザーが push も求めている場合だけ base branch へ push する。
19. PR を作成する。または環境上 PR 作成できない場合は PR タイトル・本文・差分要約を用意する。
20. 完了報告前に Git安全ゲートを再実行し、base branch へ直接 push していないこと、または直接作業許可に基づく push であることを確認する。
21. 作業が commit / push 済みで worktree に未コミット差分がなく、ユーザーが保持を明示していない場合は、worktree 削除可否を判断する。削除する場合は対象 path が今回作成した worktree であることを確認してから `git worktree remove <worktree-path>` を使う。
22. 変更内容、検証結果、デバッグ判断、ブランチ情報、worktree情報、PR情報を報告する。

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
- Worktree path
- Worktree cleanup result
- PR URL または PR 未作成の理由
- push 済みかどうか
- push 先 remote branch
- base branch 直接作業許可の有無
- Debug policy / Debug result / Reason
