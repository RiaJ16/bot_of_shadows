import time

from halliwell import Halliwell
from bot_of_shadows import BotOfShadows

bot_of_shadows = BotOfShadows("config.cfg")
halliwell = Halliwell("config.cfg")


def make_reply(msg, nombre_, telegram_id_, tipo_):
    respuesta = None
    if msg is not None:
        respuesta = halliwell.procesar_mensaje(
            msg, nombre_, telegram_id_, tipo_)
    return respuesta


update_id = None
while True:
    updates = bot_of_shadows.get_updates(offset=update_id)
    try:
        updates = updates["result"]
        if updates:
            for item in updates:
                update_id = item["update_id"]
                try:
                    message = str(item["message"]["text"])
                except (KeyError, IndexError):
                    message = None
                try:
                    topic = str(item["message"]["message_thread_id"])
                except (KeyError, IndexError):
                    topic = None
                if message:
                    tipo = item["message"]["chat"]["type"]
                    from_ = item["message"]["chat"]["id"]
                    nombre = item["message"]["from"]["first_name"]
                    telegram_id = item["message"]["from"]["id"]
                    reply = make_reply(message, nombre, telegram_id, tipo)
                    bot_of_shadows.send_message(reply, from_, topic)
        time.sleep(0.5)
    except KeyError:
        pass
