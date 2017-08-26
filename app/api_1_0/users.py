from flask import g,jsonify,request,url_for,current_app
from . import api 
from .decorators import permission_required
from ..models import Comment,Post,User,Permission
from .. import db
from .errors import forbidden

@api.route('/users/<int:id>')
def get_user(id):
    user=User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user=User.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    pagination=user.posts.order_by(Post.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POST_PER_PAGE'],error_out=False)
    posts=pagination.items
    prev=None
    if pagination.has_prev:
        prev=url_for('api.get_user_posts',page=page-1,id=id,_external=True)
    next=None
    if pagination.has_next:
        next=url_for('api.get_user_posts',page=page+1,id=id,_external=True)
    
    return jsonify({'posts':[post.to_json() for post in posts],
                    'prev':prev,
                    'next':next,
                    'count':pagination.total
                    })

@api.route('/users/<int:id>/following_posts/')
def get_user_following_posts(id):
    user=User.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    pagination=user.following_posts.order_by(Post.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POST_PER_PAGE'],error_out=False)
    posts=pagination.items
    prev=None
    if pagination.has_prev:
        prev=url_for('api.get_user_following_posts',page=page-1,_external=True)
    next=None
    if pagination.has_next:
        next=url_for('api.get_user_following_posts',page=page+1,_external=True)
    
    return jsonify({'posts':[post.to_json() for post in posts],
                    'prev':prev,
                    'next':next,
                    'count':pagination.total
                    })