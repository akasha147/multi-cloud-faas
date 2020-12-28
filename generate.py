import json
import os
import sys
import helper
import time
import subprocess

from aws.http import templates as aws_http
from aws.s3 import templates as aws_s3
from aws.dynamodb import templates as aws_dynamodb
from aws.iam import policyGenerator as aws_iam

from openwhisk.cos import templates as openwhisk_cos
from openwhisk.cloudant import templates as openwhisk_cloudant
from openwhisk.iam import policyGenerator as openwhisk_iam

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
	"python3" : "py",
	"python3.6":"py"
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
	print("Reading the requirements file and downloading the dependencies")
	requirements_file_path = os.path.join(input_dir,requirements_file)
	install_directory = os.path.join(input_dir,dependencies_output_dir)
	if os.stat(requirements_file_path).st_size != 0:
		os.makedirs(os.path.dirname(install_directory), exist_ok=True)#create the directory if doesn't exists
		os.system("pip3 install -r " + requirements_file_path +" -t "+install_directory	+" --system")
		os.system("rm -r "+os.path.join(install_directory,meta_data_pattern))
	


	#create a serverless package for each cloud
	package_name = config['package-name']
	runtime = config["runtime"]
	clouds = config['cloud-providers']
	default_cloud = config['default-cloud']
	dependencies = config['dependencies']
	
	serviceMapping = dict()
	functions = config["functions"]
	

	for function in functions:
		
		#Parse the config details
		function_name = function["name"]
		location = function["location"]
		target_cloud = function.get("target_cloud",default_cloud)
		trigger_cloud,resource = function.get("triggering_resource","::notrigger").split("::")
		trigger_type = function.get("trigger_type",None)
		resource_name = function.get("resource_name",None)
		iam = function.get("iam",None)
			
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

				# Create an aws role for the function and sleep to introduced delay
				role_name = package_name+"-"+function_name+"-role"
				os.system("aws iam create-role --role-name {role_name} --assume-role-policy-document file://aws/iam/initlambdapolicy.json".format(role_name=role_name))
				time.sleep(10) 
				
				# Create a directory for each function and copy the dependencies to it
				function_output_path =  os.path.join(output_dir,package_name,"functions",function_name)
				os.makedirs(os.path.join(function_output_path),exist_ok=True)
				os.system("cp -r "+os.path.join(install_directory,"*")+" "+function_output_path)
		
				#Get the function code and generate the serverless function
				raw_function_code = helper.giveFunctionData(os.path.join(input_dir,location),function_name)
				serverless_code = helper.generateServerlessFunction(raw_function_code,target_cloud,trigger_cloud,trigger_type)
				time.sleep(10) 

				os.makedirs(os.path.join(function_output_path,"multicloud"),exist_ok=True)
				files = ["__init__.py","handlers_aws.py","triggers.py"]
				for file in files:
					os.system("cp  multicloud/{file} {output_dir}".format(file=file,output_dir=os.path.join(function_output_path,"multicloud")))

				os.system("cp {path}/handlers_aws.py {path}/handlers.py".format(path=os.path.join(function_output_path,"multicloud")))
				os.system("rm {path}/handlers_aws.py".format(path=os.path.join(function_output_path,"multicloud")))

				#Add to function code to a file
				function_output_file = os.path.join(function_output_path,"run.py")
				with open(function_output_file,"w") as f:
					for module in dependencies:
						f.write("import "+module+"\n")
					f.write(serverless_code)

				#Zip the function code and the dependency modules
				os.system("cd {output_dir};zip -r function.zip *".format(output_dir=function_output_path))

				# create the lamdba function in aws
				os.system("aws lambda create-function --function-name {function_name} --zip-file fileb://{output_dir}/function.zip --handler {handler} --runtime {runtime} --role arn:aws:iam::779308551547:role/{role_name}"
						 .format(function_name = function_name,output_dir=function_output_path,
						 		 handler="run."+function_name,runtime=runtime,role_name=role_name))

				# get the trigger code and execute lambda permission code
				if resource!="notrigger":
					service = serviceMapping[trigger_cloud][resource]
					if service == "s3":
						execute_lambda_permission = aws_s3.execute_lambda_permission(function_name,resource_name)
						trigger_code =aws_s3.generate_s3_trigger(function_name,location.split(".")[0],resource_name,trigger_type)
						os.system(execute_lambda_permission)
						os.system(trigger_code)
					
					elif service == "https":
						api_response = subprocess.check_output("aws apigatewayv2 create-api --name {api_name} --protocol-type HTTP --target arn:aws:lambda:us-east-1:779308551547:function:{function_name}".format(api_name=function_name+"_api",function_name=function_name),shell=True).decode('utf-8')
						# api_id = subprocess.check_output('aws apigatewayv2 get-api --api-id {api_name}'.format(api_name=function_name+"_api"),shell=True).decode('utf-8')
						api_id = api_response.strip().split("\n")[4].strip().split(":")[-1][2:-2]	
						os.system("aws lambda add-permission --function-name {function_name} --statement-id apigateway-{function_name} --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:us-east-1:779308551547:{api_id}/*/*/{function_name}'".format(api_id=api_id,function_name=function_name))
				    
					elif service == "dynamodb":
						#Inorder to recieve dynamodb trigger the function needs some permissions beforehand so add those
						dynamodb_trigger_policy = aws_dynamodb.dynamodb_trigger_init_policy(tableName=resource_name)
						trigger_policy_file = os.path.join(function_output_path,"trigger-policy.json")
						with open(trigger_policy_file,"w") as fp:
							fp.write(dynamodb_trigger_policy)
						os.system("aws iam put-role-policy --role-name {role_name} --policy-name {policy_name} --policy-document file://{iam_policy_file}"
							.format(role_name=role_name,policy_name=package_name+"-"+function_name+"-trigger-policy",iam_policy_file=trigger_policy_file))
						time.sleep(10)
						#Get dynamostream arn 
						stream_arn = json.loads(subprocess.check_output('aws dynamodbstreams list-streams --table-name "{tablename}"'.format(tablename=resource_name),shell=True)
							.decode('utf8'))['Streams'][0]['StreamArn']
						trigger_code = aws_dynamodb.generate_dynamodb_trigger(function_name = function_name,arn=stream_arn)
						os.system(trigger_code)


				# Generate the iam policy code and write it to a json file
				iam_policy = helper.generatePolicy(function,default_cloud)
				iam_policy_file = os.path.join(function_output_path,"iam-policy.json")
				with open(iam_policy_file,"w") as fp:
					fp.write('{"Version": "2012-10-17","Statement": [')
					fp.write(",".join(iam_policy["aws"]))
					fp.write("]}")
				os.system("aws iam put-role-policy --role-name {role_name} --policy-name {policy_name} --policy-document file://{iam_policy_file}"
					.format(role_name=role_name,policy_name=package_name+"-"+function_name+"-policy",iam_policy_file=iam_policy_file))


			if target_cloud == "openwhisk":
				
										# Create a newnamespace for the function and switch to it
				os.system("ibmcloud fn namespace create "+package_name+"-"+function_name)
				os.system("ibmcloud fn property set --namespace "+package_name+"-"+function_name)

				raw_function_code = helper.giveFunctionData(os.path.join(input_dir,location),function_name)
				serverless_code = helper.generateServerlessFunction(raw_function_code,target_cloud,trigger_cloud,trigger_type)

				# Create a directory for each function and copy the dependencies to it
				function_output_path =  os.path.join(output_dir,package_name,"actions",function_name)
				os.makedirs(function_output_path,exist_ok=True)
				os.system("cp -r "+os.path.join(install_directory,"*")+" "+function_output_path)
				
				#Create a folder for multicloud
				os.makedirs(os.path.join(function_output_path,"multicloud"),exist_ok=True)
				files = ["__init__.py","handlers_openwhisk.py","triggers.py"]
				for file in files:
					os.system("cp  multicloud/{file} {output_dir}".format(file=file,output_dir=os.path.join(function_output_path,"multicloud")))
				os.system("cp {path}/handlers_openwhisk.py {path}/handlers.py".format(path=os.path.join(function_output_path,"multicloud")))
				os.system("rm {path}/handlers_openwhisk.py".format(path=os.path.join(function_output_path,"multicloud")))

				function_output_file = os.path.join(function_output_path,"__main__.py")
				with open(function_output_file,"w") as f:
					for module in dependencies:
						f.write("import "+module+"\n")
					f.write(serverless_code)

				os.system("cd {output_dir};zip -r function.zip *".format(output_dir=function_output_path))
				
				os.system("ibmcloud fn action create {function_name} {output_dir}/function.zip --kind python:3.7".format(output_dir=function_output_path,function_name=function_name))

				#Generate trigger_code and add it
				if resource!="notrigger":
					service = serviceMapping[target_cloud][resource]
					
					if service == "cloud-object-storage":
						trigger_code = openwhisk_cos.generate_cos_trigger(function_name,resource_name,trigger_type)
						os.system(trigger_code)
						#Create a rule to bind trigger-action
						os.system("ibmcloud fn rule create "+function_name+"-rule "+function_name+"-trigger "+function_name)

					elif service == "https":
						os.system("ibmcloud fn action update {function_name} --web true".format(function_name=function_name))
						url = subprocess.check_output("ibmcloud fn api create /{function_name} get {function_name} --response-type json".format(function_name=function_name),shell=True).decode("utf-8").strip().split("\n")[1]

					elif service == "cloudantnosqldb":
						#Need read permission to get the triggering resource
						os.system("ibmcloud iam service-id-unlock "+package_name+"-"+function_name)
						trigger_policy = openwhisk_iam.generateopenwhiskPolicy(package_name+"-"+function_name,resource_name,"no-sql-database",["trigger"])
						os.system(trigger_policy)

						#Need to create package and bind it cloudant service
						cloudant_package_name = function_name+"-cloudant"
						cloudant_instance_name = "Cloudant-serverless"
					
						os.system("ibmcloud fn package bind /whisk.system/cloudant {package_name}".format(package_name=cloudant_package_name))
						os.system("ibmcloud fn service bind cloudantnosqldb {package_name} --instance {instance} --keyname 'Service credentials-1'"
							.format(package_name=cloudant_package_name,instance=cloudant_instance_name)) 

						trigger_code = openwhisk_cloudant.generate_cloudant_trigger(cloudant_package_name,function_name,resource_name)
						os.system(trigger_code)
						os.system("ibmcloud fn rule create "+function_name+"-rule "+function_name+"-trigger "+function_name)

				#Add IAM policy if required	
				if iam: 
					#Unlock the service id to add the iam polices
					os.system("ibmcloud iam service-id-unlock "+package_name+"-"+function_name)

					#Create IAM Policies and attach them to the corresponding service(namespace)
					iam_policy  = helper.generatePolicy(function,default_cloud)
					for policy in iam_policy[target_cloud]:
						os.system(policy)
				


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

		














		

		



		



