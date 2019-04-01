import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import json
import datetime
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    return render_template('auth/login.html')
