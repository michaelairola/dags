import time
from tempfile import NamedTemporaryFile

import boto3
import paramiko
from airflow.models import Variable    

resources = boto3.resource('ec2', 
    aws_access_key_id=Variable.get("ACCESS_TOKEN"),
    aws_secret_access_key=Variable.get("SECRET_KEY"),
    region_name="us-west-2",                          
)
instance = resources.Instance(id=Variable.get("EC2_INSTANCE"))
print("wait until instance is running...")
instance.wait_until_running()
print("it is running!")
current_instance = list(resources.instances.filter(InstanceIds=[Variable.get("EC2_INSTANCE")]))
ip_address = current_instance[0].public_ip_address

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

interval = 5
retries = 0
is_connected = 1
while retries <= 3:
    retries += 1
    print('Attempting SSH into the instance: {}'.format(ip_address))
    try:
        file = NamedTemporaryFile()
        with open(file.name, 'w') as f:
            private_key = Variable.get("SSH_PRIVATE_KEY").replace('\\n','\n') 
            f.write(private_key)
        ssh.connect(
            hostname=ip_address,
            username='ec2-user',
            pkey=paramiko.RSAKey.from_private_key_file(file.name)
        )
        is_connected = 1
        break
    except Exception as e:
        print(type(e), e)
        time.sleep(interval)

if not is_connected:
    print("Failed to connect to the EC2 instance :(")
    return False

_, stdout, _ = ssh.exec_command("echo 'Hello World!'")
print(stdout.read())
