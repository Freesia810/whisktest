declare -A nodes

nodes["ubuntu@127.0.0.1"]="C:\eurosys.pem"

for node in ${!nodes[@]}
do
    ssh -i ${nodes[$key]} $node "docker image prune -f -a"
done