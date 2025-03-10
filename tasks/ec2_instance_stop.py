from airflow.models import Variable
import boto3
print("Stopping ec2 instance...")
boto3.client('ec2', 
    aws_access_key_id=Variable.get("ACCESS_TOKEN"),
    aws_secret_access_key=Variable.get("SECRET_KEY"),
    region_name="us-west-2",
).stop_instances(InstanceIds=[
    Variable.get("EC2_INSTANCE")
])
print("Instance stopped")
