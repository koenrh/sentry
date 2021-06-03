from sentry.integrations.slack.message_builder import get_logo_url
from sentry_plugins.slack.plugin import LEVEL_TO_COLOR


def build_link_attachment():
    return {
        "fallback": f"MARCOS",
        "title": "title",
        "title_link": "title_link",
        "text": "text",
        "fields": [],
        "mrkdwn_in": ["text"],
        "footer_icon": get_logo_url(),
        "footer": "footer",
        "color": LEVEL_TO_COLOR["error"],
    }


def build_unlink_attachment():
    return {
        "fallback": f"MARCOS",
        "title": "title",
        "title_link": "title_link",
        "text": "text",
        "fields": [],
        "mrkdwn_in": ["text"],
        "footer_icon": get_logo_url(),
        "footer": "footer",
        "color": LEVEL_TO_COLOR["error"],
    }
