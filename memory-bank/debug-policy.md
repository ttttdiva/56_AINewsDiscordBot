# Debug Policy

`/work` 完了後から `/merge` 前までのデバッグ実行方針。

```yaml
mode: off
```

## Modes

- `auto`: 変更範囲とリスクで `/debug` の実行有無を判断する。
- `always`: `/work` のPR作成前、または `/merge` の統合前に `/debug` を実行する。
- `off`: `/debug` は実行しない。通常の既定値。型チェック、テスト、ビルドなどの必須検証は省略しない。

## Auto の判断目安

`auto` では以下に当てはまる場合に `/debug` を実行する。

- UI、画面遷移、フォーム、表示文言、レイアウトを変更した。
- Tauri、Expo、ブラウザ、外部API、ファイルI/Oなど実行環境依存の挙動を変更した。
- ビルド、依存関係、起動手順、CI、配布処理を変更した。
- 既存バグの再現確認が必要。
- ユーザーが明示的にデバッグ確認を求めた。

以下だけなら `/debug` を省略してよい。

- README、memory-bank、docs だけの文書変更。
- コメント、型定義、設定文言など、実行挙動に影響しない軽微な変更。
- 変更範囲に近いテストや静的検証で十分に確認できる小さな修正。

## 記録ルール

`/work` の完了報告とPR本文には以下を必ず残す。

- Debug policy: `auto` / `always` / `off`
- Debug result: `done` / `skipped` / `needed-before-merge`
- Reason: 実行または省略した理由

`/merge` はこの記録を読み、`needed-before-merge` または記録なしでリスクがある場合は、merge前に `/debug` を実行する。
