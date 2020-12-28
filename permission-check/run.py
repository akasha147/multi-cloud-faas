
import boto3
from botocore.exceptions import ClientError
def handler(event,context):
	client = boto3.client('sns')
	try:
		response = client.publish(TopicArn = 'arn:aws:sns:us-east-1:779308551547:product_specification.fifo',Message = 'hello')
		return { 'response' : 'NO' }
	except ClientError as e:
		return { 'response' : e.response['Error']['Code']}

