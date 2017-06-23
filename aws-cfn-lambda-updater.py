#!env python
import boto3
import cfn_resource
import io
import json
import logging
from logging.config import fileConfig
import os
import sys
import zipfile

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

dirname = os.path.dirname(__file__)
logging_conf = os.path.join(dirname, 'logging.conf')
fileConfig(logging_conf, disable_existing_loggers=False)
if os.environ.get('TS_DEBUG'):
    logging.root.setLevel(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

handler = cfn_resource.Resource()

def _fetch_zip_file(url):
    '''
    Fetch a file from a URL and return a file-like object.
    '''

    # We'll throw an exception if we don't receive a successful response.
    u = urlopen(url)
    zip_file = io.BytesIO(u.read())

    if zipfile.is_zipfile(zip_file):
        zip_file.seek(0)
    else:
        raise Exception('Not valid zipfile.')

    return zip_file

@handler.update
def update_lambda(event, context):
    '''
    Update a lambda function.
    '''
    _logger.info('CloudFormation event received: {}'.format(json.dumps(event)))

    # get Properties keys sent from CFN.
    # ref: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requests.html
    properties = event.get('ResourceProperties')
    function_name = properties.get('FunctionName')
    function_zip_file_url = properties.get('FunctionZipFileUrl')
    function_s3_bucket = properties.get('FunctionS3Bucket')
    function_s3_key = properties.get('FunctionS3Key')
    function_code_sha256 = properties.get('CodeSha256')

    # S3{Bucket,Key} require S3 permissions/IAM policy for access. If using a
    # URL then we must fetch and get bytes.
    lambda_update_kwargs = {
        'FunctionName': function_name,
        'Publish': True
    }

    if function_zip_file_url:
        function_zip_file_bytes = _fetch_zip_file(function_zip_file_url)
        additional_args = {
            'ZipFile': function_zip_file_bytes.read()
        }
        lambda_update_kwargs.update(additional_args)
    else:
        additional_args = {
            'S3Bucket': function_s3_bucket,
            'S3Key': function_s3_key,
        }
        lambda_update_kwargs.update(additional_args)

    # Update Lambda function
    lambda_client = boto3.client('lambda')
    lambda_update_resp = lambda_client.update_function_code(**lambda_update_kwargs)
    _logger.debug('lambda_update_resp: {}'.format(lambda_update_resp))

    # NOTE: We don't error check here because update rollbacks would fail
    # since we don't have the ability to roll a function back.

    # Construct our CFN response. cfn_resource will handle setting RequestId.
    # ref: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-responses.html
    cfn_resp = {
        'Data': lambda_update_resp,
    }

    # cfn_resource will log the response so this is here only to aide if we
    # suspect issues communicating back to CFN successfully.
    _logger.debug('cfn_resp: {}'.format(json.dumps(cfn_resp)))

    # cfn_resource will signal CFN with this.
    return cfn_resp

