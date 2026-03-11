# Design Database

更新日: 2026-03-11

## 方針

MVP では SQLite を使う。日次バッチ用途なら十分軽く、重複排除と送信履歴管理に必要な永続化を最小コストで持てるため。

## 実装済みテーブル

### `bot_runs`

1 回の実行単位の履歴。

主なカラム:
- `id`
- `run_type`
- `started_at`
- `finished_at`
- `status`
- `error_message`

### `source_posts`

収集した X 投稿の正規化結果。

主なカラム:
- `id`
- `run_id`
- `post_id`
- `post_url`
- `author_handle`
- `posted_at`
- `title`
- `summary`
- `selection_reason`
- `content_excerpt`
- `collected_at`
- `raw_rank`

制約:
- `post_url` は一意
- `post_id` が取れる場合は `post_id` も一意

### `digest_messages`

日次要約の生成結果と送信結果。

主なカラム:
- `id`
- `digest_date`
- `headline`
- `overview`
- `summary_markdown`
- `discord_channel_id`
- `discord_message_ids`
- `status`
- `created_at`
- `posted_at`
- `failure_reason`

### `digest_items`

どの投稿をその日次要約に採用したかの紐付け。

主なカラム:
- `id`
- `digest_message_id`
- `source_post_id`
- `rank_order`
- `selection_reason`

## MVP で保証していること

- 同じ日付の digest を二重投稿しない
- 投稿済み digest に紐づく source post を再送しない
- 失敗 run の原因を `bot_runs` と `digest_messages` で追跡できる
