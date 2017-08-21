from flask import redirect,url_for,render_template,request,flash,current_app
from ..models import User
from .. import db
from . import auth
from .forms import LoginForm,RegisterForm,CPasswdForm,RPasswordForm,RPasswordForm2,CEmailForm
from flask_login import login_user,logout_user,login_required,current_user
from ..email import send_mail 
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@auth.before_app_request
def before_request():
    if current_user.is_authenticated :
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

# @auth.after_app_request
# def teardown_request(response):
#     if current_user.is_authenticated:
#         current_user.ping()
#     return response

@auth.route('/auth/login',methods=['POST','GET'])
def login():
    form=LoginForm()
    if current_user.is_authenticated:
        flash('您已经登录')
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的密码或邮箱！')
    return render_template('auth/login.html',form=form)

@auth.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('你已经退出登录！')
    return redirect(url_for('main.index'))

@auth.route('/auth/register',methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token=user.generate_token()
        send_mail(user.email,'验证邮箱','auth/email/confirm',token=token,user=user)
        flash('已经向您的邮箱发送了验证邮件！')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

@auth.route('/auth/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('邮箱验证成功！感谢！')        
    else:
        flash('邮箱验证链接无效或已经过期！')
    return redirect(url_for('main.index'))



@auth.route('/auth/unconfirmed')
@login_required
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/auth/confirm')
@login_required
def resend_email():
    token=current_user.generate_token()
    send_mail(current_user.email,'验证邮箱','auth/email/confirm',token=token,user=current_user)
    flash('邮件重新发送验证邮件！请查看邮箱')
    return redirect(url_for('main.index'))

@auth.route('/auth/cpasswd',methods=['POST','GET'])
@login_required
def cpasswd():
    form=CPasswdForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.oldpasswd.data):
            current_user.password=form.newpasswd.data
            db.session.add(current_user)
            db.session.commit()
            logout_user() 
            flash('修改密码成功，请重新登录')
            return redirect(url_for('auth.login'))
        else:
            flash('旧密码错误')
    return render_template('auth/cpasswd.html',form=form)

@auth.route('/auth/rpasswd',methods=['POST','GET'])
def rpasswd():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=RPasswordForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            token=user.generate_token()
            send_mail(form.email.data,'重设密码','auth/email/rpasswd',token=token)
            flash('邮件向你的邮箱发送一封重设密码的邮件！')
            return redirect(url_for('auth.login'))
        else:
            flash('邮箱错误')       
    return  render_template('auth/rpasswd.html',form=form)

@auth.route('/auth/rpasswd/<token>',methods=['POST','GET'])
def reset_passwd(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=RPasswordForm2()   
    if form.validate_on_submit():
        email=form.email.data
        user=User.query.filter_by(email=email).first()
        if user is None:
            flash('重设密码失败，链接无效、过期，或者邮箱错误。')
            return redirect(url_for('auth.login'))            
        if user.reset_passwd(token,form.password.data):
            flash('密码重设成功,请重新登录！')
        else:
            flash('重设密码失败，链接无效、过期，或者邮箱错误！')
        return redirect(url_for('auth.login'))   
    flash('请重设密码')     
    return render_template('auth/rpasswd2.html',form=form)   

@auth.route('/auth/remail',methods=['POST','GET'])
@login_required
def remail():
    form=CEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            token=current_user.generate_remail_token(form.newemail.data)
            send_mail(form.newemail.data,'修改邮箱确认','auth/email/remail',token=token,user=current_user)
            flash('已经向您的新邮箱发送一封验证邮件')
            return redirect(url_for('main.index'))
        else:
            flash('验证密码失败')        
    return render_template('auth/remail.html',form=form)

@auth.route('/auth/remail/<token>')
@login_required
def reset_email(token):
    if current_user.reset_email(token):
        logout_user()
        flash('邮箱修改成功，请重新登录')
        return redirect(url_for('auth.login'))
    else:
        flash('邮箱验证失败')
    return redirect(url_for('main.index'))


