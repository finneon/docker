## Create Dockerfiles for creating opensaf cluster

### Build opensaf-cluster image
cd docker/opensaf
./scripts/docker-build -m -r ~/workspace/opensaf-code

### Create cluster 2 SCs + 2 PLs
cd docker/opensaf/scripts
./start-cluster -s 4 -w ~/workspace/

### Create new node but it does not start opensafd
cd docker/opensaf/scripts
./docker-run -n pl3 -H PL-3 -w ~/workspace/

### Scale-out nodes automatically
./docker-scale-out -s <size> -w <workspace>

### Scale-in nodes
- Enter SC node
python /usr/local/lib/opensaf/scale-in-opensaf.py --hostname PL-4
- Then remove the container
docker rm -f pl4
