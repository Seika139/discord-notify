# Changelog

<!-- markdownlint-disable MD024 -->

このプロジェクトの注目すべき変更はこのファイルで文書化されています。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
このプロジェクトは [セマンティック バージョニング](https://semver.org/lang/ja/spec/v2.0.0.html) を遵守しています。

## Tagged Releases

- [unreleased](https://github.com/Seika139/discord-notify/compare/v0.1.1...HEAD)
- [0.1.1](https://github.com/Seika139/discord-notify/compare/v0.1.0...v0.1.1)
- [0.1.0](https://github.com/Seika139/discord-notify/releases/tag/v0.1.0)

## [Unreleased]

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
