import os
from flask import Flask, render_template, g, session
from config import Config
from models import db, User, SwapRequest, Message

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.skills import skills_bp
    from routes.swaps import swaps_bp
    from routes.chat import chat_bp
    from routes.reviews import reviews_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(swaps_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)

    # Global template context processor
    @app.context_processor
    def inject_notifications():
        if g.user:
            # Count pending incoming requests
            pending_count = SwapRequest.query.filter_by(
                receiver_id=g.user.id,
                status='pending'
            ).count()
            
            # Count unread messages
            unread_msgs = Message.query.filter_by(
                receiver_id=g.user.id,
                is_read=False
            ).count()
            
            return {
                'nav_pending_swaps': pending_count,
                'nav_unread_messages': unread_msgs
            }
        return {
            'nav_pending_swaps': 0,
            'nav_unread_messages': 0
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Auto create tables on startup
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("SkillSwap web application running at http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
