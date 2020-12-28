from string import Template


serviceMappings =  {
	"storage":"cloud-object-storage",
	"no-sql-database":"cloudantnosqldb"
}

permissions_mapping = {
	"cloud-object-storage":{
		"read":"Reader",
		"write":"Writer"
	},
	"cloudantnosqldb":
	{
		"insert":"Writer",
		"trigger":"Writer",
		"scan":"Reader"
	}
}

resources = {
	
	"cloud-object-storage" : "bucket"
}


storage_policy_template = Template(""" ibmcloud iam service-policy-create $servicename  --roles "$role" --service-name $service --resource-type $resource --resource "$name" """)
db_policy_template = Template("""ibmcloud iam service-policy-create $servicename  --roles "$role" --service-name $service""")
def generateopenwhiskPolicy(servicename,resource_name,resource_type,permissions):
	service = serviceMappings[resource_type]
	role = ",".join([permissions_mapping[service][p] for p in permissions])
	if resource_type == "storage":
		resource = resources[service]
		return policy_template.substitute(servicename=servicename,role =role,service=service,resource=resource,name=resource_name)
	if resource_type == "no-sql-database":
		return db_policy_template.substitute(servicename=servicename,role=role,service=service)

		
	

