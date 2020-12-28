import subprocess
import json
import subprocess

stream = json.loads(subprocess.check_output('aws dynamodbstreams list-streams --table-name "{tablename}"'.format(tablename="catalog"),shell=True)
	.decode('utf8'))['Streams'][0]['StreamArn']
print(stream)
