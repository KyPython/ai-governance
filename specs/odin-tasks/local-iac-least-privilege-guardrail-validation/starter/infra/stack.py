"""Build the parcel indexer's CloudFormation-compatible template."""

from typing import Any


def build_template() -> dict[str, Any]:
    """Return a fresh deterministic infrastructure template."""
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Synthetic parcel indexer resources",
        "Resources": {
            "ParcelRecordsBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketEncryption": {
                        "ServerSideEncryptionConfiguration": [
                            {"ServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}
                        ]
                    },
                    "PublicAccessBlockConfiguration": {
                        "BlockPublicAcls": True,
                        "BlockPublicPolicy": True,
                        "IgnorePublicAcls": True,
                        "RestrictPublicBuckets": True,
                    },
                },
            },
            "ParcelEventsQueue": {
                "Type": "AWS::SQS::Queue",
                "Properties": {
                    "KmsMasterKeyId": "alias/aws/sqs",
                    "VisibilityTimeout": 120,
                },
            },
            "ParcelIndexerRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"Service": "lambda.amazonaws.com"},
                                "Action": "sts:AssumeRole",
                            }
                        ],
                    },
                    "Policies": [
                        {
                            "PolicyName": "parcel-record-access",
                            "PolicyDocument": {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": "s3:*",
                                        "Resource": "*",
                                    }
                                ],
                            },
                        }
                    ],
                },
            },
        },
    }
