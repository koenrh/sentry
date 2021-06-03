from typing import Mapping
from urllib.parse import urlencode

from django.urls import reverse
from requests import Response

from sentry.testutils import APITestCase
from sentry.utils import json


def assert_is_help_text(response: Response) -> None:
    data = json.loads(response.content)
    assert "Available Commands" in data["blocks"][0]["text"]["text"]


def create_payload():
    return {
        "token": "uxymmuEYs5R7bqOgQAAt9UFf",
        "team_id": "T01DJ56Q7V0",
        "team_domain": "testingslack-les2311",
        "channel_id": "D01E80KD1GQ",
        "channel_name": "directmessage",
        "user_id": "U01DBD3V04W",
        "user_name": "mgaeta89",
        "command": "%2Fsentry",
        "text": "",
        "api_app_id": "A01DQAESPQU",
        "is_enterprise_install": "false",
        "response_url": "https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT01DJ56Q7V0%2F2135265155843%2FRYf7IUCsBp9Nl5jNRy1YdoER",
        "trigger_id": "2135049807058.1460176823986.f205ea2fc5530c46ee4d1cac187aa64c",
    }


class SlackCommandsTest(APITestCase):
    endpoint = "sentry-integration-slack-commands"

    def get_slack_response(self, payload: Mapping[str, str]) -> Response:
        """ Shadow get_success_response but with a non-JSON payload. """
        response = self.client.post(
            reverse(self.endpoint),
            content_type="application/x-www-form-urlencoded",
            data=urlencode(payload).encode("utf-8"),
        )
        assert response.status_code == 200
        return response

    def setUp(self):
        pass


class SlackCommandsGetTest(SlackCommandsTest):
    def test_method_not_allowed(self):
        self.get_error_response(status_code=405)


class SlackCommandsPostTest(SlackCommandsTest):
    method = "post"

    def test_missing_command(self):
        response = self.get_slack_response({"text": ""})
        assert_is_help_text(response)

    def test_invalid_command(self):
        response = self.get_slack_response({"text": "invalid command"})
        assert_is_help_text(response)

    def test_help_command(self):
        response = self.get_slack_response({"text": "help"})
        assert_is_help_text(response)

    def test_link_command(self):
        self.get_slack_response({"text": "link"})

    def test_unlink_command(self):
        self.get_slack_response({"text": "unlink"})

    def test_link_command_already_linked(self):
        self.get_slack_response({"text": "link"})

    def test_unlink_command_already_unlinked(self):
        self.get_slack_response({"text": "unlink"})
