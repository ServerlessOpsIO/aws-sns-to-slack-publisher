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

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:000000000000:test-topic'
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
def sns_topic_arn(topic_arn=SNS_TOPIC_ARN):
    '''SNS Topic ARN'''
    return topic_arn


def test__get_message_from_event(event):
    '''Test fetching message from test event.'''
    r = h._get_message_from_event(event)

    assert False


def test__publish_slack_message(slack_channel, slack_message):
    '''Test publish a test slack message.'''
    assert False


@mock_sts
@mock_sns
def test__publish_sns_message(sns_topic_arn, sns_message):
    '''Test publish an SNS message.'''
    assert False
