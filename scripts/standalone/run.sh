cd ..
pushd bin
nohup java -jar openwhisk-standalone.jar -m custom-runtime.json -c custom.conf >server.log 2>&1 &