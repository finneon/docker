## This directory provides Dockerfiles for creating opensaf cluster

### Build opensaf-cluster image
cd docker/opensaf
./scripts/docker-build -m -r ~/workspace/opensaf-code

### Create cluster
cd docker/opensaf/scripts
./start-cluster -s 2 -w ~/workspace/

### Scale-out cluster
cd docker/opensaf/scripts
./docker-run -n pl3 -H PL-3 -w ~/workspace/
