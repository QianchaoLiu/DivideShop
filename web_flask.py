# encoding=utf-8
from flask import Flask,url_for,render_template,request,redirect
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import numpy_init

author = 'liuqianchao'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'liuqianchao'
bootstrap = Bootstrap(app)

class InputForm(Form):
    routenumber = StringField('Route line numbers: 20')
    routedis = StringField('Distribution of Routes: 1,1,0,0...(length is equal to route line number)', validators=[Required])
    servicetimedis = StringField('Distribution of Lambda: 12,12,12...(length is equal to route line number)')
    lambdadis =  StringField('Distribution of Service time: 30,30,30...(length is equal to route line number)')
    summit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def mainpage(flag = True):
    if request.method == 'POST':
        form = InputForm()
        inpt = form.routedis.data
        total_delay = numpy_init.init([int(i) for i in inpt.split(',')])
        return render_template('main.html', flag=False, l=form, td=total_delay)
    else:
        form = InputForm()
        return render_template('main.html', flag=True, form=form)

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