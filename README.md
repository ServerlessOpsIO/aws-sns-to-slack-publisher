# aws-sns-to-slack-publisher
[![Serverless](http://public.serverless.com/badges/v3.svg)](http://www.serverless.com)
[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

Publish a message received from SNS to Slack

![System Architecture](/diagram.png?raw=true "System Architecture")

## Outputs

* __aws-sns-to-slack-publisherr-${stage}-SlackResponseSnsTopicArn__: Topic to which Slack publishing responses are sent.
