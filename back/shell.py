import asyncio
from back.repl_proto import Events, encode, decode

_REPL = 'back/repl.py'

_repls = {}
_glock = asyncio.Lock()

class Repl:
    def __init__(self, name):
        self.proc = None
        self.name = name
        self.lock = asyncio.Lock()

    async def start(self):
        files = dict(stdin=asyncio.subprocess.PIPE,
                     stdout=asyncio.subprocess.PIPE,
                     stderr=asyncio.subprocess.DEVNULL)
        self.proc = await asyncio.create_subprocess_exec('python3', _REPL, **files)

    async def stop(self):
        self.proc.write_eof()
        await self.proc.drain()
        await self.proc.wait()

    async def run(self, code):
        await self.writeline(Events.RUN, code)

    async def inp(self, code):
        await self.writeline(Events.INP, code)

    async def writeline(self, event, data=''):
        self.proc.stdin.write((encode(event, data) + '\n').encode('utf-8'))
        await self.proc.stdin.drain()

    async def readline(self):
        line = await self.proc.stdout.readline()
        if not line:
            return None
        if line.endswith(b'\n'):
            line = line[:-1]
        event, data = decode(line.decode('utf-8'))
        if event == Events.DONE:
            return None
        return {event: data}

    def get_lock(self):
        return self.lock

    def is_ready(self):
        return self.ready

async def get_repl(name):
    if name in _repls:
        return _repls[name]

    repl = Repl(name)
    await repl.start()

    async with _glock:
        if name not in _repls:
            _repls[name] = repl
            return repl

    # Someone else created a REPL before us, stop and return existing one
    await repl.stop()
    return _repls[name]
