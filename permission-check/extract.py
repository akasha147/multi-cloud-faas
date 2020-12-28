import os
from string import Template
import subprocess
import time
import json

code_template = Template("""
import boto3
from botocore.exceptions import ClientError
def handler(event,context):
	client = boto3.client('$service')
	try:
		response = client.$functioncall
		return { 'response' : 'NO' }
	except ClientError as e:
		return { 'response' : e.response['Error']['Code']}

""")

iam_policy_template = Template("""{ "Version" : "2012-10-17" , "Statement" : [ { "Sid" : "$statement_id" , "Effect" : "Allow" , "Action" : [$permission_list] , "Resource" : "*" } ] }""")



s3_permission_list = ["s3:DeleteAccessPoint",
                "s3:DeleteJobTagging",
                "s3:PutLifecycleConfiguration",
                "s3:PutObjectTagging",
                "s3:DeleteObject",
                "s3:PutAccountPublicAccessBlock",
                "s3:GetBucketWebsite",
                "s3:DeleteStorageLensConfigurationTagging",
                "s3:PutReplicationConfiguration",
                "s3:DeleteObjectVersionTagging",
                "s3:GetObjectLegalHold",
                "s3:GetBucketNotification",
                "s3:DeleteBucketPolicy",
                "s3:GetReplicationConfiguration",
                "s3:PutObject",
                "s3:PutBucketNotification",
                "s3:PutObjectVersionAcl",
                "s3:CreateJob",
                "s3:PutBucketObjectLockConfiguration",
                "s3:PutAccessPointPolicy",
                "s3:GetStorageLensDashboard",
                "s3:GetLifecycleConfiguration",
                "s3:GetBucketTagging",
                "s3:GetInventoryConfiguration",
                "s3:ReplicateTags",
                "s3:ListBucket",
                "s3:AbortMultipartUpload",
                "s3:PutBucketTagging",
                "s3:UpdateJobPriority",
                "s3:DeleteBucket",
                "s3:PutBucketVersioning",
                "s3:ListBucketMultipartUploads",
                "s3:PutMetricsConfiguration",
                "s3:PutStorageLensConfigurationTagging",
                "s3:PutObjectVersionTagging",
                "s3:GetBucketVersioning",
                "s3:PutInventoryConfiguration",
                "s3:ObjectOwnerOverrideToBucketOwner",
                "s3:GetStorageLensConfiguration",
                "s3:DeleteStorageLensConfiguration",
                "s3:GetAccountPublicAccessBlock",
                "s3:PutBucketWebsite",
                "s3:ListAllMyBuckets",
                "s3:PutBucketRequestPayment",
                "s3:PutObjectRetention",
                "s3:GetBucketCORS",
                "s3:DeleteAccessPointPolicy",
                "s3:GetObjectVersion",
                "s3:PutAnalyticsConfiguration",
                "s3:GetObjectVersionTagging",
                "s3:PutStorageLensConfiguration",
                "s3:CreateBucket",
                "s3:GetStorageLensConfigurationTagging",
                "s3:ReplicateObject",
                "s3:GetObjectAcl",
                "s3:GetBucketObjectLockConfiguration",
                "s3:DeleteBucketWebsite",
                "s3:GetObjectVersionAcl",
                "s3:PutBucketAcl",
                "s3:DeleteObjectTagging",
                "s3:GetBucketPolicyStatus",
                "s3:GetObjectRetention",
                "s3:GetJobTagging",
                "s3:ListJobs",
                "s3:PutObjectLegalHold",
                "s3:PutBucketCORS",
                "s3:ListMultipartUploadParts",
                "s3:GetObject",
                "s3:DescribeJob",
                "s3:PutBucketLogging",
                "s3:GetAnalyticsConfiguration",
                "s3:GetObjectVersionForReplication",
                "s3:CreateAccessPoint",
                "s3:GetAccessPoint",
                "s3:PutAccelerateConfiguration",
                "s3:DeleteObjectVersion",
                "s3:GetBucketLogging",
                "s3:ListBucketVersions",
                "s3:RestoreObject",
                "s3:GetAccelerateConfiguration",
                "s3:GetBucketPolicy",
                "s3:PutEncryptionConfiguration",
                "s3:GetEncryptionConfiguration",
                "s3:GetObjectVersionTorrent",
                "s3:DeleteBucketOwnershipControls",
                "s3:GetBucketRequestPayment",
                "s3:GetAccessPointPolicyStatus",
                "s3:GetObjectTagging",
                "s3:GetBucketOwnershipControls",
                "s3:GetMetricsConfiguration",
                "s3:PutObjectAcl",
                "s3:GetBucketPublicAccessBlock",
                "s3:PutBucketPublicAccessBlock",
                "s3:ListAccessPoints",
                "s3:PutBucketOwnershipControls",
                "s3:PutJobTagging",
                "s3:UpdateJobStatus",
                "s3:GetBucketAcl",
                "s3:BypassGovernanceRetention",
                "s3:ListStorageLensConfigurations", 
                "s3:GetObjectTorrent",
                "s3:PutBucketPolicy",
                "s3:GetBucketLocation",
                "s3:GetAccessPointPolicy",
                "s3:ReplicateDelete"]

