from string import Template


serviceMappings =  {
	"storage":"s3",
	"logs":"logs",
	"no-sql-database":"dynamodb"
}

permissions_mapping = {
	"s3":{
		"read":["GetObject","GetObjectAcl"],
		"write":["PutObject","PutObjectAcl"]
	},
	"logs":{
		"create":["CreateLogStream","CreateLogGroup"],
		"write":["PutLogEvents"]
	},
	"dynamodb":{
		"insert":["PutItem"],
		"scan":["scan"]
	}
}




"""
 - Effect: Allow
      Action:
        - s3:PutObject
        - s3:PutObjectAcl
      Resource: "arn:aws:s3:::${self:custom.outputBucket}/*"print json.dumps({'4': 5, '6': 7}, sort_keys=True, indent=4)
"""


policy_template = Template("""{"Sid": "$sid","Effect": "Allow","Action": [$action],"Resource": ["$arn"]}""")
def generateawsPolicy(resource_name,resource_type,permissions,sid):
	aws_resource = serviceMappings[resource_type]
	aws_permission_list = []
	for permission in permissions:
		aws_permission_list = aws_permission_list + ['"'+aws_resource+":"+permission+'"' for permission in permissions_mapping[aws_resource][permission]]
	action = ",".join(aws_permission_list)
	if aws_resource == "logs":
		arn = "arn:aws:logs:us-east-1:779308551547:log-group:/aws/lambda/"+resource_name
	elif aws_resource == "s3":
		arn = "arn:aws:"+aws_resource+":::"+resource_name+"/*"
	elif aws_resource == "dynamodb":
		arn = "arn:aws:dynamodb:us-east-1:*:table/"+resource_name
	return policy_template.substitute(sid=sid,action=action,arn=arn)
		
	

