from string import Template

triggerMappings = {
	
	"insert" :"s3:ObjectCreated:*"
}

s3_trigger_template = Template("""aws s3api put-bucket-notification-configuration --bucket $bucket --notification-configuration '{"LambdaFunctionConfigurations": [{"Id": "$sid","LambdaFunctionArn": "arn:aws:lambda:us-east-1:779308551547:function:$func_name","Events": ["$event"]}]}'""")
execute_lambda_template = Template("aws lambda add-permission --function-name $func_name --action lambda:InvokeFunction --statement-id $sid  --principal s3.amazonaws.com --source-arn arn:aws:s3:::$bucket_name")

def generate_s3_trigger(function_name,location,resource,event):
	return s3_trigger_template.substitute(func_name=function_name,bucket=resource,sid=function_name+resource+"-trigger",event=triggerMappings[event])

def execute_lambda_permission(function_name,bucket_name):
	return execute_lambda_template.substitute(func_name=function_name,bucket_name=bucket_name,sid=function_name+bucket_name)