dynamodb_permission_list = [ 
                "dynamodb:DescribeContributorInsights",
                "dynamodb:RestoreTableToPointInTime",
                "dynamodb:UpdateGlobalTable",
                "dynamodb:DeleteTable",
                "dynamodb:UpdateTableReplicaAutoScaling",
                "dynamodb:DescribeTable",
                "dynamodb:PartiQLInsert",
                "dynamodb:GetItem",
                "dynamodb:DescribeContinuousBackups",
                "dynamodb:DescribeExport",
                "dynamodb:EnableKinesisStreamingDestination",
                "dynamodb:BatchGetItem",
                "dynamodb:DisableKinesisStreamingDestination",
                "dynamodb:UpdateTimeToLive",
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:PartiQLUpdate",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
                "dynamodb:UpdateGlobalTableSettings",
                "dynamodb:CreateTable",
                "dynamodb:GetShardIterator",
                "dynamodb:DescribeReservedCapacity",
                "dynamodb:ExportTableToPointInTime",
                "dynamodb:DescribeBackup",
                "dynamodb:UpdateTable",
                "dynamodb:GetRecords",
                "dynamodb:DescribeTableReplicaAutoScaling",
                "dynamodb:ListTables",
                "dynamodb:DeleteItem",
                "dynamodb:PurchaseReservedCapacityOfferings",
                "dynamodb:CreateTableReplica",
                "dynamodb:ListTagsOfResource",
                "dynamodb:UpdateContributorInsights",
                "dynamodb:CreateBackup",
                "dynamodb:UpdateContinuousBackups",
                "dynamodb:DescribeReservedCapacityOfferings",
                "dynamodb:TagResource",
                "dynamodb:PartiQLSelect",
                "dynamodb:CreateGlobalTable",
                "dynamodb:DescribeKinesisStreamingDestination",
                "dynamodb:DescribeLimits",
                "dynamodb:ListExports",
                "dynamodb:UntagResource",
                "dynamodb:ConditionCheckItem",
                "dynamodb:ListBackups",
                "dynamodb:Query",
                "dynamodb:DescribeStream",
                "dynamodb:DeleteTableReplica",
                "dynamodb:DescribeTimeToLive",
                "dynamodb:ListStreams",
                "dynamodb:ListContributorInsights",
                "dynamodb:DescribeGlobalTableSettings",
                "dynamodb:ListGlobalTables",
                "dynamodb:DescribeGlobalTable",
                "dynamodb:RestoreTableFromBackup",
                "dynamodb:DeleteBackup",
                "dynamodb:PartiQLDelete"
            ]


sns_permission_list = [
                "sns:TagResource",
                "sns:DeleteTopic",
                "sns:ListTopics",
                "sns:Unsubscribe",
                "sns:CreatePlatformEndpoint",
                "sns:SetTopicAttributes",
                "sns:UntagResource",
                "sns:OptInPhoneNumber",
                "sns:CheckIfPhoneNumberIsOptedOut",
                "sns:ListEndpointsByPlatformApplication",
                "sns:SetEndpointAttributes",
                "sns:Publish",
                "sns:DeletePlatformApplication",
                "sns:SetPlatformApplicationAttributes",
                "sns:Subscribe",
                "sns:ConfirmSubscription",
                "sns:RemovePermission",
                "sns:ListTagsForResource",
                "sns:ListSubscriptionsByTopic",
                "sns:GetTopicAttributes",
                "sns:CreatePlatformApplication",
                "sns:SetSMSAttributes",
                "sns:CreateTopic",
                "sns:GetPlatformApplicationAttributes",
                "sns:GetSubscriptionAttributes",
                "sns:ListSubscriptions",
                "sns:AddPermission",
                "sns:DeleteEndpoint",
                "sns:ListPhoneNumbersOptedOut",
                "sns:GetEndpointAttributes",
                "sns:SetSubscriptionAttributes",
                "sns:ListPlatformApplications",
                "sns:GetSMSAttributes"
    ]


