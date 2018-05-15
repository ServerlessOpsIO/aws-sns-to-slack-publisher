'''Test health_event_publisher'''
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name
import json
import os

import boto3
import pytest

EVENT_FILE = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'events',
    'aws_sns_to_slack_publisher.json'
)


@pytest.fixture()
def event(event_file=EVENT_FILE):
    '''Trigger event'''
    with open(event_file) as f:
        return json.load(f)


@pytest.fixture()
def cfn_stack_name():
    '''Return name of stack to get Lambda from'''
    # FIXME: We should eventually read serverless.yml to figure it out.
    # Handling different environments would be good too.
    return 'aws-sns-to-slack-publisher-dev'


@pytest.fixture()
def lambda_client():
    '''Lambda client'''
    return boto3.client('lambda')


@pytest.fixture()
def lambda_function(cfn_stack_name):
    '''Return Lambda function name'''
    return '-'.join([cfn_stack_name, 'SlackPublish'])


def test_handler(lambda_client, lambda_function, event):
    '''Test handler'''
    r = lambda_client.invoke(
        FunctionName=lambda_function,
        InvocationType='RequestResponse',
        Payload=json.dumps(event).encode()
    )

    lambda_return = r.get('Payload').read()
    slack_response = json.loads(lambda_return).get('slack_response')

    assert slack_response.get('ok') is True

