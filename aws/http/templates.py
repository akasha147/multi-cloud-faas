from string import Template

trigger_template = Template("""
  $func_name:
    handler: $handler
    events:
      - http:
          path: $path
          method: $method
""")

http_proxy_function_template = Template("""
def $func_name(event, context):
    url =  "$url"
    parameters = event
    
    response = requests.get(url=url,params=parameters)
    print(response.json())
""")

def generate_http_endpoint(function_name,location,method="get"):
	return trigger_template.substitute(func_name=function_name,handler=location+"."+function_name,path=function_name,method=method)
def generate_http_proxy_function(function_name,url):
	return http_proxy_function_template.substitute(func_name=function_name+"_proxy",url=url)