import asyncio
from gino import Gino
import os
loop = asyncio.get_event_loop()

db = Gino()

async def run():
    await db.set_bind('postgresql://{user}:{password}@{host}:{port}/{database}'.format(
        user=os.environ['DB_USER'],
        database=os.environ['DB_NAME'],
        host=os.environ.get('DB_SERVICE', '127.0.0.1'),
        port=os.environ.get('DB_PORT', 5432),
        password=os.environ.get('DB_PASS', 'postgres')
        ),
        loop=loop)

loop.run_until_complete(run())
