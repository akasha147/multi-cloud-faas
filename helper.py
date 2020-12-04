import aws.iam
import openwhisk.iam.policyGenerator
import re
from string import Template

#Extract the function code from the file
def giveFunctionData(filename, function):
    function_content = ''
    data = open(filename)
    # Tells us whether to append lines to the `function_content` string
    record_content = False
    for line in data:
        if not record_content:
            # Once we find a match, we start recording lines
            if function in line and line.startswith('def'):
                function_content+=line
                record_content = True
        else:
            # We keep recording until we encounter another function
            if line.startswith('def'):
                break
            function_content+=line

    return function_content


#Generate the serverless code from the raw function code
def generateServerlessFunction(function,targetCloud,triggerCloud,triggerType):
    serverlessFunction = ""
    lines = function.split("\n")
    if targetCloud == "openwhisk":
        lines[0] = "def main(event):"
    for line in lines:
        #Replace the cloudname variables with respective cloud name
        line = re.sub("multicloud\.getTriggerCloud\(\)",'"'+triggerCloud+'"',line)
        line = re.sub("multicloud\.getTargetCloud\(\)",'"'+targetCloud+'"',line)

        if targetCloud == "openwhisk":
            line = re.sub("multicloud\..*\.","",line)
        serverlessFunction+=line+"\n"  
    return serverlessFunction



init_policy_template = Template("""
  region: us-east-1
  iamRoleStatements: """)
#Generate the iam policy code for the given configuration
def generatePolicy(config,defaultCloud):
    iam = config['iam']
    func_name,package_name = config["name"],config["package"]
    policies = {}
    policies["init"] = init_policy_template.substitute()
    
    for policy in iam:
        resource_name = policy["resource_name"]
        cloudName,resource_type = policy["resource_type"].split("::")
        if not cloudName:
            cloudName = defaultCloud
        permissions = [p for p in policy["permissions"]]
        if cloudName == "aws":
            p = aws.iam.policyGenerator.generateawsPolicy(resource_name,resource_type,cloudName,permissions)
        if cloudName == "openwhisk":
            p = openwhisk.iam.policyGenerator.generateopenwhiskPolicy(package_name+"-"+func_name,resource_name,resource_type,permissions)
        if cloudName not in policies.keys():
            policies[cloudName] = []
        policies[cloudName].append(p)
    return policies

basic_severless_config = Template ("""
service: $servicename
frameworkVersion: '2'

provider:
  name: $cloudprovider
  runtime: $runtime""")


#parse the default configFile and get the basic fields
def generateBasicConfigFile(servicename,cloud,runtime):
    return basic_severless_config.substitute(servicename=servicename,cloudprovider=cloud,runtime=runtime)


        