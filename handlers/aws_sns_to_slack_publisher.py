'''Publish message from SNS to Slack'''

import json
import logging
import os

import boto3
from slackclient import SlackClient

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))  # type: ignore
_logger = logging.getLogger(__name__)

SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
SLACK_DEFAULT_CHANNEL = os.environ.get('SLACK_DEFAULT_CHANNEL')
SLACK = SlackClient(SLACK_API_TOKEN)

RESPONSE_SNS_TOPIC_ARN = os.environ.get('RESPONSE_SNS_TOPIC_ARN')
SNS = boto3.client('sns')


def _get_message_from_event(event: dict) -> dict:
    '''Get the message from the event'''
    return json.loads(event.get('Records')[0].get('Sns').get('Message'))


def _publish_slack_message(token: str, channel: str, message: dict) -> dict:
    '''Publish message to Slack'''
    r = SLACK.api_call(
        "chat.postMessage",
        token=token,
        channel=channel,
        **message
    )
    _logger.debug('Slack response: {}'.format(json.dumps(r)))
    return r


def _publish_sns_message(sns_topic_arn: str, message: str) -> dict:
    '''Publish message to SNS topic'''
    r = SNS.publish(
        TopicArn=sns_topic_arn,
        Message=message
    )
    _logger.debug('SNS response: {}'.format(json.dumps(r)))

    return r


def handler(event, context):
    '''Function entry'''
    _logger.debug('Event received: {}'.format(json.dumps(event)))
    slack_message = _get_message_from_event(event)
    slack_response = _publish_slack_message(SLACK_API_TOKEN,
                                            SLACK_DEFAULT_CHANNEL,
                                            slack_message)
    sns_response = _publish_sns_message(RESPONSE_SNS_TOPIC_ARN,
                                        json.dumps(slack_response))

    resp = {
        'slack_response': slack_response,
        'sns_response': sns_response,
        'status': 'OK'
    }

    _logger.debug('Response: {}'.format(json.dumps(resp)))
    return resp

