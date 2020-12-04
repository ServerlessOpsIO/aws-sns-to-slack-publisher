'''Publish message from SNS to Slack'''

import json
import logging
import os
import sys

from boolean import boolean
import boto3
from botocore.exceptions import ClientError
import jsonschema
from slackclient import SlackClient
from tenacity import retry, retry_if_exception_type, stop_after_delay, wait_exponential

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))  # type: ignore
_logger = logging.getLogger(__name__)

SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
SLACK_DEFAULT_CHANNEL = os.environ.get('SLACK_DEFAULT_CHANNEL')
SLACK = SlackClient(SLACK_API_TOKEN)
SLACK_SCHEMA_FILE_PATH = os.path.join(os.path.dirname(__file__), '../slack-message-schema.json')
with open(SLACK_SCHEMA_FILE_PATH) as f:
    SLACK_MESSAGE_SCHEMA = json.load(f)

SNS_PUBLISH_RESPONSE = boolean(os.environ.get('SNS_PUBLISH_RESPONSE', 'false'))
RESPONSE_SNS_TOPIC_ARN = os.environ.get('RESPONSE_SNS_TOPIC_ARN')
SNS = boto3.client('sns')


class HandlerBaseError(Exception):
    '''Base error class'''


class SlackBaseError(HandlerBaseError):
    '''Base Slack Error'''

class SlackApiError(SlackBaseError):
    '''Slack API error class'''
    def __init__(self, response: dict):
        self.msg = 'Slack error - {}'.format(response.get('error'))
        super(HandlerBaseError, self).__init__(self.msg)


class SlackChannelListError(SlackApiError):
    '''Slack publish error'''


class SlackMessageValidationError(SlackBaseError):
    '''Slack message format error'''


class SlackPublishError(SlackApiError):
    '''Slack publish error'''


class SlackInvalidChannelNameError(SlackBaseError):
    '''Slack invalid channel name'''
    def __init__(self, channel: str):
        self.msg = 'invalid channel name - {}'.format(channel)
        super(HandlerBaseError, self).__init__(self.msg)


class SnsPublishError(HandlerBaseError):
    '''SNS publish error'''


@retry(wait=wait_exponential(), stop=stop_after_delay(15), retry=retry_if_exception_type(SlackChannelListError))
def _check_slack_channel_exists(token: str, channel: str) -> None:
    '''Check given Slack channel exists'''
    r = SLACK.api_call(
        "conversations.list",
        token=token,
    )
    _logger.debug('Slack response: {}'.format(json.dumps(r)))

    if r.get('ok') is not True:
        raise SlackChannelListError(r)

    channel_found = False
    for c in r.get('channels'):
        this_channel = c.get('name')
        if channel == this_channel:
            channel_found = True
            break

    if channel_found is False:
        raise SlackInvalidChannelNameError(channel)
    else:
        return r


def _get_message_from_event(event: dict) -> dict:
    '''Get the message from the event'''
    return json.loads(event.get('Records')[0].get('Sns').get('Message'))


@retry(wait=wait_exponential(), stop=stop_after_delay(15))
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


@retry(wait=wait_exponential(), stop=stop_after_delay(15))
def _publish_sns_message(sns_topic_arn: str, message: dict) -> dict:
    '''Publish message to SNS topic'''
    _logger.debug('SNS message: {}'.format(json.dumps(message)))
    try:
        r = SNS.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps(message)
        )
    except ClientError as e:
        exc_info = sys.exc_info()
        raise SnsPublishError(e).with_traceback(exc_info[2])

    _logger.debug('SNS response: {}'.format(json.dumps(r)))
    return r


def _sanitize_slack_channel_name(channel_name: str) -> str:
    '''Cleanup channel name'''
    # channel names are inconsistently used in the API so we make it so here.
    if channel_name[0] == '#':
        fixed_name = channel_name[1:]
    else:
        fixed_name = channel_name
    return fixed_name


def _validate_slack_message_schema(message: dict, schema: dict) -> None:
    '''Validate the incoming slack message format'''
    try:
        jsonschema.validate(message, schema)
    except jsonschema.ValidationError as e:
        exc_info = sys.exc_info()
        raise SlackMessageValidationError(e).with_traceback(exc_info[2])

    return


def handler(event, context):
    '''Function entry'''
    _logger.debug('Event received: {}'.format(json.dumps(event)))
    slack_message = _get_message_from_event(event)
    _validate_slack_message_schema(slack_message, SLACK_MESSAGE_SCHEMA)
    slack_channel = _sanitize_slack_channel_name(SLACK_DEFAULT_CHANNEL)
    _check_slack_channel_exists(SLACK_API_TOKEN, slack_channel)
    slack_response = _publish_slack_message(SLACK_API_TOKEN,
                                            slack_channel,
                                            slack_message)

    resp = {
        'slack_response': slack_response,
        'status': 'OK'
    }

    if SNS_PUBLISH_RESPONSE:
        sns_response = _publish_sns_message(RESPONSE_SNS_TOPIC_ARN,
                                            slack_response)
        resp['sns_response'] = sns_response


    _logger.debug('Response: {}'.format(json.dumps(resp)))
    return resp

