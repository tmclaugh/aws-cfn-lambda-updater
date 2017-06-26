# aws-cfn-lambda-updater [![Build Status](https://travis-ci.org/tmclaugh/aws-cfn-lambda-updater.svg?branch=master)](https://travis-ci.org/tmclaugh/aws-cfn-lambda-updater)
Lambda function to update other Lambda function when called via CloudFormation.

This repository contains two Lambda functions along with CloudFormation templates for each function.

* __aws-cfn-lambda-updater__: Function for updating an AWS Lambda function when triggered via AWS CLoudFormation.
  * _deployable code_: https://s3.amazonaws.com/straycat-dhs-org-straycat-lambda-deploys/aws-cfn-lambda-updater.zip
  * _CloudFormation template_: https://s3.amazonaws.com/straycat-dhs-org-straycat-lambda-deploys/aws-cfn-lambda-updater.json
* __aws-cfn-lambda-updater-example-lambda__: Simple “Hello World” function to demonstrate using aws-cfn-lambda-updater.
  * _deployable code_: https://s3.amazonaws.com/straycat-dhs-org-straycat-lambda-deploys/aws-cfn-lambda-updater-example-lambda.zip
  * _CloudFormation template_: https://s3.amazonaws.com/straycat-dhs-org-straycat-lambda-deploys/aws-cfn-lambda-updater-example-lambda.json

## Deployment
Deploying Both stacks can be done by clicking on "Launch Stack" below.

* __aws-cfn-lambda-updater__: [![Launch CloudFormation
Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=aws-cfn-lambda-updater&templateURL=https://s3.amazonaws.com/straycat-dhs-org-straycat-lambda-deploys/aws-cfn-lambda-updater.json)
* __aws-cfn-lambda-updater-example-lambda__: [![Launch CloudFormation
Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=aws-cfn-lambda-updater-example-lambda&templateURL=https://s3.amazonaws.com/straycat-dhs-org-straycat-lambda-deploys/aws-cfn-lambda-updater-example-lambda.json)

## Usage
To use _aws-cfn-lambda-updater_ to update another Lambda function that is deployed via CloudFormation, add a resource similar to the following to your CloudFormation template.  You’ll need to add parameters for _LambdaName_ and _S3Bucket_.

```json
"LambdaInvokeUpdater": {
  "Type": "Custom::LambdaUpdaterInvoke",
  "Properties": {
    "ServiceToken":{
      "Fn::ImportValue": {
        "Fn::Sub": "aws-cfn-lambda-updater-LambdaFunctionArn"
      }
    },
    "FunctionName": {
      "Ref": "LambdaName"
    },
    "S3Bucket": {
      "Ref": "S3Bucket"
    },
    "S3Key": {
      "Fn::Sub": "${LambdaName}.zip"
    }
  }
}
```

To ensure that the _LambdaInvokeUpdater_ resource requires an update on each version, add a command like the following to your build process.

```
$ python -c "import json, sys; cfn=json.load(sys.stdin); cfn['Resources']['LambdaInvokeUpdater']['Properties']['CodeSha256'] = '$(openssl dgst -binary -sha256 dist/aws-cfn-lambda-updater.zip | openssl base64)'; json.dump(cfn, sys.stdout, indent=2)" < dist/aws-cfn-lambda-updater-example-lambda.json > dist/aws-cfn-lambda-updater-example-lambda.json.new; mv dist/aws-cfn-lambda-updater-example-lambda.json{.new,}

```

See this repository’s _.travis.yml_ for an example in practice.

