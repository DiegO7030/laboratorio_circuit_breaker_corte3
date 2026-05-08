from flask import Flask, jsonify
import requests

app = Flask(__name__)

fallos_backend = 0
circuito_backend_abierto = False

fallos_usuarios = 0
circuito_usuarios_abierto = False


@app.route("/usuarios")
def usuarios():
    global fallos_usuarios, circuito_usuarios_abierto

    if circuito_usuarios_abierto:
        return jsonify({"error": "Servicio de usuarios temporalmente bloqueado"}), 503

    try:
        response = requests.get("http://usuarios:5000/usuarios", timeout=2)
        fallos_usuarios = 0
        return jsonify(response.json()), 200

    except:
        fallos_usuarios += 1
        print(f"Fallo número {fallos_usuarios} en usuarios", flush=True)

        if fallos_usuarios >= 3:
            circuito_usuarios_abierto = True
            print("Circuito abierto para usuarios", flush=True)

        return jsonify({"error": "Servicio de usuarios no disponible"}), 503


@app.route("/mascotas")
def mascotas():
    global fallos_backend, circuito_backend_abierto

    if circuito_backend_abierto:
        return jsonify({"error": "Servicio de mascotas temporalmente bloqueado"}), 503

    try:
        response = requests.get("http://backend:5000/mascotas", timeout=2)
        fallos_backend = 0
        return jsonify(response.json()), 200

    except:
        fallos_backend += 1
        print(f"Fallo número {fallos_backend} en mascotas", flush=True)

        if fallos_backend >= 3:
            circuito_backend_abierto = True
            print("Circuito abierto para mascotas", flush=True)

        return jsonify({"error": "Servicio de mascotas no disponible"}), 503


@app.route("/estado-circuitos")
def estado_circuitos():
    return jsonify({
        "mascotas": {
            "fallos": fallos_backend,
            "circuito_abierto": circuito_backend_abierto
        },
        "usuarios": {
            "fallos": fallos_usuarios,
            "circuito_abierto": circuito_usuarios_abierto
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