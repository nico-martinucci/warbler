import os
from dotenv import load_dotenv

from flask import (Flask, render_template, request, flash, redirect, session,
    g, jsonify)
from flask_wtf.csrf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import (UserAddForm, EditProfileForm, LoginForm,
    MessageForm, CSRFProtectForm)
from models import (db, connect_db, User, Message, Like, DEFAULT_IMAGE_URL,
    DEFAULT_HEADER_IMAGE_URL)

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///warbler"
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "secret key"

# need this for now until we can debug the csrf issue...
app.config['WTF_CSRF_ENABLED'] = False

# toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def create_csrf_only_form():
    """ Adds CSFR only form for use in all routes. """
    
    g.csrf_form = CSRFProtectForm()

# add in before_request that validates current user

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


@app.before_request
def create_message_form():
    """ Adds a message form for navbar message sending. """

    g.message_form = MessageForm()


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    # ask to logout instead?
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )

            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        flash("Sign up successfull!", 'success')
        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login and redirect to homepage on success."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.post('/logout')
def logout():
    """Handle logout of user and redirect to homepage."""

    form = g.csrf_form

    if form.validate_on_submit():
        do_logout()
        flash("You have logged out.", "success")
        return redirect("/login")

    else:
        # didn't pass CSRF; ignore logout attempt
        return redirect("/")



##############################################################################
# General user routes:

@app.get('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.get('/users/<int:user_id>')
def show_user(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    likes = [msg.id for msg in g.user.liked_messages]

    return render_template('users/show.html', user=user, likes=likes)


@app.get('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.get('/users/<int:user_id>/followers')
def show_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.get('/users/<int:user_id>/liked_messages')
def show_liked_messages(user_id):
    """ Show all liked messages for the current user. """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")


    return render_template("users/liked_messages.html",  user=g.user)


@app.post('/users/follow/<int:follow_id>')
def start_following(follow_id):
    """Add a follow for the currently-logged-in user.

    Redirect to following page for the current for the current user.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.post('/users/stop-following/<int:follow_id>')
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user.

    Redirect to following page for the current for the current user.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = EditProfileForm(obj=g.user)

    if form.validate_on_submit():
        password = form.password.data

        user = User.authenticate(
            username=g.user.username,
            password=password
        ) # the user instance if success; "False" if fail

        if user:
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or DEFAULT_IMAGE_URL
            user.header_image_url = (form.header_image_url.data or
                DEFAULT_HEADER_IMAGE_URL)
            user.bio = form.bio.data

            db.session.add(user)
            db.session.commit()

            flash("Profile updated.", "success")
            return redirect(f"/users/{user.id}")
        else:
            flash("Incorrect password.", "danger")

    return render_template("/users/edit.html", form=form)


@app.post('/users/delete')
def delete_user():
    """Delete user.

    Redirect to signup page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def add_message():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/create.html', form=form)


@app.get('/messages/<int:message_id>')
def show_message(message_id):
    """Show a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get_or_404(message_id)
    likes = [msg.id for msg in g.user.liked_messages]

    return render_template('messages/show.html', msg=msg, likes=likes)


@app.post('/messages/<int:message_id>/delete')
def delete_message(message_id):
    """Delete a message.

    Check that this message was written by the current user.
    Redirect to user page on success.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get_or_404(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")

@app.post('/api/messages/<int:message_id>/likes')
def like_unlike_message(message_id):
    """ Handle AJAX request for liking/unliking message. """

    form = g.csrf_form

    if form.validate_on_submit():
        # grab user's of current likes (list of message_ids)
        target_message = Message.query.get(message_id)
        liked_message_ids = {msg.id for msg in g.user.liked_messages} # --> this is a set; O(1) for sets!
        # see if message_id is in ^ list
        if message_id in liked_message_ids:
            # if it is, .remove() message from user's likes 
            g.user.liked_messages.remove(target_message)
        else:
            # if it is not, grab message based on message_id and .append()
            g.user.liked_messages.append(target_message)

        db.session.commit() 

        serialized = target_message.serialize()

        return (jsonify(message=serialized), 201)
    else:
        flash("Error!", "danger")
    

# add in messages id to url param instead of using the form
@app.post('/messages/likes')
def like_message():
    """Like/Dislike a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # try using WTForms to do this instead
    form = g.csrf_form

    if form.validate_on_submit():
        redirect_loc = request.form["redirect_loc"]

        # use our ORM to do this instead - .append()
        message = request.form["message_id"]
        like = Like.query.get((g.user.id, message))

        if like:
            db.session.delete(like)
            db.session.commit()
            return redirect(redirect_loc)

        else:
            new_like = Like(user_id=g.user.id, message_id=message)
            db.session.add(new_like)
            db.session.commit()
            return redirect(redirect_loc)
    else:
        return redirect(redirect_loc)



##############################################################################
# Homepage and error pages


@app.get('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        following = [user.id for user in g.user.following] + [g.user.id]

        liked_message_ids = {msg.id for msg in g.user.liked_messages} # --> this is a set; O(1) for sets!

        messages = (Message
                    .query
                    .filter(Message.user_id.in_(following))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', messages=messages, likes=liked_message_ids)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response
