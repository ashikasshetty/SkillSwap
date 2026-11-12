from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, User, Category, SkillOffered, SkillWanted, SwapRequest, Review
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', strict_slashes=False)
@admin_required
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_offered = SkillOffered.query.count()
    total_wanted = SkillWanted.query.count()
    
    total_swaps = SwapRequest.query.count()
    pending_swaps = SwapRequest.query.filter_by(status='pending').count()
    active_swaps = SwapRequest.query.filter_by(status='accepted').count()
    completed_swaps = SwapRequest.query.filter_by(status='completed').count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_swaps = SwapRequest.query.order_by(SwapRequest.created_at.desc()).limit(6).all()
    categories = Category.query.all()

    return render_template(
        'admin/dashboard.html',
        stats={
            'total_users': total_users,
            'active_users': active_users,
            'total_offered': total_offered,
            'total_wanted': total_wanted,
            'total_swaps': total_swaps,
            'pending_swaps': pending_swaps,
            'active_swaps': active_swaps,
            'completed_swaps': completed_swaps
        },
        recent_users=recent_users,
        recent_swaps=recent_swaps,
        categories=categories
    )

@admin_bp.route('/api/chart-data')
@admin_required
def chart_data():
    """Provides structured data for Chart.js interactive charts."""
    categories = Category.query.all()
    cat_labels = [c.name for c in categories]
    cat_offered = [c.skills_offered.count() for c in categories]
    cat_wanted = [c.skills_wanted.count() for c in categories]

    # Swap Status counts
    pending = SwapRequest.query.filter_by(status='pending').count()
    accepted = SwapRequest.query.filter_by(status='accepted').count()
    completed = SwapRequest.query.filter_by(status='completed').count()
    rejected = SwapRequest.query.filter_by(status='rejected').count()

    return jsonify({
        'categories': {
            'labels': cat_labels,
            'offered': cat_offered,
            'wanted': cat_wanted
        },
        'swap_status': {
            'labels': ['Pending', 'In Progress (Active)', 'Completed', 'Declined/Cancelled'],
            'data': [pending, accepted, completed, rejected]
        }
    })

@admin_bp.route('/users')
@admin_required
def users():
    search_q = request.args.get('q', '').strip()
    if search_q:
        all_users = User.query.filter(
            (User.full_name.ilike(f'%{search_q}%')) | 
            (User.email.ilike(f'%{search_q}%'))
        ).order_by(User.created_at.desc()).all()
    else:
        all_users = User.query.order_by(User.created_at.desc()).all()

    return render_template('admin/users.html', users=all_users, q=search_q)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.email == 'admin@skillswap.com':
        flash('Cannot deactivate the root administrator account.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_active = not user.is_active
    db.session.commit()
    status_str = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.full_name} has been {status_str}.', 'info')
    return redirect(url_for('admin.users'))

@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        icon = request.form.get('icon', 'fa-book').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin.categories'))

        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash('Category with this name already exists.', 'warning')
            return redirect(url_for('admin.categories'))

        new_cat = Category(name=name, icon=icon, description=description)
        db.session.add(new_cat)
        db.session.commit()
        flash(f'Category "{name}" added successfully.', 'success')
        return redirect(url_for('admin.categories'))

    all_categories = Category.query.all()
    return render_template('admin/categories.html', categories=all_categories)

@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    if cat.skills_offered.count() > 0 or cat.skills_wanted.count() > 0:
        flash(f'Cannot delete category "{cat.name}" because skills are currently assigned to it.', 'danger')
        return redirect(url_for('admin.categories'))

    cat_name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f'Category "{cat_name}" deleted.', 'info')
    return redirect(url_for('admin.categories'))
