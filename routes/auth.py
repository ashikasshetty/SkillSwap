import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import db, User, SkillOffered, SkillWanted, Review, SwapRequest

auth_bp = Blueprint('auth', __name__)

def login_required(view):
    """View decorator ensuring user is authenticated."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    """View decorator ensuring current user is an administrator."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in as an administrator.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('Access restricted to administrators only.', 'danger')
            return redirect(url_for('main.index'))
        return view(**kwargs)
    return wrapped_view

@auth_bp.before_app_request
def load_logged_in_user():
    """Load logged-in user into flask global `g.user` if session exists."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)
        if g.user and not g.user.is_active:
            session.clear()
            g.user = None
            flash('Your account has been deactivated. Please contact administrator.', 'danger')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('main.explore'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        bio = request.form.get('bio', '').strip()
        location = request.form.get('location', 'St Agnes College, Mangaluru').strip()
        avatar = request.form.get('avatar', 'default_avatar.png')

        if not full_name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Create user
        new_user = User(
            full_name=full_name,
            email=email,
            bio=bio,
            location=location,
            avatar=avatar,
            role='user'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Log user in
        session['user_id'] = new_user.id
        session['user_name'] = new_user.full_name
        session['user_role'] = new_user.role
        session['user_email'] = new_user.email

        flash(f'Welcome to SkillSwap, {new_user.full_name}! Let us add skills you can teach and skills you want to learn.', 'success')
        return redirect(url_for('skills.manage_skills'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('main.explore'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('login.html')

            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            session['user_role'] = user.role
            session['user_email'] = user.email

            flash(f'Welcome back, {user.full_name}!', 'success')
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('main.explore'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        g.user.full_name = request.form.get('full_name', g.user.full_name).strip()
        g.user.bio = request.form.get('bio', '').strip()
        g.user.location = request.form.get('location', '').strip()
        g.user.avatar = request.form.get('avatar', g.user.avatar)
        
        # Password update if requested
        new_password = request.form.get('new_password', '').strip()
        if new_password:
            g.user.set_password(new_password)
            flash('Password updated successfully.', 'success')

        db.session.commit()
        session['user_name'] = g.user.full_name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    # Load statistics
    my_offered = g.user.skills_offered.all()
    my_wanted = g.user.skills_wanted.all()
    reviews = g.user.reviews_received.order_by(Review.created_at.desc()).all()
    
    return render_template('profile.html', offered=my_offered, wanted=my_wanted, reviews=reviews)

@auth_bp.route('/user/<int:user_id>')
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    offered = user.skills_offered.all()
    wanted = user.skills_wanted.all()
    reviews = user.reviews_received.order_by(Review.created_at.desc()).all()
    
    # Calculate if logged in user has mutual matches with this person
    mutual_skills = []
    user_can_teach_viewer = []
    viewer_can_teach_user = []
    
    if g.user and g.user.id != user.id:
        my_offered_names = {s.skill_name.lower(): s for s in g.user.skills_offered.all()}
        my_wanted_names = {s.skill_name.lower(): s for s in g.user.skills_wanted.all()}
        
        their_offered_names = {s.skill_name.lower(): s for s in offered}
        their_wanted_names = {s.skill_name.lower(): s for s in wanted}

        for s_name in their_offered_names:
            if s_name in my_wanted_names:
                user_can_teach_viewer.append(their_offered_names[s_name])

        for s_name in my_offered_names:
            if s_name in their_wanted_names:
                viewer_can_teach_user.append(my_offered_names[s_name])
                
        is_mutual_match = len(user_can_teach_viewer) > 0 and len(viewer_can_teach_user) > 0
    else:
        is_mutual_match = False

    return render_template(
        'user_detail.html',
        target_user=user,
        offered=offered,
        wanted=wanted,
        reviews=reviews,
        is_mutual_match=is_mutual_match,
        user_can_teach_viewer=user_can_teach_viewer,
        viewer_can_teach_user=viewer_can_teach_user
    )
