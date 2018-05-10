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


@pytest.fixture()
def event(event_file=EVENT_FILE):
    '''Trigger event'''
    with open(event_file) as f:
        return json.load(f)


@pytest.fixture()
def slack_message(event):
    '''Slack message'''
    return json.dumps(h._get_message_from_event(event))


@pytest.fixture()
def slack_channel(channel=SLACK_CHANNEL):
    '''Slack channel'''
    return channel


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
