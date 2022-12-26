from flask import Flask, render_template, redirect
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('_navbar_test1.html')

@app.route('/aaa')
def index1():
    return "牛逼"

@app.route('/bbb')
def index2():
    return "是真牛逼啊！！"

@app.route('/ddd/<int:a>')
def index3(a):
    return f'平方和为:{a*a}!'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
