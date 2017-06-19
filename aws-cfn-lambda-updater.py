#!env python
import boto3
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

def handler(event, context):
    '''
    Update a lambda function.
    '''
    _logger.info('Event received: {}'.format(json.dumps(event)))

    function_name = event.get('FunctionName')
    function_zip_file_url = event.get('FunctionZipFileUrl')
    function_s3_bucket = event.get('FunctionS3Bucket')
    function_s3_key = event.get('FunctionS3Key')

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

    _logger.debug('lambda_update_resp: {}'.format(json.dumps(lambda_update_resp)))

    return lambda_update_resp

