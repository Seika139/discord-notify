# discord-notify

外部依存ゼロの Discord Webhook クライアント。Python 標準ライブラリ（`urllib.request`）のみで動作する。

## インストール

```bash
uv sync
```

他のプロジェクトから依存として使う場合は `pyproject.toml` に以下を追加する。

```toml
[project]
dependencies = ["discord-notify"]

[tool.uv.sources]
discord-notify = { path = "../discord-notify", editable = true }
```

## 使い方

### テキストメッセージを送る

```python
from discord_notify import DiscordWebhook

webhook = DiscordWebhook("https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN")
webhook.send("Hello from discord-notify!")
```

### Embed 付きメッセージを送る

```python
from discord_notify import DiscordWebhook, Embed
from discord_notify.webhook import COLOR_ERROR, COLOR_INFO, COLOR_SUCCESS, COLOR_WARNING

webhook = DiscordWebhook(
    "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN",
    username="my-bot",  # Discord に表示される Bot 名（省略可）
)

embed = Embed(
    title="デプロイ完了",
    description="本番環境へのデプロイが正常に完了しました。",
    color=COLOR_SUCCESS,
)
embed.add_field("環境", "production", inline=True)
embed.add_field("バージョン", "v1.2.3", inline=True)
embed.add_field("デプロイ者", "CI/CD")

webhook.send(embeds=[embed])
```

### カラー定数

| 定数 | 色 | 用途 |
|------|------|------|
| `COLOR_SUCCESS` | 緑 (`#2ECC71`) | 成功通知 |
| `COLOR_WARNING` | 黄 (`#F1C40F`) | 警告 |
| `COLOR_ERROR` | 赤 (`#E74C3C`) | エラー・障害 |
| `COLOR_INFO` | 青 (`#3498DB`) | 情報 |

### テスト用にペイロードだけ確認する

```python
webhook = DiscordWebhook("https://example.com/webhook")
embed = Embed(title="Test")
payload = webhook.build_payload("hello", embeds=[embed])
print(payload)
# {'content': 'hello', 'embeds': [{'title': 'Test'}]}
```

## テスト

```bash
uv run pytest -v
```

## Lint

```bash
uv run ruff check .
uv run ruff format --check .
```
