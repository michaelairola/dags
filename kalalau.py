# import os 
# import time
# from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.decorators import task

kalalau = DAG(
    dag_id="kalalau",
    start_date=datetime(2025, 2, 26),
    schedule_interval="55 2 * * *",
    catchup=False,
)

@task.virtualenv(
    task_id="start_ec2_instance",
    dag=kalalau,
    requirements=["boto3==1.37.0", "apache-airflow"],
    system_site_packages=True,
)
def start_ec2_instance():
    import time
    import boto3
    from airflow.models import Variable

    def start(retries=0):
        interval = 5
        try:
            retries += 1
            print("Starting ec2 instance...")
            boto3.client('ec2', 
                aws_access_key_id=Variable.get("ACCESS_TOKEN"),
                aws_secret_access_key=Variable.get("SECRET_KEY"),
                region_name="us-west-2",
            ).start_instances(InstanceIds=[
                Variable.get("EC2_INSTANCE")
            ])
            print("Instance started :)")
            return True
        except Exception as e:
            print(e)
            time.sleep(interval)
            if retries > 4:
                raise e
            return start(retries)
    return start()

@task.virtualenv(
    task_id="echo_hello",
    dag=kalalau,
    requirements=["boto3==1.37.0", "paramiko", "apache-airflow"],
    system_site_packages=True,
)
def echo_hello():
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
    return True


@task.virtualenv(
    task_id="stop_ec2_instance",
    dag=kalalau,
    requirements=["boto3==1.37.0", "apache-airflow"],
    system_site_packages=True,
    trigger_rule="all_done",
)
def stop_ec2_instance():
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
    return True


start = start_ec2_instance()
hello = echo_hello()
stop = stop_ec2_instance()

start >> hello >> stop
