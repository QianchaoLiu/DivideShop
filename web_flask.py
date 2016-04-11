# encoding=utf-8
from flask import Flask,url_for,render_template,request,redirect
import numpy_init

author = 'liuqianchao'
app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def mainpage(flag = True):
    if request.method == 'POST':
        list = request.form
        inpt = list['routedis']
        total_delay = numpy_init.init([int(i) for i in inpt.split(',')])
        return render_template('main.html', flag=False, l=list, td=total_delay)
    else:
        return render_template('main.html', flag=True)

@app.route('/showresult')
def showresult(forms):
    print forms
    return render_template('result.html')

#with app.test_request_context():
#    print url_for('hello_world', url='0.0.0.0:8080')
#    url_for('static', filename='style.css')
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)