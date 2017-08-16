# -*- coding: utf-8 -*-
from flask import Flask,redirect,url_for,render_template,session,flash
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from threading import Thread
import os
from flask_migrate import Migrate,MigrateCommand

basedir=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)
app.config['SECRET_KEY']='huu cool'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['MAIL_SERVER']='smtp.qq.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_ADMIN']=os.environ.get('FLASKY_ADMIN')
app.config['FLASK_MAIL_SUBJECT_PREFIX']='[Flasky]'
app.config['FLASK_MAIL_SENDER']='Huu Flask <742790905@qq.com>'


def send_async_mail(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to,subject,template,**kw):
    msg=Message(app.config['FLASK_MAIL_SUBJECT_PREFIX']+subject,sender=app.config['FLASK_MAIL_SENDER'],recipients=[to])
    msg.body=render_template(template+'.txt',**kw)
    msg.html=render_template(template+'.html',**kw)
    thr=Thread(target=send_async_mail,args=[app,msg])
    thr.start()
    return thr

bootstrap=Bootstrap(app)
manager=Manager(app)
db=SQLAlchemy(app)
mail=Mail(app)
migrate=Migrate(app,db)



class NameForm(FlaskForm):
    name=StringField('你叫什么名字？',validators=[Required()])
    submit=SubmitField('告诉我')

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    users=db.relationship('User',backref='role',lazy='dynamic')


    def __repr__(self):
        return '<Role %r>'%self.name

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    

    def __repr__(self):
        return '<User %r>'%self.username

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)

manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command("db",MigrateCommand)

@app.route('/',methods=['POST','GET'])
def index():
    form=NameForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.name.data).first()
        if user is None:
            user=User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known']=False
            if app.config['FLASKY_ADMIN']:
                send_mail(app.config['FLASKY_ADMIN'],'New User','mail/user_name',user=user)
        else:
            session['known']=True
        session['name']=form.name.data
        form.name.data=''
        return redirect(url_for('index'))
    return render_template('index.html',form=form,name=session.get('name'),known=session.get('known',False))

if __name__ == '__main__':
    manager.run()