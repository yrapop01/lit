from sanic import Sanic
import traceback
import socketio

from back.repl_http import get_repl

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)

app.static('/', 'front/')

@sio.on('run')
async def message(sid, data):
    try:
        name = data.get('repl', sid)
        code = data['code']

        repl = await get_repl(name)
        async with repl.get_lock():
            await repl.run(code)

            out = await repl.readline()
            while out is not None:
                out['guid'] = data['guid']
                await sio.emit('out', out, room=name)
                out = await repl.readline()
    except Exception as e:
        traceback.print_exc()
        raise

if __name__ == '__main__':
    app.run()
