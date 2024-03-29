import random
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

    def roll(self, cadena, nombre):
        try:
            tiradas = cadena.split("+")
            respuesta = ''
            suma = 0
            for tirada in tiradas:
                try:
                    dados = int(tirada.split('d')[0])
                    caras = int(tirada.split('d')[1])
                    if dados > 1000 or caras > 9999:
                        raise OverflowError
                    respuesta = f"{respuesta}("
                    for dado in range(0, dados):
                        resultado = random.randint(1, caras)
                        suma += resultado
                        tipo = 0
                        if resultado == caras:
                            tipo = 1
                        elif resultado == 1:
                            tipo = 2
                        resultado = self.procesar_tipo(resultado, tipo)
                        respuesta = f"{respuesta}{resultado} + "
                    respuesta = f"{respuesta.rstrip('+ ')}) + "
                except IndexError:
                    suma += dados
                    respuesta = f"{respuesta}{dados} + "
            if len(respuesta) >= 4000:
                respuesta = ""
            respuesta = f"{respuesta.rstrip(' + ')} = <b>{suma}</b>"
            respuesta = f"<pre>Resultado de la tirada de {nombre}" \
                        f" ({cadena}):</pre>\n{respuesta}"
            respuesta = respuesta.replace('+', '%2b')
        except ValueError:
            respuesta = f"Ha ocurrido un error, <b>{nombre}</b>." \
                        f" Revisa el formato de la tirada."
        except OverflowError:
            respuesta = f"Ha ocurrido un error, <b>{nombre}</b>." \
                        f" Ingresa una tirada más realista, pl0x."
        return respuesta

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
                elif comando == 'roll':
                    try:
                        respuesta = self.roll(mensaje.split()[1], nombre)
                    except IndexError:
                        respuesta = self.roll("1d10", nombre)
                elif comando == 'hola':
                    respuesta = f"Hola, {nombre}, no he aprendido una respuesta personalizada para ti"
                    if telegram_id == 90783987:
                        respuesta = f"Hola, amo y creador Jair"
                    elif telegram_id == 38114961:
                        respuesta = f"Hola, master corrupto Erik"
                    elif telegram_id == 101807242:
                        respuesta = f"Hola a ti, Venenosa :)"
                    elif telegram_id == 73727415:
                        respuesta = f"Hola, Fai. ¡Ya eres popular! De nada."
                    elif telegram_id == 51280994:
                        respuesta = f'Hola, "Rosa" ¬¬'
                    elif telegram_id == 122654776:
                        respuesta = f"Hola, Prisca, ayudante corrupta del master corrupto"
                elif comando == 'ayuda':
                    respuesta = "Hola, estás accediendo a la ayuda de este bot."
                elif comando == 'good':
                    try:
                        if mensaje.split()[1].lower() == "bot":
                            respuesta = f"Good {nombre}."
                    except IndexError:
                        respuesta = "Good what?"
                elif comando == 'bad':
                    try:
                        if mensaje.split()[1].lower() == "bot":
                            respuesta = ":("
                    except IndexError:
                        respuesta = "Bad what?"
        return respuesta

    @staticmethod
    def estilizar(respuesta, nombre, tipo, simple=False):
        reply, personaje = respuesta
        if not simple:
            if tipo == 'group' or tipo == 'supergroup':
                indicacion = f"<pre>Resultado de la tirada de {nombre}"
                if personaje:
                    indicacion = f"{indicacion} ({personaje})"
                reply = f"{indicacion}:</pre>\n{reply}"
            elif tipo == 'private':
                if personaje:
                    reply = f"<pre>Resultado de la tirada de {personaje}:</pre>\n{reply}"
        return reply
