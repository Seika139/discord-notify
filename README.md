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

## webhook URL の渡し方の注意

このライブラリは環境変数を読まず、渡された URL に送るだけ (URL の取得は利用側の責務)。URL を環境変数や .env 経由で渡す場合は次の罠に注意する。

- **マシン共通の export と衝突させない**。シェルプロファイル等でマシン全体に `DISCORD_WEBHOOK_URL` のような汎用名を export していると、利用側の dotenv 読み込みが setdefault 型 (既存環境変数を優先) の場合にプロジェクトの `.env` が無視され、**別チャンネルへ静かに通知され続ける**。対策は 2 つ: (1) マシン共通の export には用途を含む固有名 (例: `AGENT_NOTIFY_DISCORD_WEBHOOK_URL`) を使う、(2) 利用側はプロジェクトの `.env` に明記したキーを環境変数より優先して読み込む。
- **systemd と手動実行で挙動が変わりうる**。systemd service はシェルプロファイルを読まないため、「定期実行は正しいチャンネルに届くのに手動実行だけ違う (またはその逆)」という症状はこの環境変数の継承差を疑う。

## トラブルシューティング

### 通知が想定と違うチャンネルに届く

実効値を確認する: 利用側コードで URL を組み立てた直後に末尾数文字をログに出すか、`echo ${DISCORD_WEBHOOK_URL: -8}` をシェルと .env とで比較する。上記「webhook URL の渡し方の注意」の衝突パターンであることが多い。

### Discord 側で設定した webhook の名前・アイコンが反映されない

`DiscordWebhook(url, username=...)` で `username` を渡すと、Discord の webhook 設定の名前を**メッセージ単位で上書き**する。webhook 設定の名前・アイコンを使いたい場合は `username` を渡さない (None にする)。なおアイコンの上書き (`avatar_url`) は本ライブラリでは未対応で、常に webhook 設定のアイコンが使われる。

## テスト

```bash
uv run pytest -v
```

## Lint

```bash
uv run ruff check .
uv run ruff format --check .
```
