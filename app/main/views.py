from flask import render_template,session,redirect,url_for,current_app,abort,flash,request,make_response
from .. import db
from ..models import User,Permission,Role,Post,Follow,Comment
from ..email import send_mail
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm,CommentForm

from flask_login import login_required,current_user
from .decorators import admin_required,permission_required
from flask_sqlalchemy import get_debug_queries
@main.route('/',methods=['POST','GET'])
def index():
    form=PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post=Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    page=request.args.get('page',1,type=int)
    show_following=False
    if current_user.is_authenticated :
        show_following=bool(request.cookies.get('show_following',''))
    if show_following:
        query=current_user.following_posts       
    else:
        query=Post.query
    pagination=query.order_by(Post.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POST_PER_PAGE'],error_out=False)
    posts=pagination.items
    return render_template('index.html',form=form,posts=posts,pagination=pagination,show_following=show_following)

@main.route('/all')
@login_required
def show_all():
    resp=make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_following','',max_age=30*24*3600)
    return resp

@main.route('/following')
@login_required
def show_following():
    resp=make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_following','1',max_age=30*24*3600)
    return resp

# @main.route('/admin')
# @login_required
# @admin_required
# def for_admins_only():
#     return "For Administrator Only"

# @main.route('/moderate')
# @login_required
# @permission_required(Permission.MODERATE_COMMEMTS)
# def for_moderator_only():
#     return "For Moderator Only"

@main.route('/user/<username>')
def user(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page=request.args.get('page',1,type=int)
    pagination=user.posts.order_by(Post.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POST_PER_PAGE'],error_out=False)
    posts=pagination.items
    return render_template('user.html',user=user,posts=posts,pagination=pagination)

@main.route('/edit-profile',methods=['POST','GET'])
@login_required
def edit_profile():
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('用户信息已更新')
        return redirect(url_for('main.user',username=current_user.username))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit-profile.html',form=form)

@main.route('/edit-profile/<int:id>',methods=['POST','GET'])
@login_required
@admin_required
def edit_profile_admin(id):
    user=User.query.get_or_404(id)
    form=EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email=form.email.data
        user.username=form.username.data
        user.confirmed=form.confirmed.data
        user.role=Role.query.get(form.role.data)
        user.name=form.name.data
        user.location=form.location.data
        user.about_me=form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('用户信息已经更新')
        return redirect(url_for('main.user',username=user.username))
    form.email.data=user.email
    form.username.data=user.username
    form.confirmed.data=user.confirmed
    form.role.data=user.role_id
    form.name.data=user.name
    form.location.data=user.location
    form.about_me.data=user.about_me
    return render_template('edit-profile.html',user=user,form=form)

@main.route('/post/<int:id>',methods=['POST','GET'])
def post(id):
    form=CommentForm()
    post=Post.query.get_or_404(id)
    if form.validate_on_submit():
        comment=Comment(body=form.body.data,post=post,author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('评论发表成功')
        return redirect(url_for('main.post',id=post.id,page=-1))
    page=request.args.get('page',1,type=int)
    if page==-1:
        page=(post.comments.count()-1) / current_app.config['FLASKY_COMMENT_PER_PAGE'] + 1
    pagination=post.comments.order_by(Comment.timestamp.asc()).paginate(int(page),per_page=current_app.config['FLASKY_COMMENT_PER_PAGE'],error_out=False)
    comments=pagination.items
    return render_template('post.html',posts=[post],pagination=pagination,comments=comments,form=form)

@main.route('/edit/<int:id>',methods=['POST','GET'])
@login_required
def edit(id):
    post=Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.body=form.body.data
        db.session.add(post)
        db.session.commit()
        flash('文章已经更新')
        return redirect(url_for('main.post',id=post.id))
    form.body.data=post.body
    return render_template('edit_post.html',form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('你已经关注了该用户')
        return redirect(url_for('main.user',username=username))
    current_user.follow(user)
    flash('你成功关注了 %s'% username)
    return redirect(url_for('main.user',username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('你没有关注该用户')
        return redirect(url_for('main.user',username=username))
    current_user.unfollow(user)
    flash('你对%s取消关注'% username)
    return redirect(url_for('main.user',username=username))

@main.route('/followers/<username>')
def followers(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户')
        return redirect(url_for('main.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followers.order_by(Follow.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POST_PER_PAGE'],error_out=False)
    follows=[ {'user':item.follower,'timestamp':item.timestamp } for item in pagination.items]
    return render_template('follows.html',user=user,title='的粉丝',endpoint='main.followers',pagination=pagination,follows=follows)

@main.route('/following/<username>')
def following(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在的用户')
        return redirect(url_for('main.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.following.order_by(Follow.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POST_PER_PAGE'],error_out=False)
    follows=[ {'user':item.followed,'timestamp':item.timestamp } for item in pagination.items]
    return render_template('follows.html',user=user,title='关注的人',endpoint='main.following',pagination=pagination,follows=follows)

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMEMTS)
def moderate():
    page=request.args.get('page',1,type=int)
    pagination=Comment.query.order_by(Comment.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_COMMENT_PER_PAGE'],error_out=False)
    comments=pagination.items
    return render_template('moderate.html',comments=comments,pagination=pagination,page=page)

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMEMTS)
def moderate_disable(id):
    comment=Comment.query.get_or_404(id)
    comment.disable=True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.moderate',page=request.args.get('page',1,type=int)))

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMEMTS)
def moderate_enable(id):
    comment=Comment.query.get_or_404(id)
    comment.disable=False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.moderate',page=request.args.get('page',1,type=int)))

@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown=request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shut down..'

@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASK_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %f\nContext: %s\n'%(query.statement,query.parameters,query.duration,query.context)
                )
    return  response