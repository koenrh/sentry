from sentry.utils.assets import get_asset_url
from sentry.utils.http import absolute_uri


def get_logo_url() -> str:
    return absolute_uri(get_asset_url("sentry", "images/sentry-email-avatar.png"))
