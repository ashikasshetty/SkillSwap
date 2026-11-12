from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import db, SwapRequest, SkillOffered, User, Message
from routes.auth import login_required

swaps_bp = Blueprint('swaps', __name__, url_prefix='/swaps')

@swaps_bp.route('/', strict_slashes=False)
@login_required
def list_swaps():
    user_id = g.user.id
    
    incoming_pending = SwapRequest.query.filter_by(receiver_id=user_id, status='pending').order_by(SwapRequest.created_at.desc()).all()
    outgoing_pending = SwapRequest.query.filter_by(sender_id=user_id, status='pending').order_by(SwapRequest.created_at.desc()).all()
    
    active_swaps = SwapRequest.query.filter(
        ((SwapRequest.sender_id == user_id) | (SwapRequest.receiver_id == user_id)),
        SwapRequest.status == 'accepted'
    ).order_by(SwapRequest.updated_at.desc()).all()
    
    history_swaps = SwapRequest.query.filter(
        ((SwapRequest.sender_id == user_id) | (SwapRequest.receiver_id == user_id)),
        SwapRequest.status.in_(['completed', 'rejected', 'cancelled'])
    ).order_by(SwapRequest.updated_at.desc()).all()

    return render_template(
        'swap_requests.html',
        incoming_pending=incoming_pending,
        outgoing_pending=outgoing_pending,
        active_swaps=active_swaps,
        history_swaps=history_swaps
    )

@swaps_bp.route('/request/<int:receiver_id>', methods=['POST'])
@login_required
def send_request(receiver_id):
    if g.user.id == receiver_id:
        flash('You cannot send a skill swap request to yourself.', 'warning')
        return redirect(url_for('main.explore'))

    receiver = User.query.get_or_404(receiver_id)
    offered_skill_id = request.form.get('offered_skill_id', type=int)
    requested_skill_id = request.form.get('requested_skill_id', type=int)
    message_text = request.form.get('message', '').strip()
    schedule_note = request.form.get('schedule_note', '').strip()

    # Check if there's already an active/pending request between them
    existing = SwapRequest.query.filter(
        ((SwapRequest.sender_id == g.user.id) & (SwapRequest.receiver_id == receiver_id)) |
        ((SwapRequest.sender_id == receiver_id) & (SwapRequest.receiver_id == g.user.id)),
        SwapRequest.status.in_(['pending', 'accepted'])
    ).first()

    if existing:
        flash(f'An active or pending swap request already exists with {receiver.full_name}.', 'info')
        return redirect(url_for('swaps.list_swaps'))

    new_swap = SwapRequest(
        sender_id=g.user.id,
        receiver_id=receiver_id,
        offered_skill_id=offered_skill_id,
        requested_skill_id=requested_skill_id,
        status='pending',
        message=message_text or f"Hi {receiver.full_name}, I'd love to swap skills with you!",
        schedule_note=schedule_note
    )
    db.session.add(new_swap)
    db.session.commit()

    flash(f'Swap proposal sent successfully to {receiver.full_name}!', 'success')
    return redirect(url_for('swaps.list_swaps'))

@swaps_bp.route('/<int:swap_id>/accept', methods=['POST'])
@login_required
def accept_request(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if swap.receiver_id != g.user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('swaps.list_swaps'))

    swap.status = 'accepted'
    
    # Send automatic welcome chat message to open communication
    welcome_msg = Message(
        swap_id=swap.id,
        sender_id=g.user.id,
        receiver_id=swap.sender_id,
        content=f"Hello! I've accepted your skill swap proposal. Let's discuss our schedules and learning plan."
    )
    db.session.add(welcome_msg)
    db.session.commit()

    flash(f'You accepted the skill swap with {swap.sender.full_name}! You can now chat and coordinate.', 'success')
    return redirect(url_for('chat.chat_room', swap_id=swap.id))

@swaps_bp.route('/<int:swap_id>/reject', methods=['POST'])
@login_required
def reject_request(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if swap.receiver_id != g.user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('swaps.list_swaps'))

    swap.status = 'rejected'
    db.session.commit()
    flash(f'Swap request from {swap.sender.full_name} was declined.', 'info')
    return redirect(url_for('swaps.list_swaps'))

@swaps_bp.route('/<int:swap_id>/cancel', methods=['POST'])
@login_required
def cancel_request(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if swap.sender_id != g.user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('swaps.list_swaps'))

    swap.status = 'cancelled'
    db.session.commit()
    flash('Swap proposal cancelled.', 'info')
    return redirect(url_for('swaps.list_swaps'))

@swaps_bp.route('/<int:swap_id>/complete', methods=['POST'])
@login_required
def complete_swap(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if g.user.id not in [swap.sender_id, swap.receiver_id]:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('swaps.list_swaps'))

    swap.status = 'completed'
    db.session.commit()

    partner = swap.receiver if swap.sender_id == g.user.id else swap.sender
    flash(f'Skill swap completed! Please leave a review and rating for {partner.full_name}.', 'success')
    return redirect(url_for('reviews.add_review', swap_id=swap.id))
