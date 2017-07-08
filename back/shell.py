import asyncio
import signal
import os
from back.repl_proto import Events, encode, decode

_REPL = 'back/repl.py'

_shells = {}
_glock = asyncio.Lock()

class Shell:
    def __init__(self, name, user):
        self._proc = None
        self._user = None
        self._name = name
        self._lock = asyncio.Lock()

    async def assign(self, user, force=False):
        if self.user == user:
            return True
        if not force and not self.available:
            return False
        self._user = user
        return True

    async def start(self):
        files = dict(stdin=asyncio.subprocess.PIPE,
                     stdout=asyncio.subprocess.PIPE,
                     stderr=asyncio.subprocess.DEVNULL)
        self._proc = await asyncio.create_subprocess_exec('python3', _REPL, **files)

    def interrupt(self):
        os.kill(self._proc.pid, signal.SIGINT)

    async def stop(self):
        self._proc.write_eof()
        self._proc.interrupt()
        await self._proc.drain()
        await self._proc.wait()

    async def run(self, code):
        await self.writeline(Events.RUN, code)

    async def inp(self, code):
        await self.writeline(Events.INP, code)

    async def writeline(self, event, data=''):
        self._proc.stdin.write((encode(event, data) + '\n').encode('utf-8'))
        await self._proc.stdin.drain()

    async def readline(self):
        line = await self._proc.stdout.readline()
        if not line:
            return None
        if line.endswith(b'\n'):
            line = line[:-1]
        event, data = decode(line.decode('utf-8'))
        if event == Events.DONE:
            return None
        return {event: data}

    @property
    def name(self):
        return self._name

    @property
    def lock(self):
        return self._lock

    @property
    def user(self):
        return self._user

    @property
    def available(self):
        return self._user is None or not self._user.open

async def acquire(name, user, force=False):
    async with _glock:
        if name in _shells:
            shell = _shells[name]
            if shell.assign(user, force):
                return shell
            return None
        elif name:
            shell = _shells[name] = Shell(user)
        else:
            shell = Shell(user)

    await shell.start()
    return shell

async def release(shell, user):
    if shell is None:
        return
    if not shell.name:
        await shell.stop()
        return
    async with _glock:
        if shell.user == user:
            shell.assign(None, force=True)

async def stop(name):
    shell = _shells[name]
    async with _glock:
        del _shells[name]

    await shell.stop()
