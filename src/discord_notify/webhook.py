"""Minimal Discord webhook client using only the standard library."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from typing import Any

logger = logging.getLogger(__name__)

try:
    __version__ = version("discord-notify")
except PackageNotFoundError:  # ソース直実行などで未インストールの場合
    __version__ = "0.0.0+unknown"

USER_AGENT = f"discord-notify/{__version__}"

# Discord は 1 メッセージあたり最大 10 embed まで受け付ける。
MAX_EMBEDS_PER_MESSAGE = 10

# Discord embed color presets
COLOR_SUCCESS = 0x2ECC71  # green
COLOR_WARNING = 0xF1C40F  # yellow
COLOR_ERROR = 0xE74C3C  # red
COLOR_INFO = 0x3498DB  # blue


@dataclass
class Embed:
    """A Discord embed object.

    >>> e = Embed(title="Test", color=COLOR_INFO)
    >>> e.add_field("key", "value")
    Embed(title='Test', ...)

    title / description / color / fields に加え、Discord embed の任意要素として
    title リンク (``url``)、``timestamp``、``author`` / ``footer`` / ``thumbnail`` /
    ``image`` をサポートする。これらは値があるときだけ payload に含まれる。
    author / footer は複数のサブ項目を持つため、``set_author`` / ``set_footer`` の
    fluent setter で組み立てる。
    """

    # 既存の公開フィールド順 (title, description, color, fields) は positional 構築の
    # 後方互換のため維持する。新しい任意フィールドは必ずこの後ろに足す。
    title: str = ""
    description: str = ""
    color: int | None = None
    fields: list[dict[str, str | bool]] = field(default_factory=list)
    url: str = ""
    timestamp: str | None = None
    author: dict[str, str] | None = None
    footer: dict[str, str] | None = None
    thumbnail: dict[str, str] | None = None
    image: dict[str, str] | None = None

    def add_field(self, name: str, value: str, *, inline: bool = False) -> Embed:
        self.fields.append({"name": name, "value": value, "inline": inline})
        return self

    def set_author(self, name: str, *, url: str = "", icon_url: str = "") -> Embed:
        """author (アイコン+名前の小見出し行) を設定する。空のサブ項目は省く。"""
        author: dict[str, str] = {"name": name}
        if url:
            author["url"] = url
        if icon_url:
            author["icon_url"] = icon_url
        self.author = author
        return self

    def set_footer(self, text: str, *, icon_url: str = "") -> Embed:
        """footer (最下部の小さなテキスト) を設定する。"""
        footer: dict[str, str] = {"text": text}
        if icon_url:
            footer["icon_url"] = icon_url
        self.footer = footer
        return self

    def set_thumbnail(self, url: str) -> Embed:
        """thumbnail (右上の小さな画像) を設定する。"""
        self.thumbnail = {"url": url}
        return self

    def set_image(self, url: str) -> Embed:
        """image (下部の大きな画像) を設定する。"""
        self.image = {"url": url}
        return self

    def set_timestamp(self, value: str | datetime) -> Embed:
        """timestamp を設定する。datetime を渡すと ISO8601 文字列に変換する。

        aware な datetime は元のタイムゾーン (オフセット) を保持する。naive な
        datetime はオフセットが付かず Discord が 400 を返すため、UTC を補ってから
        変換する。文字列はそのまま設定する。
        """
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            self.timestamp = value.isoformat()
        else:
            self.timestamp = value
        return self

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.title:
            d["title"] = self.title
        if self.description:
            d["description"] = self.description
        if self.url:
            d["url"] = self.url
        if self.color is not None:
            d["color"] = self.color
        if self.timestamp:
            d["timestamp"] = self.timestamp
        if self.author:
            d["author"] = self.author
        if self.thumbnail:
            d["thumbnail"] = self.thumbnail
        if self.image:
            d["image"] = self.image
        if self.footer:
            d["footer"] = self.footer
        if self.fields:
            d["fields"] = self.fields
        return d


class DiscordWebhook:
    """Send messages to a Discord channel via webhook URL.

    Usage::

        webhook = DiscordWebhook("https://discord.com/api/webhooks/xxx/yyy")
        webhook.send("Hello!")
        webhook.send(embeds=[Embed(title="Alert", color=COLOR_ERROR)])
    """

    def __init__(self, url: str, *, username: str | None = None, timeout: int = 10) -> None:
        self.url = url
        self.username = username
        self.timeout = timeout

    def build_payload(
        self,
        content: str = "",
        embeds: list[Embed] | None = None,
    ) -> dict[str, Any]:
        """Build the JSON payload without sending it. Useful for testing."""
        payload: dict[str, Any] = {}
        if content:
            payload["content"] = content
        if self.username:
            payload["username"] = self.username
        if embeds:
            payload["embeds"] = [e.to_dict() for e in embeds]
        return payload

    def send(
        self,
        content: str = "",
        embeds: list[Embed] | None = None,
        *,
        dry_run: bool = False,
    ) -> list[int]:
        """Send a message to Discord, returning the HTTP status code of each request.

        Discord は 1 メッセージ最大 10 embed のため、embed が 10 件を超える場合は
        複数のメッセージに分割して送る (``content`` は最初のメッセージにのみ付く)。
        戻り値は送信順の HTTP ステータスコードのリスト。

        ``dry_run=True`` のときは HTTP 送信せず、各メッセージの payload を INFO ログに
        出力して空リストを返す。

        ``content`` と ``embeds`` が両方とも空の場合は、Discord が空ペイロードを 400 で
        拒否するため、リクエストを送らず ``ValueError`` を送出する。
        """
        if not content and not embeds:
            raise ValueError("content または embeds のいずれかを指定してください")
        statuses: list[int] = []
        for payload in self._build_payloads(content, embeds):
            if dry_run:
                logger.info("[dry_run] would POST: %s", json.dumps(payload, ensure_ascii=False))
                continue
            statuses.append(self._post(payload))
        return statuses

    def _build_payloads(
        self,
        content: str,
        embeds: list[Embed] | None,
    ) -> list[dict[str, Any]]:
        """送信用 payload を組み立てる。embed が 10 件を超える場合は複数に分割する。"""
        if not embeds:
            return [self.build_payload(content)]
        payloads: list[dict[str, Any]] = []
        for i in range(0, len(embeds), MAX_EMBEDS_PER_MESSAGE):
            chunk = embeds[i : i + MAX_EMBEDS_PER_MESSAGE]
            # content は最初のメッセージにのみ付け、分割時の重複を避ける。
            chunk_content = content if i == 0 else ""
            payloads.append(self.build_payload(chunk_content, chunk))
        return payloads

    def _post(self, payload: dict[str, Any]) -> int:
        """POST a single prebuilt payload to the webhook URL. Returns the HTTP status code."""
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            self.url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return int(resp.status)
        except urllib.error.HTTPError as e:
            logger.error("Discord webhook failed: %s %s", e.code, e.reason)
            raise
        except urllib.error.URLError as e:
            logger.error("Discord webhook connection error: %s", e.reason)
            raise
