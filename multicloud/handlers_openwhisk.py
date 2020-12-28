# import boto3
# import uuid

import ibm_boto3
from ibm_botocore.client import Config, ClientError
from cloudant.client import Cloudant
import os


class StorageHandler():
	def __init__(self, cloudName = "aws",event=None):
		self.cloudName = cloudName
		
		# if self.cloudName =="aws":
		# 	self.storage = boto3.client('s3')

		if self.cloudName == "openwhisk":
			self.crn = "crn:v1:bluemix:public:cloud-object-storage:global:a/28453f44d273458db9d39547381efbbc:e8469f95-0c29-42bc-8a52-11fbb96d579c::"
			self.endpoint_url = "https://"+event["endpoint"]
			self.storage =  ibm_boto3.client("s3",config=Config(signature_version="oauth"),ibm_service_instance_id=self.crn,ibm_api_key_id=os.environ['__OW_IAM_NAMESPACE_API_KEY'],endpoint_url=self.endpoint_url)
			

	def copyObject(self,Bucket,CopySource,Key):
		# if self.cloudName == "aws":
		# 	response = self.storage.copy_object(Bucket=Bucket,CopySource=CopySource,Key=Key)
		
		if self.cloudName == "openwhisk":
			response = self.storage.copy_object(Bucket=Bucket,CopySource=CopySource,Key=Key)
		return response

class noSqlDatabaseHandler():
	def __init__(self,cloudName="aws",event=None):
		self.cloudName = cloudName

		# if self.cloudName == "aws":
		# 	self.db = boto3.client('dynamodb')

		if self.cloudName == "openwhisk":
			self.host = "d59c484b-77e6-4236-ae6c-e3e9c499b8ea-bluemix"
			self.key = os.environ['__OW_IAM_NAMESPACE_API_KEY']
			self.db = Cloudant.iam(self.host,self.key)


	def insert(self,TableName,Item):
		# if self.cloudName == "aws":
		# 	new_item = dict()
		# 	for k in Item.keys():
		# 		new_item[k] = {'S':Item[k]}
		# 	new_item['Id'] = {'S':str(uuid.uuid1())}
		# 	response = self.db.put_item(TableName=TableName,Item=new_item)
		
		if self.cloudName == "openwhisk":
			self.db.connect()
			response = self.db[TableName].create_document(Item)
			self.db.disconnect()

		return response

	def get_all(self,TableName):
		# if self.cloudName == "aws":
		# 	query_result = self.db.scan(TableName=TableName)
		# 	response = []
		# 	for item in query_result['Items']:
		# 		datatuple = dict()
		# 		for key in item.keys():
		# 			for type in item[key].keys():
		# 				datatuple[key]=item[key][type]
		# 		response.append(datatuple)

		if self.cloudName == "openwhisk":
			self.db.connect()
			response = []
			for document in self.db[TableName]:
				response.append(document)
			self.db.disconnect()
		
		return response
