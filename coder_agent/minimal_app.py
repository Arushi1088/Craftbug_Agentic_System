from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello from Azure!</h1><p>Server is working!</p>'

@app.route('/test')
def test():
    return {'status': 'ok', 'message': 'Azure deployment successful'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
