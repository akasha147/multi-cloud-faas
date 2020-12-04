from string import Template


serviceMappings =  {
	"storage":"cloud-object-storage"
}

permissions_mapping = {
	"cloud-object-storage":{
		"read":"Reader",
		"write":"Writer"
	}
}

resources = {
	
	"cloud-object-storage" : "bucket"
}


policy_template = Template(""" ibmcloud iam service-policy-create $servicename  --roles "$role" --service-name $service --resource-type $resource --resource "$name" """)

def generateopenwhiskPolicy(servicename,resource_name,resource_type,permissions):
	service = serviceMappings[resource_type]
	role = ",".join([permissions_mapping[service][p] for p in permissions])
	resource = resources[service]
	return policy_template.substitute(servicename=servicename,role =role,service=service,resource=resource,name=resource_name)

		
	