s3_function_mapping = {
	
	# "copy_object" : "s3.copy_object(Bucket='bqt2',CopySource='bqt1/sample.jpg',Key='copy_sample.jpg')"
	# "download_file" : "s3.download_file(Bucket='bqt1', Key='sample.jpg', Filename='sample.jpg')"
	#"create_bucket" : "s3.create_bucket(Bucket='bqt3')"
	# "list_bucket_analytics_configurations":"s3.list_bucket_analytics_configurations(Bucket='bqt1')"
	# "list_bucket_inventory_configurations":"s3.list_bucket_inventory_configurations(Bucket='bqt1')",
	# "list_bucket_metrics_configurations":"s3.list_bucket_metrics_configurations(Bucket='bqt1')",
	# "list_buckets":"s3.list_buckets()",
	# "list_multipart_uploads":"s3.list_multipart_uploads(Bucket='bqt2')",
	# "list_object_versions":"s3.list_object_versions(Bucket='bqt2')",
	"list_objects":"s3.list_objects(Bucket='incoming-traffic')"


}


dynamodb_function_mapping = {
        "scan" : "scan(TableName ='photographers')"
}

sns_function_mapping = {
     
      "publish" : "publish(TopicArn = 'arn:aws:sns:us-east-1:779308551547:product_specification.fifo',Message = 'hello')"
}


if __name__ == '__main__':
        function_mapping = sns_function_mapping
        permission_list = sns_permission_list
        service = "sns"
        
        for function in function_mapping.keys():
            print("Function checked: "+function)
            role_name =function+"-role"

    	#Create role
            role_response = subprocess.check_output("aws iam create-role --role-name {role_name} --assume-role-policy-document file://initlambdapolicy.json".format(role_name=role_name),shell=True)
            time.sleep(10)

            #Create Function
            function_name = function
            function_code = code_template.substitute(functioncall = function_mapping[function],service=service)
            with open("run.py","w") as fp:
                    fp.write(function_code)
            os.system("zip -r function.zip run.py")
            function_response = subprocess.check_output("aws lambda create-function --function-name {function_name} --zip-file fileb://function.zip --handler run.handler --runtime python3.6 --role arn:aws:iam::779308551547:role/{role_name}".format(role_name=role_name,function_name=function_name),shell=True)
            essential_permissions = []

        for i in range(len(permission_list)):
            print("Permission checked: "+permission_list[i])			

            policy_name = function+"-"+str(i)+"-policy"
            permissions = ", ".join(['"'+permission_list[j]+'"' for j in range(len(permission_list)) if j!=i])
            iam_policy_code = iam_policy_template.substitute(permission_list=permissions,statement_id="statement"+str(i))
            with open("iam_policy.json","w") as fp:
                fp.write(iam_policy_code)
            iam_response = subprocess.check_output("aws iam put-role-policy --role-name {role_name} --policy-name {policy_name} --policy-document file://iam_policy.json".format(role_name=role_name,policy_name=policy_name),shell=True)
            time.sleep(10)

            function_invoke_response = subprocess.check_output("aws lambda invoke --function-name {function_name} response.json".format(function_name=function_name),shell=True)
            with open("response.json", 'r') as fp:
                response = json.loads(fp.read())
            print(response["response"])
            
            if response["response"] != "NO":
                print("Permission Needed")
                essential_permissions.append(permission_list[i])
            
            os.system("aws iam delete-role-policy --role-name {role_name} --policy-name {policy_name}".format(role_name=role_name,policy_name=policy_name))

        os.system("aws iam delete-role --role-name {role_name}".format(role_name=role_name))
        os.system("aws lambda delete-function --function-name {function_name}".format(function_name=function_name))
        print(essential_permissions)
        with open("permissions.csv","a+") as fp:
            fp.write(function_name+","+",".join(essential_permissions)+"\n")
			
		
