from string import Template

triggerMappings = {
	
	"insert" :"s3:ObjectCreated:*"
}

init_trigger_policy = Template("""{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetShardIterator",
                "dynamodb:DescribeStream",
                "dynamodb:GetRecords"
            ],
            "Resource": "arn:aws:dynamodb:*:779308551547:table/$tablename/stream/*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "dynamodb:ListStreams",
            "Resource": "*"
        }
    ]
}

""")

dynamodb_trigger_template = Template(""" aws lambda create-event-source-mapping --function-name $functionname --batch-size 1 --starting-position LATEST --event-source-arn $arn""")

# s3_trigger_template = Template("""aws s3api put-bucket-notification-configuration --bucket $bucket --notification-configuration '{"LambdaFunctionConfigurations": [{"Id": "$sid","LambdaFunctionArn": "arn:aws:lambda:us-east-1:779308551547:function:$func_name","Events": ["$event"]}]}'""")
# execute_lambda_template = Template("aws lambda add-permission --function-name $func_name --action lambda:InvokeFunction --statement-id $sid  --principal s3.amazonaws.com --source-arn arn:aws:s3:::$bucket_name")

# def generate_s3_trigger(function_name,location,resource,event):
# 	return s3_trigger_template.substitute(func_name=function_name,bucket=resource,sid=function_name+resource+"-trigger",event=triggerMappings[event])

# def execute_lambda_permission(function_name,bucket_name):
# 	return execute_lambda_template.substitute(func_name=function_name,bucket_name=bucket_name,sid=function_name+bucket_name)

def dynamodb_trigger_init_policy(tableName):
	return init_trigger_policy.substitute(tablename=tableName)

def generate_dynamodb_trigger(function_name,arn):
	return dynamodb_trigger_template.substitute(functionname=function_name,arn=arn)