
from string import Template


serviceMappings =  {
	"storage":"s3"
}

permissions_mapping = {
	"s3":{
		"read":["GetObject","GetObjectAcl"],
		"write":["PutObject","PutObjectAcl"]
	}
}

"""
 - Effect: Allow
      Action:
        - s3:PutObject
        - s3:PutObjectAcl
      Resource: "arn:aws:s3:::${self:custom.outputBucket}/*"
"""


policy_template = Template("""
    - Effect: Allow
      Action: $action
      Resource: "$arn" """)

def generateawsPolicy(resource_name,resource_type,cloudName,permissions):
	aws_resource = serviceMappings[resource_type]
	aws_permission_list = []
	for permission in permissions:
		aws_permission_list = aws_permission_list + permissions_mapping[aws_resource][permission]
	action = ""
	for aws_permission in aws_permission_list:
		action+="\n          - "
		action+=aws_resource+":"+aws_permission
	arn = "arn:aws:"+aws_resource+":::"+resource_name
	return policy_template.substitute(action=action,arn=arn)
		
	

