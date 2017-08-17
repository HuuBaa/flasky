from flask import render_template,session,redirect,url_for,current_app
from .. import db
from ..models import User,Permission
from ..email import send_mail
from . import main
from .forms import NameForm

from flask_login import login_required
from .decorators import admin_required,permission_required

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For Administrator Only"

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMEMTS)
def for_moderator_only():
    return "For Moderator Only"

