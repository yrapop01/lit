class Events:
    # REPL to USER EVENTS
    INP = 'inp'
    OUT = 'out'
    ERR = 'err'
    HTML = 'html'
    DONE = 'done'
    EXC = 'exc'

    # USER to REPL EVENTS
    WRT = 'wrt'
    RUN = 'run'

def encode(event, data=''):
    return event + ' ' + data.replace('\n', '\\n')

def decode(message):
    msg = message.split(' ', 1)
    if len(msg) == 1:
        return msg[0].rstrip(), ''
    event, data = msg
    return event, data.replace('\\n', '\n')
