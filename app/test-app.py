from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>App Working! DB: dbcont</h1><img src="/static/images/VS_Logo1.jpg">'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
