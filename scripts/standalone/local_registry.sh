registry_host=127.0.0.1:5000

declare -A images

images["python-runtime:latest"]="action-python-v3.10"
images["nodejs-runtime:latest"]="action-nodejs-v20"
images["java-runtime:latest"]="openwhisk/java8action"


# for key in ${!images[@]}
# do
#     docker pull ${images[$key]}
# done


# docker run -itd -v /data/registry:/var/lib/registry -p 5000:5000 --restart=always --name registry registry:latest

echo { \
  "insecure-registries": ["$registry_host"], \
} \
| /home/freesia/whisktest/daemon.json

sudo systemctl restart docker

sleep 3

# for key in ${!images[@]}
# do
#     docker tag ${images[$key]} $registry_host/$key
#     docker push $registry_host/$key
#     docker rmi ${images[$key]}
#     docker rmi $registry_host/$key
# done