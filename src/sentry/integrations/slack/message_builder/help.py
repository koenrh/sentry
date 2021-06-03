from typing import Any, Mapping, Optional

AVAILABLE_COMMANDS = {
    "help": "displays the available commands",
    "link": "kicks of linking Slack and Sentry",
    "unlink": "unlinks your identity",
}


def build_help_attachment(command: Optional[str] = None) -> Mapping[str, Any]:
    unknown_command = f"Unknown command: `{command}`\n" if command else ""
    commands_list = "\n".join(
        f"• *{command}* - {description}" for command, description in AVAILABLE_COMMANDS.items()
    )
    message = f"{unknown_command}Available Commands:\n{commands_list}"

    return {"type": "section", "text": {"type": "mrkdwn", "text": message}}
