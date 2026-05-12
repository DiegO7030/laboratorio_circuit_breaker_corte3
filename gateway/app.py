from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

TIEMPO_ESPERA = 10

fallos_backend = 0 
circuito_backend_abierto = False
ultimo_fallo_backend = None

fallos_usuarios = 0
circuito_usuarios_abierto = False
ultimo_fallo_usuarios = None


def tiempo_para_reintento(ultimo_fallo):
    if ultimo_fallo is None:
        return 0

    tiempo_transcurrido = time.time() - ultimo_fallo
    tiempo_restante = TIEMPO_ESPERA - tiempo_transcurrido

    if tiempo_restante < 0:
        return 0

    return int(tiempo_restante)


def estado_del_circuito(circuito_abierto, ultimo_fallo):
    if not circuito_abierto:
        return "CERRADO"

    if tiempo_para_reintento(ultimo_fallo) == 0:
        return "HALF_OPEN"

    return "ABIERTO"

@app.route("/")
def home():
    return "Gateway funcionando 😀🍻🎉"

@app.route("/usuarios")
def usuarios():
    global fallos_usuarios, circuito_usuarios_abierto, ultimo_fallo_usuarios

    if circuito_usuarios_abierto:
        if tiempo_para_reintento(ultimo_fallo_usuarios) > 0:
            return jsonify({"error": "Servicio de usuarios temporalmente bloqueado"}), 503

        print("Circuito de usuarios en HALF_OPEN, probando recuperación...", flush=True)

    try:
        response = requests.get("http://usuarios:5000/usuarios", timeout=2)

        fallos_usuarios = 0
        circuito_usuarios_abierto = False
        ultimo_fallo_usuarios = None # Reiniciamos el tiempo de fallo al recuperar el servicio

        return jsonify(response.json()), 200

    except:
        fallos_usuarios += 1
        ultimo_fallo_usuarios = time.time()

        print(f"Fallo número {fallos_usuarios} en usuarios", flush=True)

        if fallos_usuarios >= 3:
            circuito_usuarios_abierto = True
            print("Circuito abierto para usuarios", flush=True)

        return jsonify({"error": "Servicio de usuarios no disponible"}), 503


@app.route("/mascotas")
def mascotas():
    global fallos_backend, circuito_backend_abierto, ultimo_fallo_backend

    if circuito_backend_abierto:
        if tiempo_para_reintento(ultimo_fallo_backend) > 0:
            return jsonify({"error": "Servicio de mascotas temporalmente bloqueado"}), 503

        print("Circuito de mascotas en HALF_OPEN, probando recuperación...", flush=True)

    try:
        response = requests.get("http://backend:5000/mascotas", timeout=2)

        fallos_backend = 0
        circuito_backend_abierto = False
        ultimo_fallo_backend = None # Reiniciamos el tiempo de fallo al recuperar el servicio

        return jsonify(response.json()), 200

    except:
        fallos_backend += 1
        ultimo_fallo_backend = time.time()

        print(f"Fallo número {fallos_backend} en mascotas", flush=True) # Imprime el número de fallo actual para mascotas

        if fallos_backend >= 3:
            circuito_backend_abierto = True
            print("Circuito abierto para mascotas", flush=True)

        return jsonify({"error": "Servicio de mascotas no disponible"}), 503


def verificar_servicio(url): # Función para verificar si un servicio está disponible
    try:
        response = requests.get(url, timeout=2)

        if response.status_code == 200: 
            return "funcionando"
        else:
            return "no disponible" # Si el servicio responde pero con un error, lo consideramos no disponible

    except:
        return "no disponible" # Si el servicio no responde o hay un error de conexión, lo consideramos no disponible


@app.route("/estado-circuitos")
def estado_circuitos():
    estado_mascotas = verificar_servicio("http://backend:5000/mascotas") 
    estado_usuarios = verificar_servicio("http://usuarios:5000/usuarios") 

    return jsonify({ 
        "mascotas": {
            "servicio": estado_mascotas,
            "fallos": fallos_backend,
            "circuito": estado_del_circuito(circuito_backend_abierto, ultimo_fallo_backend),
            "reintento_en_segundos": tiempo_para_reintento(ultimo_fallo_backend)
        },
        "usuarios": {
            "servicio": estado_usuarios,
            "fallos": fallos_usuarios,
            "circuito": estado_del_circuito(circuito_usuarios_abierto, ultimo_fallo_usuarios),
            "reintento_en_segundos": tiempo_para_reintento(ultimo_fallo_usuarios)
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)















# from flask import Flask, jsonify
# import requests

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Gateway funcionando 😁🌻"

# @app.route("/usuarios")
# def usuarios():
#     try:
#         response = requests.get("http://usuarios:5000/usuarios", timeout=5)
#         return jsonify(response.json())
#     except requests.exceptions.RequestException:
#         return jsonify({"error": "Servicio de usuarios no disponible"}), 503


# @app.route("/mascotas")
# def mascotas():
#     for i in range(3):
#         try:
#             print("[GATEWAY] Llamando al backend...", flush=True)

#             response = requests.get("http://backend:5000/mascotas", timeout=5)
#             data = response.json()

#             if response.status_code != 200:
#                 print("[ERROR] Backend respondió mal", flush=True)
#                 return jsonify({"error": "Error en backend"}), response.status_code
            
#             if not data:
#                 print("[ERROR] No hay datos que mostrar", flush=True)
#                 return jsonify({"error": "No hay datos"}), 404

#             print("[GATEWAY] Backend respondió con éxito", flush=True)
#             return jsonify(data)

#         except requests.exceptions.ConnectionError:
#             print(f"[ERROR] Backend caído intento {i+1}", flush=True)

#         except requests.exceptions.Timeout:
#             print(f"[GATEWAY] Timeout intento {i+1}", flush=True)

#     return jsonify({"error": "Servicio no responde"}), 504


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)