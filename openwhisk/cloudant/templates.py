from string import Template


# ibmcloud fn trigger create test-trigger --feed /whisk.system/cos/changes -p bucket "out-check"-p event_types "write"

cloudant_trigger_template = Template(""" ibmcloud fn trigger create $triggername --feed /_/$package_name/changes --param dbname "$dbname" """)

def generate_cloudant_trigger(package_name,function_name,resource):
	return cloudant_trigger_template.substitute(package_name=package_name,triggername = function_name+"-trigger",dbname=resource)