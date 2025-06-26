from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/datos', methods=['POST'])
def recibir_datos():
    data = request.get_json()
    print("📥 Datos recibidos:")
    print(data)
    return jsonify({"mensaje": "Datos recibidos correctamente"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
