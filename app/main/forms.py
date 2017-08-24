from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField
from wtforms.validators import Email,Required,Length,Regexp,EqualTo
from ..models import User,Role
from flask_pagedown.fields import PageDownField
class NameForm(FlaskForm):
    name=StringField('你叫什么名字？',validators=[Required()])
    submit=SubmitField('告诉我')

class EditProfileForm(FlaskForm):
    name=StringField('真名',validators=[Length(0,64)])
    location=StringField('家庭住址',validators=[Length(0,64)])
    about_me=TextAreaField('关于我')
    submit=SubmitField('提交')

class EditProfileAdminForm(FlaskForm):
    email=StringField('邮箱',validators=[Email(),Required(),Length(1,64)])
    username=StringField('用户名',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'用户名必须以字母开头，只能包含字母、数字、点、下划线')])
    confirmed=BooleanField('邮箱确认状态')
    role=SelectField('用户角色',coerce=int)
    name=StringField('真名',validators=[Length(0,64)])
    location=StringField('家庭住址',validators=[Length(0,64)])
    about_me=TextAreaField('关于我')
    submit=SubmitField('提交')

    def __init__(self,user,*args,**kw):
        super(EditProfileAdminForm,self).__init__(*args,**kw)
        self.role.choices=[(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user=user

    def validate_email(self,field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册')

    def validate_username(self,field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用')

class PostForm(FlaskForm):
    body=PageDownField('你在想什么？',validators=[Required()])
    submit=SubmitField('提交')
    
class CommentForm(FlaskForm):
    body=StringField('评论',validators=[Required()])
    submit=SubmitField('发表评论')