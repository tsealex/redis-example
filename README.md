# redis-example
## Docker Compose
Start the Redis cluster with:
```
# Start the Redis containers
docker compose up -d
# Once all containers are up, initialize the Redis cluster
docker compose exec redis-1 \
  sh -c "yes yes | redis-cli --cluster create \
    redis-1:7001 redis-2:7002 redis-3:7003 \
    redis-4:7004 redis-5:7005 redis-6:7006 \
    --cluster-replicas 1"
```
Run `python main.py` to start the Redis workload that continuously reads from and writes to the key `{foo}`. While it's running, in another terminal, you can trigger a failover in the Redis cluster (e.g. restart, down-scaling) by running:
```
# Get the node that hosts the key {foo}
docker compose exec redis-1 redis-cli -p 7001 get {foo}:list

# Replace the following redis-3/4 with the actual master/replica nodes
# for the key {foo}. The failover command needs to be run on the 
# replica node.

# Initiate a failover in the replica redis-4 to promote it to master
# Then restart the old master redis-3
docker compose exec redis-4 redis-cli -p 7004 cluster failover && \
    docker compose restart -t 60 redis-3
# Reverse the failover: promote redis-3 back to master
docker compose exec redis-3 redis-cli -p 7003 cluster failover && \
    docker compose restart -t 60 redis-4
```
Kill the Python workload and shut down the Redis cluster with:
```
docker compose down -v
```
### Output
This is the output from `main.py` during a failover:
```
Get ('{foo}:list', '17') 2025-08-17 12:07:08.999962
Push 18 2025-08-17 12:07:09.000367
Get ('{foo}:list', '18') 2025-08-17 12:07:11.008986
Push 19 2025-08-17 12:07:11.009393
<<<------------ during blpop(), failover is triggered
Caught ResponseError: UNBLOCKED force unblock from blocking operation, instance state changed (master -> replica?)
<<<------------- failover complete
Get ('{foo}:list', '19') 2025-08-17 12:07:13.014259
Push 20 2025-08-17 12:07:13.014428
```