import json
import os
import sys
import helper
from aws.http import templates as aws_http
from aws.s3 import templates as aws_s3

config_file_name = "config.json"
service_mapping_file = "serviceMapping.json"
serverless_config_file = "serverless.yml"
requirements_file = "requirements.txt"
dependencies_output_dir = "modules"
meta_data_pattern = "*dist-info"



if __name__ == '__main__':
	
	#location to the source code
	input_dir = sys.argv[1]
	output_dir = sys.argv[2]
	print("Entering " + input_dir)
	
	#read the config_file
	print("Reading the config file")
	config_file_path = os.path.join(input_dir,config_file_name)
	with open(config_file_path, 'r') as j:
		config = json.loads(j.read())

	#download the dependencies
	print("Reading the requirements file and downloading the dependencies")
	requirements_file_path = os.path.join(input_dir,requirements_file)
	install_directory = os.path.join(input_dir,dependencies_output_dir)
	os.makedirs(os.path.dirname(install_directory), exist_ok=True)#create the directory if doesn't exists
	os.system("pip3 install -r " + requirements_file_path +" -t "+install_directory	+" --system")
	os.system("rm -r "+os.path.join(install_directory,meta_data_pattern))




	#create a serverless package for each cloud
	package_name = config['package-name']
	runtime = config["runtime"]
	clouds = config['cloud-providers']
	default_cloud = config['default-cloud']
	dependencies = config['dependencies']

	for cloud in clouds:
		print("Creating serverless template for " + cloud)
		os.system("serverless create --template " + "aws" + "-" + runtime + " --path " + os.path.join(output_dir,cloud+"-"+package_name))
		os.system("cp -r "+os.path.join(install_directory,"*")+" "+os.path.join(output_dir,cloud+"-"+package_name))
	
	#process the functions
	
	serviceMapping = dict()
	functions = config["functions"]
	

	for function in functions:
		
		#Parse the config details
		function_name = function["name"]
		location = function["location"]
		target_cloud = function["target_cloud"]
		trigger_cloud,resource = function["triggering_resource"].split("::")
		trigger_type = function["trigger_type"]
		resource_name = function["resource_name"]
		
		if not trigger_cloud:
			trigger_cloud = default_cloud


		#Get the generic resource name to cloud service mappings
		if trigger_cloud not in serviceMapping.keys():
			with open(os.path.join(trigger_cloud,service_mapping_file)) as j:
				serviceMapping[trigger_cloud] = json.loads(j.read())
		
		#Get the service name
		service = serviceMapping[trigger_cloud][resource]
		
		#Get the function code
		function_code = helper.giveFunctionData(os.path.join(input_dir,location),function_name)

		if True:
			# 1.Generate http-endpoint-trigger
			# Get the function code and write it in the approriate file
			function_code = helper.giveFunctionData(os.path.join(input_dir,location),function_name)
			function_output_file =  os.path.join(output_dir,target_cloud+"-"+package_name,location)
			
			os.makedirs(os.path.dirname(function_output_file), exist_ok=True) #create the directories if it doesn't exist
			
			with open(function_output_file,"a+") as f:
				if os.stat(function_output_file).st_size == 0:#write the import statements when the file is created
					for module in dependencies:
						f.write("import "+module+"\n")
				f.write(function_code)
			
			# Get the trigger config code in the serverless format
			trigger_code = aws_http.generate_http_endpoint(function_name,location.split(".")[0])
			trigger_config_file = os.path.join(output_dir,target_cloud+"-"+package_name,serverless_config_file)
			with open(trigger_config_file,"a+") as f:
				f.write(trigger_code)

			#2.Assuming the http endpoint exists beforehand,generate a function that acts as a proxy event handler and forward the event to the corresponding function
			http_trigger_url = "https://wmhf3xkfoj.execute-api.us-east-1.amazonaws.com/dev/read_s3"
			proxy_function_code = aws_http.generate_http_proxy_function(function_name,http_trigger_url)

			proxy_function_output_file =  os.path.join(output_dir,trigger_cloud+"-"+package_name,location)
			
			os.makedirs(os.path.dirname(proxy_function_output_file), exist_ok=True) #create the directories if it doesn't exist
			
			with open(proxy_function_output_file,"a+") as f:
				if os.stat(proxy_function_output_file).st_size == 0:#write the import statements when the file is created
					for module in dependencies:
						f.write("import "+module+"\n")
				f.write(proxy_function_code)
			
			# Get the trigger config code in the serverless format
			proxy_trigger_code = aws_s3.generate_s3_trigger(function_name,location.split(".")[0],resource_name,trigger_type)
			proxy_trigger_config_file = os.path.join(output_dir,trigger_cloud+"-"+package_name,serverless_config_file)
			with open(proxy_trigger_config_file,"a+") as f:
				f.write(proxy_trigger_code)

		














		

		



		



