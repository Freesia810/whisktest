import boto3
import paramiko
import time,shlex
import subprocess as sp
import random
import os
import sys
import shutil
import statistics
FNULL = open(os.devnull, 'w')

AMI = {
    "serverlessappimages/py_graph_pagerank": "ami-02dd88ff5c1b6d385",
    "serverlessappimages/py_video_processing": "ami-07e9ba9fa1a74ab02",
    "serverlessappimages/py_image_recognition": "ami-08363dfff36e5f314",
    "serverlessappimages/py_graph_bfs": "ami-0c2b77bcd85ddd183",
    "serverlessappimages/py_file_compression": "ami-0601a8905cf4f8b2d",
    "serverlessappimages/py_sentiment_analysis": "ami-0e5ee9edea9f47a96"
}

def start_ec2(ec2_name, app):
    ec2_client = boto3.client("ec2", region_name='us-east-1')
    instance=ec2_client.run_instances(ImageId=AMI[app], MinCount=1, MaxCount=1, 
                                      InstanceType=ec2_name, KeyName="eurosys",
                                      SecurityGroupIds=["sg-041ccbbb7e6e1b089"],
                                      SecurityGroups=["eurosys_sgroup"])
    return (instance["Instances"][0]["InstanceId"])


def terminate_ec2(e):
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(e)
    instance.terminate()


def ssh_connect_with_retry_with_run(ssh, ip_address, retries,app):
    if retries > 3:
        return False
    privkey = paramiko.RSAKey.from_private_key_file(keypath)
    interval = 5
    try:
        retries += 1
        print('SSH into the instance: {}'.format(ip_address))
        ssh.connect(hostname=ip_address, timeout=7200, username='ubuntu', pkey=privkey)
    
    except Exception as e:
        print(e)
        time.sleep(interval)
        print('Retrying SSH connection to {}'.format(ip_address))
        return ssh_connect_with_retry_with_run(ssh, ip_address, retries, app)

    print("connected")
    stdin, stdout, stderr = ssh.exec_command("pwd")
    res, err = stdout.read(), stderr.read()
    print("test res: " + str(res))

    t1=time.time()
    stdin, stdout, stderr = ssh.exec_command("docker run "+app)
    res, err = stdout.read(), stderr.read()
    print("cold exec res: " + str(res) + ", err: " + str(err))
    t2=time.time()
    stdin, stdout, stderr = ssh.exec_command("docker run "+app)
    res, err = stdout.read(), stderr.read()
    print("warm exec res: " + str(res) + ", err: " + str(err))
    t3=time.time()
    exit_status = stdout.channel.recv_exit_status()
    return t2-t1, t3-t2

def exp_with_ec2(ec2, app, instance_family, instance_id):
    current_instance = list(ec2.instances.filter(InstanceIds=[instance_id]))
    ip_address = current_instance[0].public_ip_address
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    a,b=ssh_connect_with_retry_with_run(ssh, ip_address, 2,app)
    exe_time=b
    cs_time=a-b

    print("instance family = ", instance_family)
    print("exe_time = ", exe_time)
    print("cs_time = ", cs_time)

if __name__ == "__main__":
    high_end_vm_family='c6in.4xlarge' ##
    low_end_vm_family='c6in.4xlarge' ##
    keypath='/Users/pchen/eurosys.pem' ##
    app_list = {
        "a": "serverlessappimages/py_graph_pagerank",
        "b": "serverlessappimages/py_graph_bfs",
        "c": "serverlessappimages/py_video_processing",
        "d": "serverlessappimages/py_image_recognition",
        "e": "serverlessappimages/py_sentiment_analysis",
        "f": "serverlessappimages/py_file_compression"
    }
    app = app_list["f"] ##
    high_end_server_instance_id = start_ec2(high_end_vm_family, app)
    low_end_server_instance_id = start_ec2(low_end_vm_family, app)
    
    print("app = ", app)
    print("high_end = ", high_end_vm_family)
    print("low_end = ", low_end_vm_family)

    ec2 = boto3.resource('ec2', region_name='us-east-1')
    exp_with_ec2(ec2, app, high_end_vm_family, high_end_server_instance_id)
    terminate_ec2(high_end_server_instance_id)

    exp_with_ec2(ec2, app, low_end_vm_family, low_end_server_instance_id)
    terminate_ec2(low_end_server_instance_id)
