import multicloud.handlers

class Trigger(object):
	def __init__(self, cloudName="aws",triggerType="storage",event="None"):
		self.cloudName = cloudName
		self.event = event
		self.triggerType = triggerType
        
		if self.triggerType == "storage":
			
			if self.cloudName == "aws":
				self.triggerJSON = self.event['Records'][0]
				self.bucketName = self.triggerJSON['s3']['bucket']['name']
				self.key = self.triggerJSON['s3']['object']['key']
			
			if self.cloudName == "openwhisk":
				self.triggerJSON = event
				self.bucketName = self.triggerJSON['bucket']
				self.key = self.triggerJSON['key']

		if self.triggerType == "https":
			if self.cloudName == "aws":
				self.queryParameters = self.event.get("queryStringParameter",None)
			
			if self.cloudName == "openwhisk":
				self.queryParameters = self.event

		if self.triggerType == "no-sql-database":
			if self.cloudName == "aws":
				self.eventName = self.event['Records'][0]['eventName']
				triggering_item = event['Records'][0]['dynamodb']['NewImage']
				self.item = dict()
				for key in triggering_item.keys():
					for type in triggering_item[key].keys(): 
						self.item[key] = triggering_item[key][type]
			
			if self.cloudName == "openwhisk":
				self.eventName = self.event.get('deleted',"INSERT")
				if self.eventName == "INSERT":
					self.db_handler = multicloud.handlers.noSqlDatabaseHandler(cloudName="openwhisk")
					self.db_handler.db.connect()
					self.item = self.db_handler.db[event['dbname']][event['id']]
					self.db_handler.db.disconnect()






	


