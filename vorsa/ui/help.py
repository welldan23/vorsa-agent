"""Tampilan teks /bantuan."""

from html import escape

from vorsa.menu import MENU_ITEMS, PANEL_COMMAND


def render_help() -> str:
    lines = ["<b>❓ Bantuan VORSA</b>", "", "Tekan tombol di panel, atau ketik perintah:", ""]
    command, description = PANEL_COMMAND
    lines.append(f"/{command} — {escape(description)}")
    lines += [f"/{item.command} — {escape(item.description)}" for item in MENU_ITEMS]
    return "\n".join(lines)
