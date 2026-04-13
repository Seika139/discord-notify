"""Tests for discord_notify.webhook — payload construction only, no HTTP calls."""

from discord_notify import DiscordWebhook, Embed
from discord_notify.webhook import COLOR_ERROR, COLOR_INFO


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
