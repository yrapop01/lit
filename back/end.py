import json
import asyncio
import traceback
from back.shell import acquire, release

async def send(ws, code, data=''):
    if not ws:
        return
    try:
        message = json.dumps({'code': code, 'value': data})
        data = await ws.send(message)
    except Exception as e:
        traceback.print_exc()

async def recv(ws):
    try:
        data = await ws.recv()
        action, value = json.loads(data)
        return action, value
    except Exception as e:
        traceback.print_exc()
        raise

async def run_code(shell, ids, code):
    with async shell.lock:
        await send(shell.user, 'started', {'ids': ids})
        await shell.run(code)
        data = await shell.readline()

        while data is not None:
            await send(shell.user, 'out', {'ids': ids, 'data': data})
            line = await shell.readline()

async def main(ws):
    shell = None
    try:
        while True:
            action, value = await recv(ws)

            if action == 'notebook':
                shell = await acquire(value, ws)
                if shell is None:
                    await send(ws, ['error', 'the notebook is busy'])
            elif action == 'run':
                ids = value['ids']
                code = value['code']
                asyncio.ensure_future(run_code(shell, ids, code))
    except Exception as e:
        traceback.print_exc()
        raise
    finally:
        await release(shell)

if __name__ == '__main__':
    app.run()
