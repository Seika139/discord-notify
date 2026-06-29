"""Tests for discord_notify.webhook — payload construction only, no HTTP calls."""

import logging
from typing import Any

import pytest

from discord_notify import DiscordWebhook, Embed
from discord_notify.webhook import COLOR_ERROR, COLOR_INFO, MAX_EMBEDS_PER_MESSAGE


class TestEmbed:
    def test_empty_embed(self) -> None:
        e = Embed()
        assert e.to_dict() == {}

    def test_full_embed(self) -> None:
        e = Embed(title="T", description="D", color=COLOR_INFO)
        e.add_field("k1", "v1").add_field("k2", "v2", inline=True)
        d = e.to_dict()
        assert d["title"] == "T"
        assert d["description"] == "D"
        assert d["color"] == COLOR_INFO
        assert len(d["fields"]) == 2
        assert d["fields"][1]["inline"] is True

    def test_add_field_returns_self(self) -> None:
        e = Embed()
        result = e.add_field("a", "b")
        assert result is e


class TestDiscordWebhook:
    def test_build_payload_content_only(self) -> None:
        wh = DiscordWebhook("https://example.com/webhook")
        payload = wh.build_payload("hello")
        assert payload == {"content": "hello"}

    def test_build_payload_with_username(self) -> None:
        wh = DiscordWebhook("https://example.com/webhook", username="bot")
        payload = wh.build_payload("msg")
        assert payload["username"] == "bot"

    def test_build_payload_with_embeds(self) -> None:
        wh = DiscordWebhook("https://example.com/webhook")
        embed = Embed(title="Alert", color=COLOR_ERROR)
        payload = wh.build_payload(embeds=[embed])
        assert len(payload["embeds"]) == 1
        assert payload["embeds"][0]["title"] == "Alert"

    def test_build_payload_empty(self) -> None:
        wh = DiscordWebhook("https://example.com/webhook")
        payload = wh.build_payload()
        assert payload == {}


class TestSend:
    """send() の分割送信・dry_run を、HTTP を呼ばずに検証する。"""

    @staticmethod
    def _capture(wh: DiscordWebhook, monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
        """_post を差し替えて POST されるはずの payload を記録する。"""
        posted: list[dict[str, Any]] = []

        def fake_post(payload: dict[str, Any]) -> int:
            posted.append(payload)
            return 204

        monkeypatch.setattr(wh, "_post", fake_post)
        return posted

    def test_send_single_request_for_few_embeds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        wh = DiscordWebhook("https://example.com/webhook")
        posted = self._capture(wh, monkeypatch)
        statuses = wh.send(embeds=[Embed(title=f"e{i}") for i in range(3)])
        assert statuses == [204]
        assert len(posted) == 1
        assert len(posted[0]["embeds"]) == 3

    def test_send_splits_embeds_over_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        wh = DiscordWebhook("https://example.com/webhook")
        posted = self._capture(wh, monkeypatch)
        n = MAX_EMBEDS_PER_MESSAGE * 2 + 3  # 23 → 10 / 10 / 3
        statuses = wh.send(embeds=[Embed(title=f"e{i}") for i in range(n)])
        assert statuses == [204, 204, 204]
        assert [len(p["embeds"]) for p in posted] == [10, 10, 3]

    def test_send_content_only_on_first_chunk(self, monkeypatch: pytest.MonkeyPatch) -> None:
        wh = DiscordWebhook("https://example.com/webhook")
        posted = self._capture(wh, monkeypatch)
        wh.send("hello", embeds=[Embed(title=f"e{i}") for i in range(MAX_EMBEDS_PER_MESSAGE + 1)])
        assert posted[0]["content"] == "hello"
        assert "content" not in posted[1]

    def test_send_dry_run_returns_empty_and_logs(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        wh = DiscordWebhook("https://example.com/webhook")
        posted = self._capture(wh, monkeypatch)
        with caplog.at_level(logging.INFO, logger="discord_notify.webhook"):
            statuses = wh.send(embeds=[Embed(title="t")], dry_run=True)
        assert statuses == []
        assert posted == []  # HTTP は呼ばれない
        assert any("dry_run" in r.message for r in caplog.records)

    def test_send_empty_raises_value_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        wh = DiscordWebhook("https://example.com/webhook")
        posted = self._capture(wh, monkeypatch)
        with pytest.raises(ValueError, match="content または embeds"):
            wh.send()
        assert posted == []  # 送信は試みられない
