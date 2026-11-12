import unittest
from app import create_app
from models import db, User, Category, SkillOffered, SkillWanted, SwapRequest, Message, Review

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test'
    UPLOAD_FOLDER = 'static/uploads'

class SkillSwapTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for test environment with in-memory database
        self.app = create_app(TestConfig)
        
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_user_authentication(self):
        user = User(full_name="Test Student", email="test@student.com", role="user")
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

        self.assertTrue(user.check_password("secret123"))
        self.assertFalse(user.check_password("wrongpass"))
        self.assertFalse(user.is_admin)

    def test_smart_reciprocal_matching(self):
        # Category
        cat = Category(name="Programming", icon="fa-code")
        cat2 = Category(name="Creative", icon="fa-camera")
        db.session.add_all([cat, cat2])
        db.session.commit()

        # User A offers Python, wants Photography
        user_a = User(full_name="User A", email="a@test.com")
        user_a.set_password("pass")
        db.session.add(user_a)
        db.session.commit()

        skill_a_offered = SkillOffered(user_id=user_a.id, category_id=cat.id, skill_name="Python")
        skill_a_wanted = SkillWanted(user_id=user_a.id, category_id=cat2.id, skill_name="Photography")
        db.session.add_all([skill_a_offered, skill_a_wanted])

        # User B offers Photography, wants Python
        user_b = User(full_name="User B", email="b@test.com")
        user_b.set_password("pass")
        db.session.add(user_b)
        db.session.commit()

        skill_b_offered = SkillOffered(user_id=user_b.id, category_id=cat2.id, skill_name="Photography")
        skill_b_wanted = SkillWanted(user_id=user_b.id, category_id=cat.id, skill_name="Python")
        db.session.add_all([skill_b_offered, skill_b_wanted])
        db.session.commit()

        # Check reciprocal match logic
        a_offered_names = {s.skill_name.lower() for s in user_a.skills_offered.all()}
        a_wanted_names = {s.skill_name.lower() for s in user_a.skills_wanted.all()}

        b_offered_names = {s.skill_name.lower() for s in user_b.skills_offered.all()}
        b_wanted_names = {s.skill_name.lower() for s in user_b.skills_wanted.all()}

        can_teach = a_wanted_names.intersection(b_offered_names)
        can_learn = a_offered_names.intersection(b_wanted_names)

        self.assertIn("photography", can_teach)
        self.assertIn("python", can_learn)
        self.assertTrue(len(can_teach) > 0 and len(can_learn) > 0)

    def test_swap_lifecycle_and_messaging(self):
        cat = Category(name="General", icon="fa-book")
        u1 = User(full_name="Sender", email="s@test.com")
        u1.set_password("pass")
        u2 = User(full_name="Receiver", email="r@test.com")
        u2.set_password("pass")
        db.session.add_all([cat, u1, u2])
        db.session.commit()

        swap = SwapRequest(
            sender_id=u1.id,
            receiver_id=u2.id,
            status="pending",
            message="Let's swap!"
        )
        db.session.add(swap)
        db.session.commit()
        self.assertEqual(swap.status, "pending")

        # Accept
        swap.status = "accepted"
        db.session.commit()
        self.assertEqual(swap.status, "accepted")

        # Send Message
        msg = Message(swap_id=swap.id, sender_id=u1.id, receiver_id=u2.id, content="Hi peer!")
        db.session.add(msg)
        db.session.commit()
        self.assertEqual(swap.messages.count(), 1)

        # Complete swap and review
        swap.status = "completed"
        db.session.commit()

        review = Review(swap_id=swap.id, reviewer_id=u1.id, reviewee_id=u2.id, rating=5, comment="Great teacher!")
        db.session.add(review)
        db.session.commit()

        self.assertEqual(u2.average_rating, 5.0)
        self.assertEqual(u2.total_reviews_count, 1)

    def test_chart_data_api(self):
        admin = User(full_name="Admin", email="admin@test.com", role="admin")
        admin.set_password("admin")
        db.session.add(admin)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_id'] = admin.id
            sess['user_role'] = 'admin'

        res = self.client.get('/admin/api/chart-data')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertIn('categories', json_data)
        self.assertIn('swap_status', json_data)

if __name__ == '__main__':
    unittest.main()
