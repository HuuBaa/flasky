from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField,PasswordField
from wtforms.validators import Email,Required,Length,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
   email=StringField('邮箱',validators=[Required(),Email(),Length(1,64)])
   password=PasswordField('密码',validators=[Required()])
   remember_me=BooleanField('记住我')
   submit=SubmitField('登录')

class RegisterForm(FlaskForm):
    email=StringField('邮箱',validators=[Email(),Required(),Length(1,64)])
    username=StringField('用户名',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'用户名必须以字母开头，只能包含字母、数字、点、下划线')])
    password=PasswordField('密码',validators=[Required(),EqualTo('password2',message='两次输入密码不一致')])
    password2=PasswordField('确认密码',validators=[Required()])
    submit=SubmitField('注册')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经注册')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用')

class CPasswdForm(FlaskForm):
    oldpasswd=PasswordField('旧密码',validators=[Required()])
    newpasswd=PasswordField('新密码',validators=[Required(),EqualTo('newpasswd2',message='两次输入密码不一致')])
    newpasswd2=PasswordField('重新输入新密码',validators=[Required()])
    submit=SubmitField('修改密码')

class RPasswordForm(FlaskForm):
    email=StringField('账号邮箱',validators=[Required(),Email()])
    submit=SubmitField('重设密码')

class RPasswordForm2(FlaskForm):
    email=StringField('邮箱',validators=[Email(),Required(),Length(1,64)])
    password=PasswordField('密码',validators=[Required(),EqualTo('password2',message='两次输入密码不一致')])
    password2=PasswordField('重新输入新密码',validators=[Required()])
    submit=SubmitField('重设密码')

class CEmailForm(FlaskForm):
    newemail=StringField('填入新邮箱',validators=[Required(),Email()])
    password=PasswordField('进行邮箱的修改需要验证账号的密码',validators=[Required()])
    submit=SubmitField('修改邮箱')