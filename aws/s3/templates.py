from string import Template

triggerMappings = {
	
	"insert" :"s3:ObjectCreated:*"
}

s3_trigger_template = Template("""
  $func_name:
    handler: $handler
    events:
      - s3:
          bucket: $bucket
          event: $event
""")

def generate_s3_trigger(function_name,location,resource,event):
	return s3_trigger_template.substitute(func_name=function_name+"_proxy",handler=location+"."+function_name+"_proxy",bucket=resource,event=triggerMappings[event])