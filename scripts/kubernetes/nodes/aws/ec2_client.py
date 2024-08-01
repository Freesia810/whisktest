import json
import time
import boto3
import paramiko

class EC2Client:
    def __init__(self):
        self.instances = {}

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
        id = instance["Instances"][0]["InstanceId"]
        current_instance = list(self.ec2_resource.instances.filter(InstanceIds=[id]))
        ip_address = current_instance[0].public_ip_address
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.instances[id] = (ip_address, ssh)
        return id
    
    def getInstancePublicAddress(self, instance_id):
        current_instance = list(self.ec2_resource.instances.filter(InstanceIds=[instance_id]))
        ip_address = current_instance[0].public_ip_address
        return ip_address

    def connectInstance(self, instance_id, pem_path, retries=3):
        if retries < 0:
            return False
        interval = 5
        ip, ssh = self.instances[instance_id]
        try:
            print('SSH into the instance: {}'.format(ip))
            ssh.connect(hostname=ip, timeout=7200, username='ubuntu', pkey=paramiko.RSAKey.from_private_key_file(pem_path))
            return True
        except Exception as e:
            retries = retries - 1
            print(e)
            time.sleep(interval)
            print('Retrying SSH connection to {}'.format(ip))
            return self.connectInstance(instance_id, pem_path, retries)
    
    def executeCommand(self, instance_id, cmd):
        _, ssh = self.instances[instance_id]
        _, stdout, _ = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))

def k8s_add_node():
    ec2 = EC2Client()
    with open("aws.json") as f:
        config = json.load(f)
        ec2.init("ap-northeast-2", config['key_id'], config['access_key'])
        instance_id = ec2.createInstance('ami-09d3dd0451050f4b5', 't3.2xlarge', 'node-2', 'kubernetes', 'sg-015f6d7b3480b80ee', 'kubernetes')
        ec2.connectInstance(instance_id, '/home/freesia/kubernetes.pem')
        ec2.executeCommand(instance_id, config['command'])

if __name__ == "__main__":
    k8s_add_node()