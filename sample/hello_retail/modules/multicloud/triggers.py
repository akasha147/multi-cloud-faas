class Trigger(object):
	def __init__(self, cloudName="aws",triggerType="storage",event="None"):
		self.cloudName = cloudName
		self.event = event
		self.triggerType = triggerType
        
		if self.triggerType == "storage":
			
			if self.cloudName == "aws":
				self.triggerJSON = event['Records'][0]
				self.bucketName = self.triggerJSON['s3']['bucket']['name']
				self.key = self.triggerJSON['s3']['bucket']['key']
			
			if self.cloudName == "openwhisk":
				self.triggerJSON = event
				self.bucketName = self.triggerJSON['bucket']
				self.key = self.triggerJSON['key']


	


