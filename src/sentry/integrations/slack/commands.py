import logging
from typing import Any, Mapping
from urllib.parse import parse_qs

from django.http import HttpResponse
from rest_framework import status
from rest_framework.request import Request

from sentry.integrations.slack.message_builder.help import build_help_attachment
from sentry.utils import json
from sentry.web.decorators import transaction_start
from sentry.web.frontend.base import BaseView

logger = logging.getLogger("sentry.integrations.slack")


# TODO MARCOS 1
def link():
    # handle already linked
    pass


# TODO MARCOS 2
def unlink():
    pass


def respond(data: Mapping[str, Any]) -> HttpResponse:
    return HttpResponse(
        json.dumps({"blocks": [data]}),
        content_type="application/json",
        status=status.HTTP_200_OK,
    )


def get_command(payload: Mapping[str, str]) -> str:
    text = payload.get("text", [""])[0]
    return text.split(" ")[0].lower()


class SlackCommandsEndpoint(BaseView):
    authentication_classes = ()
    permission_classes = ()
    auth_required = False
    csrf_protect = False

    @transaction_start("SlackCommandsEndpoint")
    def handle(self, request: Request) -> HttpResponse:
        """
        TODO MARCOS DESCRIBE
        Slack commands are all sent to one URL.
        """
        if request.method != "POST":
            return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            payload = parse_qs(request.body.decode("utf-8"), strict_parsing=True)
        except ValueError:
            logger.info("slack.webhook.invalid-payload", extra={"todo": "marcos"})
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        command = get_command(payload)

        if command in ["help", ""]:
            return respond(build_help_attachment())
        elif command == "link":
            link()
            return respond({})
        elif command == "unlink":
            unlink()
            return respond({})

        # If we cannot interpret the command, print help text.
        return respond(build_help_attachment(command))
