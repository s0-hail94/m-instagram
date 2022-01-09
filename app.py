import sys
import logging
import autologging
import forms
import models
from flask import Flask, g, render_template, flash, redirect, url_for, abort
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = '=1bz9k8uz8*qpmau4!4p#nu%3x+nl5ks)0knr2%c$@)--jc5y%'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@autologging.logged
@login_manager.user_loader
def load_user(user_id):
    '''Check if given user_id exists'''
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@autologging.logged
@app.before_request
def before_request():
    """Connect to database before each request"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@autologging.logged
@app.after_request
def after_request(response):
    """Close database connection after each request"""
    g.db.close()
    return response


@autologging.logged
@app.route('/register', methods=('GET', 'POST'))
def register():
    '''
    Register new user to database
    parameters:
      - name: username
        in: body
        type: string
        required: true
        description: username of user that wants to register

      - name: email
        in: body
        type: string
        required: true
        description: email of user that wants to register

      - name: password
        in: body
        type: string
        required: true
        description: password of user that wants to register

      - name: password_confirmation
        in: body
        type: string
        required: true
        description: password confirmation
    '''
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Registeration has been complete", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@autologging.logged
@app.route('/login', methods=('GET', 'POST'))
def login():
    '''
    Login with given credential
    parameters:
      - name: email
        in: body
        type: string
        required: true
        description: email of user that wants to login

      - name: password
        in: body
        type: string
        required: true
        description: password of user that wants to login
    '''
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Given credential does not exist", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Logged in succesfully", "success")
                return redirect(url_for('index'))
            else:
                flash("Given credential does not exist", "error")
    return render_template('login.html', form=form)


@autologging.logged
@app.route('/logout')
@login_required
def logout():
    '''Logout from webapp'''
    logout_user()
    flash("Logged out")
    return redirect(url_for('login'))


@autologging.logged
@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    '''
    Send new post to webapp
    --
    parameters:
      - name: content
        in: body
        type: string
        required: true
        description: content that logged in user wants to post
    '''
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user.id,
                           content=form.content.data.strip())
        flash("Message Posted successfully", "success")
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@autologging.logged
@app.route('/')
def index():
    '''Webapp home page'''
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream=stream)


@autologging.logged
@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    '''
    Show posted content to user
    --
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: username that system suppose to show related posts
    '''
    template = 'stream.html'
    if username and (current_user.is_anonymous or username != current_user.username):
        try:
            user = models.User.select().where(models.User.username**username).get()
        except models.DoesNotExist:
            abort(404)
        else:
            stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'user_stream.html'
    return render_template(template, stream=stream, user=user)


@autologging.logged
@app.route('/post/<int:post_id>')
def view_post(post_id):
    '''
    Show specefic post information
    --
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: database id of post that user wants to visit
    '''
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html', stream=posts)


@autologging.logged
@app.route('/follow/<username>')
@login_required
def follow(username):
    '''
    Follow given user
    --
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: username to follow
    '''
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash("You are now following {}".format(
                to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))


@autologging.logged
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    '''
    Unfollow given user
    --
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: username to unfollow
    '''
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash("You have unfollowed {}".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))


@autologging.logged
@app.errorhandler(404)
def not_found():
    '''Return appropriate output while 404 is occured'''
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.initialize()

    print('''                    		
						_____           _                                  
		_ __ ___         \_   \_ __  ___| |_ __ _  __ _ _ __ __ _ _ __ ___  
		| '_ ` _ \ _____   / /\/ '_ \/ __| __/ _` |/ _` | '__/ _` | '_ ` _ \ 
		| | | | | |_____/\/ /_ | | | \__ \ || (_| | (_| | | | (_| | | | | | |
		|_| |_| |_|     \____/ |_| |_|___/\__\__,_|\__, |_|  \__,_|_| |_| |_|
												|___/                                          
		''')
    try:
        port = sys.argv[1]
    except IndexError:
        print('Try to run program with run.sh, or with following command after activating venv\n')
        print('Python3 app.py --port 8000')
        exit

    logging.basicConfig(level=autologging.TRACE, stream=sys.stderr,
                        format="%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s")
    print('[-] Starting the service on' + '0.0.0.0:' + port + '...')

    app.run(debug=True, host='0.0.0.0', port=port)
