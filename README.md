# aws-sns-to-slack-publisher
[![Serverless](http://public.serverless.com/badges/v3.svg)](http://www.serverless.com)
[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)
[![Build Status](https://travis-ci.org/ServerlessOpsIO/aws-sns-to-slack-publisher.svg?branch=master)](https://travis-ci.org/ServerlessOpsIO/aws-sns-to-slack-publisher)

Publish a message received from SNS to Slack.

![System Architecture](/diagram.png?raw=true "System Architecture")

This service requires an SNS topic for it to subscribe to.  It will receive SNS messages formatted for the _chat.postMessage_ Slack API for publishing to Slack.

Example service:

* [aws-health-event-to-slack-message](https://github.com/ServerlessOpsIO/aws-health-event-to-slack-message)

## Slack App setup
This service requires the creation of a Slack App in your organization.  It will use the credentials and permissions of that app in order to post messages.

### 1) Sign in to your Slack workspace.
click the link below to sign into the desired Slack workspace.

* [Slack login](https://slack.com/signin)

### 2) Create a Slack app in your workspace.
Click the link below and on that page click the __"Create New App"__ button.

* [Slack Apps page](https://api.slack.com/apps)

Give the app a name and select the workspace.

![Slack Create App](/doc/create-new-app.png?raw=true "Slack Create App")

### 3) Obtain OAuth token and select permissions.

OAuth Tokens & Redirect URLs

Click _"OAuth & Permissions"_ in the left side bar.  On that page under the __OAuth Tokens & Redirect URLs__ section obtain an _OAuth Access Token_.  You will need that to deploy this service.

Under the __Scopes__ section add the following:

* channels:read
* chat:write:bot

Once you've saved settings, your Slack bot is configured.

## Service Interface

* __Event Type:__ AWS SNS
* __SNS Message:__ Message should be a JSON formatted string that conforms to the _chat.postMessage_ Slack API method.  See also [slack-message-schema.json](/slack-message-schema.json) in this repository to understand more about the message shape.

## Deployment

You will need the following in order to deploy and use this service.

* A Slack App API key
* A Slack channel
* The CloudFormation export value of the SNS topic ARN this should subscribe to.

In addition, this service can optionally publish responses from the Slack API to an SNS topic so the responses may be processed.  You may toggle this attribute of the stack as well.

This application is intended to be deployed using [AWS Serverless Application Repository](https://aws.amazon.com/serverless/serverlessrepo/).  However, [Serverless Framework](https://www.serverless.com) is also supported.

### Serverless Application Repository / CloudFormation

When deploying via Serverless Application Repository or CloudFormation, you will be presented with the following parameters to configure.

* __SlackApiToken (Required):__ API token to use when publishing to slack.
* __SlackDefaultChannel:__ Channel messages should be published to.
* __SnsPublishResponse:__ Name of the CloudFormation export to find the event source SNS topic to subscribe
* __SnsPublisherTopicExport (Required):__ Whether to publish Slack API responses to an SNS topic.

__AWS Serverless Application Repository:__ [aws-sns-to-slack-publisher](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:641494176294:applications~aws-sns-to-slack-publisher)

### Serverless Framework

To configure the deployment of this service, the following environment variables may be set when running `sls deploy`.

* **SLACK_API_TOKEN** (Required): API token to use when publishing to slack.
* **SLACK_DEFAULT_CHANNEL:** Channel messages should be published to.
* **SNS_PUBLISHER_TOPIC_EXPORT (Required):** Name of the CloudFormation export to find the event source SNS topic to subscribe to.
* **SNS_PUBLISH_RESPONSE (Values: 'true'|'false'):** Whether to publish Slack API responses to an SNS topic.

```
$ npm install -g serverless
$ npm install
$ SLACK_API_TOKEN=|TOKEN| SNS_PUBLISHER_TOPIC_EXPORT=|CFN_EXPORT| serverless deploy -v
```

## Exports

These values may be used by other services in your AWS infrastructure.

* __${AWS::StackName}-SlackResponseSnsTopicArn__: Topic to which Slack publishing responses are sent.
