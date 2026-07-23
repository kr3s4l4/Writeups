from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    print('📩 Datos recibidos:')
    print('Método:', request.method)
    print('Body:', request.data.decode('utf-8'))
    print('---')
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4444)
