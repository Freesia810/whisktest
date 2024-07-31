# 清理所有invoke pod
# image cache需在对应node清理 `docker image prune -f -a`

kubectl get pods -n openwhisk | grep '\-guest\-' | awk '{print $1}' | xargs kubectl delete pod -n openwhisk