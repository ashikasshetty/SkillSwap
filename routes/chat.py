from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from models import db, SwapRequest, Message, User
from routes.auth import login_required

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/<int:swap_id>')
@login_required
def chat_room(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if g.user.id not in [swap.sender_id, swap.receiver_id]:
        flash('Unauthorized access to this chat.', 'danger')
        return redirect(url_for('swaps.list_swaps'))

    partner = swap.receiver if swap.sender_id == g.user.id else swap.sender

    # Mark all unread incoming messages as read
    unread_messages = Message.query.filter_by(
        swap_id=swap.id,
        receiver_id=g.user.id,
        is_read=False
    ).all()
    for m in unread_messages:
        m.is_read = True
    db.session.commit()

    messages = Message.query.filter_by(swap_id=swap.id).order_by(Message.created_at.asc()).all()

    return render_template(
        'chat.html',
        swap=swap,
        partner=partner,
        messages=messages
    )

@chat_bp.route('/<int:swap_id>/send', methods=['POST'])
@login_required
def send_message(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if g.user.id not in [swap.sender_id, swap.receiver_id]:
        return jsonify({'error': 'Unauthorized'}), 403

    receiver_id = swap.receiver_id if swap.sender_id == g.user.id else swap.sender_id
    
    # Check JSON or Form
    if request.is_json:
        data = request.get_json()
        content = data.get('content', '').strip()
    else:
        content = request.form.get('content', '').strip()

    if not content:
        if request.is_json:
            return jsonify({'error': 'Message content cannot be empty'}), 400
        return redirect(url_for('chat.chat_room', swap_id=swap.id))

    new_msg = Message(
        swap_id=swap.id,
        sender_id=g.user.id,
        receiver_id=receiver_id,
        content=content
    )
    db.session.add(new_msg)
    db.session.commit()

    if request.is_json:
        return jsonify({
            'success': True,
            'message': {
                'id': new_msg.id,
                'sender_id': new_msg.sender_id,
                'sender_name': g.user.full_name,
                'content': new_msg.content,
                'timestamp': new_msg.created_at.strftime('%I:%M %p')
            }
        })

    return redirect(url_for('chat.chat_room', swap_id=swap.id))

@chat_bp.route('/<int:swap_id>/api/messages')
@login_required
def get_messages_api(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if g.user.id not in [swap.sender_id, swap.receiver_id]:
        return jsonify({'error': 'Unauthorized'}), 403

    # Mark incoming as read
    Message.query.filter_by(
        swap_id=swap.id,
        receiver_id=g.user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()

    messages = Message.query.filter_by(swap_id=swap.id).order_by(Message.created_at.asc()).all()
    
    return jsonify({
        'messages': [{
            'id': m.id,
            'sender_id': m.sender_id,
            'sender_name': m.sender.full_name,
            'content': m.content,
            'timestamp': m.created_at.strftime('%I:%M %p'),
            'is_me': (m.sender_id == g.user.id)
        } for m in messages]
    })
