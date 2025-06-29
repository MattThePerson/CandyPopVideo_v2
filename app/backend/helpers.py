from fastapi import WebSocket


async def aprint(ws: WebSocket|None, *args, sep=' ', end='\n'):
    text = sep.join(str(arg) for arg in args) + end
    print(text, end='')  # prevent double newline
    if ws is not None:
        await ws.send_text(text)


