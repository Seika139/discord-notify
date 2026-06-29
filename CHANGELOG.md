# Changelog

<!-- markdownlint-disable MD024 -->

このプロジェクトの注目すべき変更はこのファイルで文書化されています。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
このプロジェクトは [セマンティック バージョニング](https://semver.org/lang/ja/spec/v2.0.0.html) を遵守しています。

## Tagged Releases

- [unreleased](https://github.com/Seika139/discord-notify/compare/v0.2.0...HEAD)
- [0.2.0](https://github.com/Seika139/discord-notify/compare/v0.1.5...v0.2.0)
- [0.1.5](https://github.com/Seika139/discord-notify/compare/v0.1.4...v0.1.5)
- [0.1.4](https://github.com/Seika139/discord-notify/compare/v0.1.3...v0.1.4)
- [0.1.3](https://github.com/Seika139/discord-notify/compare/v0.1.2...v0.1.3)
- [0.1.2](https://github.com/Seika139/discord-notify/compare/v0.1.1...v0.1.2)
- [0.1.1](https://github.com/Seika139/discord-notify/compare/v0.1.0...v0.1.1)
- [0.1.0](https://github.com/Seika139/discord-notify/releases/tag/v0.1.0)

## [Unreleased]

### Added

- `Embed` に Discord embed の任意要素を追加する: title リンク (`url`)、`timestamp`、`author` / `footer` / `thumbnail` / `image`
- `Embed.set_author` / `set_footer` / `set_thumbnail` / `set_image` / `set_timestamp` の fluent setter を追加する (`add_field` と同様に `self` を返す)。`set_timestamp` は `datetime` を ISO8601 文字列へ変換し、aware なら元のオフセットを保持、naive なら UTC を補う (Discord が naive を 400 で拒否するため)

新しい任意フィールドは既存の `title` / `description` / `color` / `fields` の後ろに配置し、positional での構築 (`Embed("T", "D", color)`) の後方互換を保つ。

これらはすべて任意で、未設定なら payload に含まれないため既存の利用は影響を受けない。

## [0.2.0] - 2026-06-29

### Added

- `DiscordWebhook.send()` に `dry_run` 引数を追加し、HTTP 送信せず payload を INFO ログに出力できるようにする
- `send()` が embed 10 件超を複数メッセージへ自動分割するようにし、Discord の 1 メッセージ最大 10 embed 制限に対応する
- `send()` で `content` と `embeds` が両方空の場合に `ValueError` を送出し、400 が確定するリクエストを未然に防ぐ

### Changed

- **破壊的変更**: `send()` の戻り値を `int` から `list[int]` に変更する。分割送信した各リクエストの HTTP ステータスコードを送信順に返す (`dry_run` 時は空リスト)

## [0.1.5] - 2026-06-29

### Fixed

- `User-Agent` ヘッダーをパッケージバージョンから動的に生成するよう変更し、リリース版と乖離していた問題を修正
- `pyproject.toml` の `version` が `0.1.3` のまま更新漏れになっていた問題を修正

## [0.1.4] - 2026-06-29

### Added

- webhook URL の渡し方の注意とトラブルシューティングを README に追記し、環境変数の衝突で別チャンネルへ通知される問題や `username` 上書きの挙動を解説する

## [0.1.3] - 2026-04-21

### Fixed

- `User-Agent` ヘッダーを設定し、Discord が urllib デフォルト UA を 403 で拒否する問題を修正

## [0.1.2] - 2026-04-14

### Added

- `CHANGELOG.md` を追加し、Keep a Changelog 形式で変更履歴を管理する
- `update-version` reusable workflow を導入し、バージョン管理を自動化する

## [0.1.1] - 2026-04-14

### Added

- PEP 561 準拠の `py.typed` マーカーを追加し、型情報を配布可能にする
- `mise.toml` を追加し、`uv` と `python` のバージョンを固定する
- mypy strict と `ty` による型チェックを導入する

### Changed

- `dict` を `dict[str, Any]` に変更して strict モードの型チェックを通過させる
- `urllib.request.urlopen(...).status` を `int` でキャストして戻り値型を明示する
- テスト関数に戻り値アノテーション `-> None` を追加する

## [0.1.0] - 2026-04-14

### Added

- `DiscordWebhook` クラスを実装し、Python 標準ライブラリのみで
  Discord Webhook にメッセージを送信可能にする
- `Embed` dataclass を提供し、フィールド付きの Embed メッセージを構築可能にする
- `COLOR_SUCCESS` / `COLOR_WARNING` / `COLOR_ERROR` / `COLOR_INFO`
  のカラー定数を提供する
- `build_payload` メソッドを提供し、HTTP 送信せずにペイロードを構築可能にする
