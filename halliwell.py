import requests

from bot_of_shadows import BotOfShadows


class Halliwell:

    def __init__(self, config):
        self.base_url = BotOfShadows.read_token_from_config_file(config, 'url')

    def tirar(self, tirada, telegram_id):
        personaje = False
        url_tirada = self.base_url + 'tirar/'
        sesion = requests.session()
        datos = {
                'tirada': tirada,
                'id_personaje': 1,
                'format': 'json',
                'telegram_id': telegram_id
                 }
        try:
            r = sesion.post(url_tirada, data=datos)
            diccionario = r.json()
            base = self.procesar_tipo(diccionario['base'], diccionario['tipo'])
            if tirada:
                resultado = self.procesar_tipo(diccionario['resultado'], diccionario['tipo'])
                respuesta = f"{base}" \
                            f"{diccionario['resultado_string']}" \
                            f" = <b>{resultado}</b>"
                respuesta = respuesta.replace('+', '%2b')
                personaje = diccionario['personaje']
            else:
                respuesta = f"<b>{base}</b>"
        except requests.exceptions.ConnectionError:
            respuesta = ''
        return respuesta, personaje

    def asignar_personaje(self, personaje, telegram_id, nombre):
        url_asignar = self.base_url + 'asignarpersonaje/'
        sesion = requests.session()
        datos = {
                'personaje': personaje,
                'telegram_id': telegram_id,
                'username': nombre,
                'format': 'json'
                 }
        try:
            r = sesion.post(url_asignar, data=datos)
            respuesta = r.json()
            if respuesta['exito']:
                return f"Personaje <b>{personaje}</b> asignado con éxito al usuario"
            else:
                return "Ocurrió un error,"
        except requests.exceptions.ConnectionError:
            return ''

    def personaje_asignado(self, telegram_id):
        url_asignado = self.base_url + 'personaje_asignado/'
        sesion = requests.session()
        datos = {
                'telegram_id': telegram_id,
                'format': 'json'
                 }
        try:
            r = sesion.post(url_asignado, data=datos)
            respuesta = r.json()
            personaje = respuesta['personaje']
            if personaje:
                return f"<b>{personaje}</b> es el personaje asignado al usuario"
            else:
                return "Ocurrió un error,"
        except requests.exceptions.ConnectionError:
            return ''

    @staticmethod
    def procesar_tipo(base, tipo):
        if tipo == 1:
            base = f"<u>{base}</u>"
        elif tipo == 2:
            base = f"<i>{base}</i>"
        return base

    def procesar_mensaje(self, mensaje, nombre, telegram_id, tipo):
        respuesta = None
        if len(mensaje) > 0:
            first_char = mensaje[0]
            if first_char == '/':
                comando = mensaje.split()[0][1:].split('@rpg_sheet_bot')[0].lower()
                respuesta = "Utiliza el comando /tirar para realizar una tirada."
                if comando == 'tirar':
                    try:
                        respuesta = self.tirar(mensaje.split()[1], telegram_id)
                        respuesta = self.estilizar(respuesta, nombre, tipo)
                    except IndexError:
                        respuesta = self.tirar('', telegram_id)
                        respuesta = self.estilizar(respuesta, nombre, tipo)
                elif comando == 'personaje':
                    try:
                        respuesta = self.asignar_personaje(
                            mensaje.split()[1], telegram_id, nombre)
                    except IndexError:
                        respuesta = self.personaje_asignado(telegram_id)
                    finally:
                        respuesta = f"{respuesta} <b>{nombre}</b>."
                elif comando == 'hola':
                    respuesta = f"Hola, {nombre}, no he aprendido una respuesta personalizada para ti"
                    if telegram_id == 90783987:
                        respuesta = f"Hola, amo y creador Jair"
                    elif telegram_id == 38114961:
                        respuesta = f"Hola, master corrupto Erik"
                    elif telegram_id == 101807242:
                        respuesta = f"Hola a ti, Venenosa :)"
                elif comando == 'ayuda':
                    respuesta = "Hola, estás accediendo a la ayuda de este bot."
        return respuesta

    @staticmethod
    def estilizar(respuesta, nombre, tipo, simple=False):
        reply, personaje = respuesta
        if not simple:
            if tipo == 'group' or tipo == 'public':
                indicacion = f"<pre>Resultado de la tirada de {nombre}"
                if personaje:
                    indicacion = f"{indicacion} ({personaje})"
                reply = f"{indicacion}:</pre>\n{reply}"
            elif tipo == 'private':
                if personaje:
                    reply = f"<pre>Resultado de la tirada de {personaje}:</pre>\n{reply}"
        return reply
