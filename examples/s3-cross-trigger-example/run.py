import json
def read_s3(event,context):
	return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda akash!')
    	}