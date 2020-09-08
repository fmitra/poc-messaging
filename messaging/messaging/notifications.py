from messaging.sockets import active_sockets


async def notify(user_id: str, notification: str):
    all_ws = active_sockets.get_sockets(user_id)
    if not all_ws:
        return

    # TODO Handle in multiple coroutines
    for ws in all_ws:
        await ws.send_str(notification)
