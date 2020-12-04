from string import Template

triggerMappings = {
	
	"insert" :"write"
}

# ibmcloud fn trigger create test-trigger --feed /whisk.system/cos/changes -p bucket "out-check"-p event_types "write"

cos_trigger_template = Template(""" ibmcloud fn trigger create $triggername --feed /whisk.system/cos/changes -p bucket "$bucketname" -p event_types "$event" """)

def generate_cos_trigger(function_name,resource,event):
	return cos_trigger_template.substitute(triggername = function_name+"-trigger",bucketname=resource,event=triggerMappings[event])