pushd ../../../openwhisk-deploy-kube
cp ../config/runtimes.json helm/openwhisk/runtimes.json
cp ../config/whisk.conf helm/openwhisk/whiskconfig.conf
cp ../config/mycluster.yaml .
helm install owdev ./helm/openwhisk -n openwhisk --create-namespace -f mycluster.yaml
popd