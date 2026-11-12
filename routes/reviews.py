from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import db, SwapRequest, Review, User
from routes.auth import login_required

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@reviews_bp.route('/<int:swap_id>/add', methods=['GET', 'POST'])
@login_required
def add_review(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if g.user.id not in [swap.sender_id, swap.receiver_id]:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('swaps.list_swaps'))

    if swap.status != 'completed':
        flash('You can only review completed skill swaps.', 'warning')
        return redirect(url_for('swaps.list_swaps'))

    reviewee = swap.receiver if swap.sender_id == g.user.id else swap.sender

    # Check if already reviewed
    existing_review = Review.query.filter_by(
        swap_id=swap.id,
        reviewer_id=g.user.id
    ).first()

    if existing_review:
        flash('You have already submitted a review for this skill swap.', 'info')
        return redirect(url_for('auth.user_detail', user_id=reviewee.id))

    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()

        if not rating or rating < 1 or rating > 5:
            flash('Please select a star rating between 1 and 5.', 'danger')
            return render_template('review_modal.html', swap=swap, reviewee=reviewee)

        new_review = Review(
            swap_id=swap.id,
            reviewer_id=g.user.id,
            reviewee_id=reviewee.id,
            rating=rating,
            comment=comment
        )
        db.session.add(new_review)
        db.session.commit()

        flash(f'Thank you! Your feedback for {reviewee.full_name} has been recorded.', 'success')
        return redirect(url_for('auth.user_detail', user_id=reviewee.id))

    return render_template('review_modal.html', swap=swap, reviewee=reviewee)
