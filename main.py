import asyncio
from datetime import datetime

from redis.asyncio import RedisCluster
from redis.exceptions import ResponseError


async def main():
    r = RedisCluster(
        host='localhost',
        port=7001,
        # This is needed if you're using Docker or similar because the cluster
        # nodes would advertise their internal Docker IPs which are not reachable
        # from the host machine. (host, port) -> (remapped_host, remapped_port)
        address_remap=lambda host_port: ('localhost', host_port[1]),
        decode_responses=True,
        # You need these to reduce reconnection/retry timeouts
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
        cluster_error_retry_attempts=30,
    )

    async def lpush():
        i = 0
        while True:
            async with r.pipeline() as pipe:
                pipe.set('foo', i)
                pipe.lpush('{foo}:list', i)
                await pipe.execute()
                i += 1
            print('Push', i, datetime.now())
            await asyncio.sleep(2)

    asyncio.create_task(lpush())

    while True:
        # await asyncio.sleep(0.5)
        try:
            print('Get', await r.blpop(['{foo}:list']), datetime.now())
        except ResponseError as e:
            print('Caught ResponseError:', e)
            pass  # Retry happens inside redis-py


if __name__ == '__main__':
    asyncio.run(main())
