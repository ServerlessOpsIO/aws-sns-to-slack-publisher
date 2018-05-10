'''Publish message from SNS to Slack'''

import json
import logging
import os
import sys

import boto3
from botocore.exceptions import ClientError
from slackclient import SlackClient

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))  # type: ignore
_logger = logging.getLogger(__name__)

SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
SLACK_DEFAULT_CHANNEL = os.environ.get('SLACK_DEFAULT_CHANNEL')
SLACK = SlackClient(SLACK_API_TOKEN)

RESPONSE_SNS_TOPIC_ARN = os.environ.get('RESPONSE_SNS_TOPIC_ARN')
SNS = boto3.client('sns')


class HandlerBaseError(Exception):
    '''Base error class'''


class SlackPublishError(HandlerBaseError):
    '''Slack publish error'''
    def __init__(self, response):
        self.msg = 'Slack API Error - {}'.format(response.get('error'))
        super(HandlerBaseError, self).__init__(self.msg)


class SnsPublishError(HandlerBaseError):
    '''SNS publish error'''


def _get_message_from_event(event: dict) -> dict:
    '''Get the message from the event'''
    return json.loads(event.get('Records')[0].get('Sns').get('Message'))


def _publish_slack_message(token: str, channel: str, message: dict) -> dict:
    '''Publish message to Slack'''
    message['channel'] = channel
    _logger.debug('Slack message: {}'.format(json.dumps(message)))
    # XXX: Don't log the token in the debug call.
    message['token'] = token

    r = SLACK.api_call(
        "chat.postMessage",
        **message
    )
    _logger.debug('Slack response: {}'.format(json.dumps(r)))

    if r.get('ok') is not True:
        raise SlackPublishError(r)
    else:
        return r


def _publish_sns_message(sns_topic_arn: str, message: str) -> dict:
    '''Publish message to SNS topic'''
    try:
        r = SNS.publish(
            TopicArn=sns_topic_arn,
            Message=message
        )
    except ClientError as e:
        exc_info = sys.exc_info()
        raise SnsPublishError(e).with_traceback(exc_info[2])

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

