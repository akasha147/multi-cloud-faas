import boto3
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import sys
import os

class StorageHandler():
	def __init__(self, cloudName = "aws",event=None):
		self.cloudName = cloudName
		self.crn = "crn:v1:bluemix:public:cloud-object-storage:global:a/28453f44d273458db9d39547381efbbc:e8469f95-0c29-42bc-8a52-11fbb96d579c::"
		self.endpoint_url = "https://"+event["endpoint"]
		if cloudName == "aws":
			self.storage = boto3.client('s3')
		if cloudName == "openwhisk":
			self.storage =  ibm_boto3.client("s3",config=Config(signature_version="oauth"),ibm_service_instance_id=self.crn,ibm_api_key_id=os.environ['__OW_IAM_NAMESPACE_API_KEY'],endpoint_url=self.endpoint_url)
			

	def copyObject(self,Bucket,CopySource,Key):
		if self.cloudName in ["aws","openwhisk"]:
			response = self.storage.copy_object(Bucket=Bucket,CopySource=CopySource,Key=Key)
			return reponse

