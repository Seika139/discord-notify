"""Minimal Discord webhook client using only the standard library."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

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
    """

    title: str = ""
    description: str = ""
    color: int | None = None
    fields: list[dict[str, str | bool]] = field(default_factory=list)

    def add_field(self, name: str, value: str, *, inline: bool = False) -> Embed:
        self.fields.append({"name": name, "value": value, "inline": inline})
        return self

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.title:
            d["title"] = self.title
        if self.description:
            d["description"] = self.description
        if self.color is not None:
            d["color"] = self.color
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

    def __init__(
        self, url: str, *, username: str | None = None, timeout: int = 10
    ) -> None:
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
    ) -> int:
        """Send a message to Discord. Returns the HTTP status code."""
        payload = self.build_payload(content, embeds)
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            self.url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "discord-notify/0.1.3",
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
