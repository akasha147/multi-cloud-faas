import json
import os
import sys
import helper

from aws.http import templates as aws_http
from aws.s3 import templates as aws_s3
from aws.iam import policyGenerator as aws_iam

from openwhisk.cos import templates as openwhisk_cos

config_file_name = "config.json"
service_mapping_file = "serviceMapping.json"
serverless_config_file = "serverless.yml"
requirements_file = "requirements.txt"
dependencies_output_dir = "modules"
meta_data_pattern = "*dist-info"

serviceMappings =  {
	"aws" :
			{
	  		  "storage":"s3"
	  		 }
}

runtimeExtensions = {
	"python3" : "py"
}


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
	# print("Reading the requirements file and downloading the dependencies")
	# requirements_file_path = os.path.join(input_dir,requirements_file)
	# install_directory = os.path.join(input_dir,dependencies_output_dir)
	# os.makedirs(os.path.dirname(install_directory), exist_ok=True)#create the directory if doesn't exists
	# os.system("pip3 install -r " + requirements_file_path +" -t "+install_directory	+" --system")
	# os.system("rm -r "+os.path.join(install_directory,meta_data_pattern))
	# #copy the multi-cloud-library to the modules followed
	# os.system("cp -r multicloud "+os.path.join(install_directory))




	#create a serverless package for each cloud
	package_name = config['package-name']
	runtime = config["runtime"]
	clouds = config['cloud-providers']
	default_cloud = config['default-cloud']
	dependencies = config['dependencies']

	# for cloud in clouds:
	# 	print("Creating serverless template for " + cloud)
	# 	os.system("serverless create --template " + "aws" + "-" + runtime + " --path " + os.path.join(output_dir,cloud+"-"+package_name))
	# 	os.system("cp -r "+os.path.join(install_directory,"*")+" "+os.path.join(output_dir,cloud+"-"+package_name))
	
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
		iam = function["iam"]
			
		function["package"] = package_name

		if not trigger_cloud:
			trigger_cloud = default_cloud


		#Get the generic resource name to cloud service mappings
		if trigger_cloud not in serviceMapping.keys():
			with open(os.path.join(trigger_cloud,service_mapping_file)) as j:
				serviceMapping[trigger_cloud] = json.loads(j.read())
		

		#Single Cloud Scenario
		if trigger_cloud ==target_cloud:
			if target_cloud == "aws":
				
				#Get the function code and generate the serverless function
				raw_function_code = helper.giveFunctionData(os.path.join(input_dir,location),function_name)
				serverless_code = helper.generateServerlessFunction(raw_function_code,target_cloud,trigger_cloud,trigger_type)
				
				#Generate the iam policy code if exists
				iam_policy = helper.generatePolicy(function,default_cloud)

				#Write the function to the respective_file
				function_output_file =  os.path.join(output_dir,target_cloud+"-"+package_name,location)
				os.makedirs(os.path.dirname(function_output_file), exist_ok=True) #create the directories if it doesn't exist
				
				with open(function_output_file,"a+") as f:
					if os.stat(function_output_file).st_size == 0:#write the import statements when the file is created
						for module in dependencies:
							f.write("import "+module+"\n")
					f.write(serverless_code)

				#Copy the basic config details into a new config file
				config_file_path = os.path.join(output_dir,target_cloud+"-"+package_name,serverless_config_file)
				basic_config = helper.generateBasicConfigFile(target_cloud+"-"+package_name,target_cloud,runtime)

				#Generate the trigger code based on the service	
				service = serviceMapping[target_cloud][resource]
				if service == "s3":
					trigger_code = aws_s3.generate_s3_trigger(function_name,location.split(".")[0],resource_name,trigger_type)

				with open(config_file_path,"w") as f:
					f.write(basic_config)
					f.write(iam_policy["init"])
					f.write("\n".join(iam_policy[target_cloud]))
					f.write("\n\nfunctions:")
					f.write(trigger_code)

			if target_cloud == "openwhisk":
				#Create a newnamespace for the function and switch to it
				os.system("ibmcloud fn namespace create "+package_name+"-"+function_name)
				os.system("ibmcloud fn property set --namespace "+package_name+"-"+function_name)

				raw_function_code = helper.giveFunctionData(os.path.join(input_dir,location),function_name)
				serverless_code = helper.generateServerlessFunction(raw_function_code,target_cloud,trigger_cloud,trigger_type)

				#Create the function-file and corresponding openwhisk action
				function_file = os.path.join(input_dir,function_name+"."+runtimeExtensions[runtime])

				# output multi-cloud-library classes into the function file
				os.system("cat multicloud/handlers.py >>"+function_file)
				os.system("cat multicloud/triggers.py >>"+function_file)


				with open(function_file,"a+") as f:
					f.write(serverless_code)
				
				os.system("ibmcloud fn action create " + function_name+" "+function_file)

				#Generate trigger_code and add it
				service = serviceMapping[target_cloud][resource]
				if service == "cloud-object-storage":
					trigger_code = openwhisk_cos.generate_cos_trigger(function_name,resource_name,trigger_type)
				os.system(trigger_code)

				#Create a rule to bind trigger-action
				os.system("ibmcloud fn rule create "+function_name+"-rule "+function_name+"-trigger "+function_name)

				#Unlock the service id to add the iam polices
				os.system("ibmcloud iam service-id-unlock "+package_name+"-"+function_name)

				#Create IAM Policies and attach them to the corresponding service(namespace)
				iam_policy  = helper.generatePolicy(function,default_cloud)
				for policy in iam_policy[target_cloud]:
					os.system(policy)
			


			# with open(os.path.joininput_dir"serverless.yml")

			# #Write the trigger details into the serverless config file
			# trigger_code = aws_s3.generate_s3_trigger(function_name,location.split(".")[0],resource_name,trigger_type)
			# trigger_config_file = os.path.join(output_dir,target_cloud+"-"+package_name,serverless_config_file)
			# with open(trigger_config_file,"a+") as f:
			# 	f.write(trigger_code)

			# if len(iam_policy):




		if trigger_cloud!=target_cloud:
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

		














		

		



		



