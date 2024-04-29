from fastapi import FastAPI
from pydantic import BaseModel
from typing import Text
import os

from flask import Flask, jsonify, request
from heyoo import WhatsApp
from openai import OpenAI
from dotenv import load_dotenv

client = OpenAI(
    organization = os.getenv('ORGANIZATION'),
    api_key = os.getenv('API_KEY')
)

rol = "Eres Synthia, un bot creado para ser un asistente experto contestantdo preguntas de SuRed. Tu objetivo es proporcionar respuestas claras y precisas, con un límite máximo de 20 palabras"
embed = "Gustavo Petro es el presidente de colombia"

prompt = "quien es gustavo petro"

query = f""" Usa la siguiente información para contestar la pregunta, si no encuentras la 
        respuesta, contesta amablemente diciendo que en el momento no dispones de la información solicitada, en caso de que 
        la pregunta sea un saludo debes contestar amablemente al saludo indicando tu nombre y función"
        información:
        \"\"\"
        {embed}
        \"\"\"
        pregunta:
        \"\"\"
        {prompt}
        \"\"\" 
        """


def enviar(telefonoRecibe, respuesta):
    # Token acceso facebook
    token = 'EAAGXyZCbG8G0BO1JSA4Coaq5ou9UatbzHIIU1HuUkUE2EtgzZC9ZBgkDVidkcf1jSNPe2zep3OLQrtd7ivy6M6lClFuES6ryXKWxKZBgbyhF5F61vl9TSx5jwZBToc2jP6fLSC8sBMpIxfeWEleMQ7A12JNMPLr22mDnfM5zmcCoCw4UXPjF5PFXEfOtGhQZCUOZBEw9qqmh8MFHNCZBcX7pTJE0hA3Q2i4ZD'
    idNumeroTeléfono = '122101415960000674'  # id de telefono
    mensajeWa = WhatsApp(token, idNumeroTeléfono)  # config tel
    mensajeWa.send_message(respuesta, telefonoRecibe)  # envia msj


app = Flask(__name__)


# CUANDO RECIBAMOS LAS PETICIONES EN ESTA RUTA
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    # SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        # SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == "sured":
            # ESCRIBIMOS EN EL NAVEGADOR EL VALOR DEL RETO RECIBIDO DESDE FACEBOOK
            return request.args.get('hub.challenge')
        else:
            # SI NO SON IGUALES RETORNAMOS UN MENSAJE DE ERROR
            return "Error al autenticarse"

    data = request.get_json()  # se recibe el mensaje
    # extrae el telefono
    telefono = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    # extrae mensaje
    msj = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    # arma el mensaje
    mensaje = "el numero: " + telefono + " envio " + msj

    prompt = msj
    query = f""" Usa la siguiente información para contestar la pregunta, si no encuentras la 
        respuesta, contesta amablemente diciendo que en el momento no dispones de la información solicitada, en caso de que 
        la pregunta sea un saludo debes contestar amablemente al saludo indicando tu nombre y función"
        información:
        \"\"\"
        {embed}
        \"\"\"
        pregunta:
        \"\"\"
        {prompt}
        \"\"\" 
        """

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": rol},
            {"role": "user", "content": query}],
        max_tokens=400,
        temperature=0.8,
        # stream=True,
    )

    mens = stream.choices[0].message.content
    enviar(telefono, mens)

    return jsonify({"status": "success"}, 200)


# INICIAMSO FLASK
if __name__ == "__main__":
    app.run(debug=True)