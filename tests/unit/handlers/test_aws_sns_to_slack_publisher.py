'''Test health_event_publisher'''
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name
import json
import os

import boto3
from moto import mock_sns, mock_sts
import pytest

import handlers.aws_sns_to_slack_publisher as h

EVENT_FILE = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'events',
    'aws_sns_to_slack_publisher.json'
)

SNS_TOPIC_NAME = "mock-aws-sns-to-slack-publisher-responses"
SLACK_CHANNEL = "#testing"
SLACK_SCHEMA_FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    '../../../slack-message-schema.json'
)


@pytest.fixture()
def event(event_file=EVENT_FILE):
    '''Trigger event'''
    with open(event_file) as f:
        return json.load(f)


@pytest.fixture()
def slack_message(event):
    '''Slack message'''
    return h._get_message_from_event(event)


@pytest.fixture()
def slack_channel(channel=SLACK_CHANNEL):
    '''Slack channel'''
    return channel

@pytest.fixture()
def slack_message_schema():
    '''Slack message schema'''
    with open(SLACK_SCHEMA_FILE_PATH) as f:
        return json.load(f)


@pytest.fixture()
def slack_response():
    '''Slack response'''
    return {}


@pytest.fixture()
def sns_message(slack_response):
    '''SNS message'''
    return slack_response


@pytest.fixture()
def sns_client():
    '''SNS client'''
    return boto3.client('sns')


@pytest.mark.skip(reason="Not sure how to mock this yet.")
def test__check_slack_channel_exists():
    '''Test slack channel exists'''
    assert False


def test__get_message_from_event(event):
    '''Test fetching message from test event.'''
    r = h._get_message_from_event(event)

    assert isinstance(r, dict)
    assert 'text' in r.keys()


@pytest.mark.skip(reason="Not sure how to mock this yet.")
def test__publish_slack_message(slack_channel, slack_message):
    '''Test publish a test slack message.'''
    assert False


@mock_sts
@mock_sns
def test__publish_sns_message(sns_client, sns_message, sns_topic_name=SNS_TOPIC_NAME):
    '''Test publish an SNS message.'''

    sns_create_topic_resp = sns_client.create_topic(Name=SNS_TOPIC_NAME)
    sns_publish_resp = h._publish_sns_message(
        sns_create_topic_resp.get('TopicArn'),
        json.dumps(sns_message)
    )

    assert sns_publish_resp.get('ResponseMetadata').get('HTTPStatusCode') == 200


def test__sanitize_slack_channel_name_clean():
    '''Test sanitizing a clean channel name'''
    channel = 'clean'
    new_channel = h._sanitize_slack_channel_name(channel)
    assert channel == new_channel


def test__sanitize_slack_channel_name_dirty():
    '''Test sanitizing a dirty channel name'''
    channel = '#dirty'
    new_channel = h._sanitize_slack_channel_name(channel)
    assert new_channel[0] != '#'


def test__validate_slack_message_schema(slack_message, slack_message_schema):
    '''Validate a Slack message.'''
    # Throws an exception on bad in put.
    h._validate_slack_message_schema(slack_message, slack_message_schema)


def test__validate_slack_message_schema_has_attachment(slack_message, slack_message_schema):
    '''Validate message with attachment is fine'''
    slack_message['attachment'] = [{'text': 'attachment text'}]
    h._validate_slack_message_schema(slack_message, slack_message_schema)


def test__validate_slack_message_schema_has_attachment_bad_type(slack_message, slack_message_schema):
    '''Validate message with attachment is fine'''
    slack_message['attachments'] = {'text': 'attachment text'}

    error = None
    try:
        h._validate_slack_message_schema(slack_message, slack_message_schema)
    except h.SlackMessageValidationError as e:
        error = e

    assert isinstance(error, h.SlackMessageValidationError)


def test__validate_slack_message_schema_has_attachment_missing_text_property(slack_message, slack_message_schema):
    '''Validate message with attachment is fine'''
    slack_message['attachments'] = [{'missing_text': 'field text'}]

    error = None
    try:
        h._validate_slack_message_schema(slack_message, slack_message_schema)
    except h.SlackMessageValidationError as e:
        error = e

    assert isinstance(error, h.SlackMessageValidationError)


def test__validate_slack_message_schema_has_attachment_has_fields(slack_message, slack_message_schema):
    '''Validate message with attachment is fine'''
    slack_message['attachments'] = [
        {
            'text': 'attachment text',
            'fields': [
                {
                    'title': 'title',
                    'value': 'value',
                }
            ]
        }
    ]

    h._validate_slack_message_schema(slack_message, slack_message_schema)

def test__validate_slack_message_schema_has_attachment_has_fields_missing_property(slack_message, slack_message_schema):
    '''Validate message with attachment is fine'''
    slack_message['attachments'] = [
        {
            'text': 'attachment text',
            'fields': [
                {
                    'title': 'title',
                }
            ]
        }
    ]

    error = None
    try:
        h._validate_slack_message_schema(slack_message, slack_message_schema)
    except h.SlackMessageValidationError as e:
        error = e

    assert isinstance(error, h.SlackMessageValidationError)

