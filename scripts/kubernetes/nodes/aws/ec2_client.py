import time
import boto3
import paramiko

class EC2Client:
    def __init__(self):
        pass
    def init(self, region, key_id, access_key):
        self.ec2_client = boto3.client("ec2", region_name=region, 
                                       aws_access_key_id=key_id, 
                                       aws_secret_access_key=access_key)
        self.ec2_resource = boto3.resource('ec2', region_name=region,
                                           aws_access_key_id=key_id,
                                           aws_secret_access_key=access_key)
    
    def createInstance(self, image_id, instance_type, instance_name, key_name, security_group_id, security_group_name):
        instance = self.ec2_client.run_instances(ImageId=image_id, MinCount=1, MaxCount=1, 
                                      InstanceType=instance_type, KeyName=key_name,
                                      SecurityGroupIds=[security_group_id],
                                      SecurityGroups=[security_group_name],
                                      TagSpecifications=[
                                        {
                                            'ResourceType': 'instance',
                                            'Tags': [
                                                {
                                                    'Key': 'Name',
                                                    'Value': instance_name
                                                },
                                            ]
                                        },
                                    ])
        return (instance["Instances"][0]["InstanceId"])
    
    def getInstancePublicAddress(self, instance_id):
        current_instance = list(self.ec2_resource.instances.filter(InstanceIds=[instance_id]))
        ip_address = current_instance[0].public_ip_address
        return ip_address


def ssh_connect_with_retry_with_run(ssh, ip_address, retries):
    if retries > 3:
        return False
    privkey = paramiko.RSAKey.from_private_key_file('/home/freesia/kubernetes.pem')
    interval = 5
    try:
        retries += 1
        print('SSH into the instance: {}'.format(ip_address))
        ssh.connect(hostname=ip_address, timeout=7200, username='ubuntu', pkey=privkey)
    
    except Exception as e:
        print(e)
        time.sleep(interval)
        print('Retrying SSH connection to {}'.format(ip_address))
        return ssh_connect_with_retry_with_run(ssh, ip_address, retries)

    print("connected")
    _, stdout, stderr = ssh.exec_command("pwd")
    res, _ = stdout.read(), stderr.read()
    print("test res: " + str(res))

if __name__ == "__main__":
    ec2 = EC2Client()

    ec2.init("ap-northeast-2", "", "")
    instance_id = ec2.createInstance('ami-09d3dd0451050f4b5', 't3.2xlarge', 'node-2', 'kubernetes', 'sg-015f6d7b3480b80ee', 'kubernetes')
    ip = ec2.getInstancePublicAddress(instance_id)
    print(ip)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_connect_with_retry_with_run(ssh, ip, 2)