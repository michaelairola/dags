def start(retries=0):
    import time
    import boto3
    from airflow.models import Variable
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

start()
