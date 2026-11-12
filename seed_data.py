import os
from datetime import datetime, timezone
from app import create_app
from models import db, User, Category, SkillOffered, SkillWanted, SwapRequest, Message, Review

def seed():
    app = create_app()
    with app.app_context():
        # Clear existing tables cleanly
        db.drop_all()
        db.create_all()

        print("--> Populating Skill Categories...")
        categories_data = [
            ("Computer Programming", "fa-code", "Python, Java, C++, Algorithms & Data Structures"),
            ("Web & Mobile Development", "fa-laptop-code", "HTML, CSS, JavaScript, React, Flask, Mobile Apps"),
            ("Graphic Design & UI/UX", "fa-palette", "Figma, Adobe Illustrator, UI Design, Wireframing"),
            ("Photography & Video Editing", "fa-camera-retro", "DSLR Photography, Premiere Pro, Color Grading"),
            ("Languages & Communication", "fa-language", "Spanish, French, Public Speaking, English Fluency"),
            ("Music & Audio", "fa-music", "Acoustic Guitar, Keyboard, Vocal Training, Audio Mixing"),
            ("Data Science & AI", "fa-brain", "Data Analysis, Machine Learning, Statistics, Pandas"),
            ("Digital Marketing", "fa-bullhorn", "SEO, Social Media Marketing, Content Strategy")
        ]

        cat_map = {}
        for name, icon, desc in categories_data:
            c = Category(name=name, icon=icon, description=desc)
            db.session.add(c)
            cat_map[name] = c
        db.session.commit()

        print("--> Creating Users (including Ashika Shetty, Ganavi K.H, and Admin)...")
        # 1. Ashika Shetty
        ashika = User(
            full_name="Ashika Shetty",
            email="ashika@skillswap.com",
            bio="II MCA student at St Agnes College. Passionate about Python, Flask web development, and cloud computing. Looking to learn photography and UI design!",
            location="St Agnes College (Autonomous), Mangaluru",
            avatar="avatar_ashika.png",
            role="user"
        )
        ashika.set_password("password123")

        # 2. Ganavi K.H
        ganavi = User(
            full_name="Ganavi K.H",
            email="ganavi@skillswap.com",
            bio="II MCA student & photography enthusiast. Skilled in DSLR photography, Lightroom, and video editing. Excited to exchange skills for Python programming!",
            location="St Agnes College (Autonomous), Mangaluru",
            avatar="avatar_ganavi.png",
            role="user"
        )
        ganavi.set_password("password123")

        # 3. Rahul Sharma
        rahul = User(
            full_name="Rahul Sharma",
            email="rahul@skillswap.com",
            bio="UI/UX Designer who loves crafting aesthetic user journeys and Figma systems. Eager to understand backend web development.",
            location="Mangaluru, Karnataka",
            avatar="avatar_rahul.png",
            role="user"
        )
        rahul.set_password("password123")

        # 4. Ananya Rao
        ananya = User(
            full_name="Ananya Rao",
            email="ananya@skillswap.com",
            bio="Linguist and communication coach. Fluent in Spanish & public speaking. Interested in photography and machine learning.",
            location="Mangaluru, Karnataka",
            avatar="avatar_ananya.png",
            role="user"
        )
        ananya.set_password("password123")

        # 5. Platform Admin
        admin = User(
            full_name="Platform Administrator",
            email="admin@skillswap.com",
            bio="SkillSwap System Administrator for MCA Mini Projects at St Agnes College.",
            location="St Agnes College MCA Dept",
            avatar="avatar_admin.png",
            role="admin"
        )
        admin.set_password("admin123")

        db.session.add_all([ashika, ganavi, rahul, ananya, admin])
        db.session.commit()

        print("--> Populating Offered and Wanted Skills...")
        # Ashika's skills
        ash_teach_py = SkillOffered(
            user_id=ashika.id,
            category_id=cat_map["Computer Programming"].id,
            skill_name="Python Programming",
            proficiency="Expert",
            description="Core Python, OOP concepts, data structures, automation scripts, and problem solving."
        )
        ash_teach_web = SkillOffered(
            user_id=ashika.id,
            category_id=cat_map["Web & Mobile Development"].id,
            skill_name="Web Development with Flask",
            proficiency="Advanced",
            description="Building backend RESTful APIs, Jinja templating, SQLAlchemy ORM, and MVC architecture."
        )
        ash_want_photo = SkillWanted(
            user_id=ashika.id,
            category_id=cat_map["Photography & Video Editing"].id,
            skill_name="Digital Photography",
            target_level="Beginner",
            description="Mastering DSLR camera settings, manual mode, aperture, shutter speed, and framing."
        )
        ash_want_ui = SkillWanted(
            user_id=ashika.id,
            category_id=cat_map["Graphic Design & UI/UX"].id,
            skill_name="UI/UX Design with Figma",
            target_level="Intermediate",
            description="Learning wireframing, color theory, component design systems, and mobile layouts."
        )

        # Ganavi's skills
        gan_teach_photo = SkillOffered(
            user_id=ganavi.id,
            category_id=cat_map["Photography & Video Editing"].id,
            skill_name="Digital Photography",
            proficiency="Expert",
            description="DSLR composition, golden hour portraits, aperture triangle, lighting, and Adobe Lightroom."
        )
        gan_teach_video = SkillOffered(
            user_id=ganavi.id,
            category_id=cat_map["Photography & Video Editing"].id,
            skill_name="Video Editing & Color Grading",
            proficiency="Advanced",
            description="Premiere Pro video cutting, B-roll timing, color grading, and audio syncing."
        )
        gan_want_py = SkillWanted(
            user_id=ganavi.id,
            category_id=cat_map["Computer Programming"].id,
            skill_name="Python Programming",
            target_level="Beginner",
            description="Want to learn Python syntax, loops, functions, and write mini project scripts."
        )
        gan_want_web = SkillWanted(
            user_id=ganavi.id,
            category_id=cat_map["Web & Mobile Development"].id,
            skill_name="Web Development with Flask",
            target_level="Beginner",
            description="Want to learn how web servers work and how to build web pages."
        )

        # Rahul's skills
        rahul_teach_ui = SkillOffered(
            user_id=rahul.id,
            category_id=cat_map["Graphic Design & UI/UX"].id,
            skill_name="UI/UX Design with Figma",
            proficiency="Expert",
            description="Interactive prototyping, design systems, typography, and responsive UX."
        )
        rahul_want_py = SkillWanted(
            user_id=rahul.id,
            category_id=cat_map["Computer Programming"].id,
            skill_name="Python Programming",
            target_level="Beginner",
            description="Interested in basic Python coding."
        )

        # Ananya's skills
        ananya_teach_spanish = SkillOffered(
            user_id=ananya.id,
            category_id=cat_map["Languages & Communication"].id,
            skill_name="Conversational Spanish",
            proficiency="Expert",
            description="Grammar, vocabulary, cultural nuances, and fluent daily speaking practice."
        )
        ananya_want_photo = SkillWanted(
            user_id=ananya.id,
            category_id=cat_map["Photography & Video Editing"].id,
            skill_name="Digital Photography",
            target_level="Beginner",
            description="Looking to take better travel photos with my camera."
        )

        db.session.add_all([
            ash_teach_py, ash_teach_web, ash_want_photo, ash_want_ui,
            gan_teach_photo, gan_teach_video, gan_want_py, gan_want_web,
            rahul_teach_ui, rahul_want_py,
            ananya_teach_spanish, ananya_want_photo
        ])
        db.session.commit()

        print("--> Creating Sample Swap Requests, Chats & Ratings...")
        # 1. Active Swap between Ashika and Ganavi (Perfect Mutual Match!)
        swap_ashika_ganavi = SwapRequest(
            sender_id=ashika.id,
            receiver_id=ganavi.id,
            offered_skill_id=ash_teach_py.id,
            requested_skill_id=gan_teach_photo.id,
            status="accepted",
            message="Hi Ganavi! I saw your amazing photography portfolio. I would love to teach you Python programming in exchange for learning DSLR photography basics!",
            schedule_note="Saturdays 3:00 PM - 5:00 PM at College Computer Lab / Campus"
        )
        db.session.add(swap_ashika_ganavi)
        db.session.commit()

        # Seed chat messages in the active swap
        msg1 = Message(
            swap_id=swap_ashika_ganavi.id,
            sender_id=ashika.id,
            receiver_id=ganavi.id,
            content="Hi Ganavi! Really excited to start our skill exchange. Are you free this Saturday to kick off Python basics?",
            is_read=True
        )
        msg2 = Message(
            swap_id=swap_ashika_ganavi.id,
            sender_id=ganavi.id,
            receiver_id=ashika.id,
            content="Hey Ashika! Absolutely! I have prepared my notes on DSLR camera settings and ISO. Let's meet at 3:30 PM.",
            is_read=True
        )
        msg3 = Message(
            swap_id=swap_ashika_ganavi.id,
            sender_id=ashika.id,
            receiver_id=ganavi.id,
            content="Awesome! I'll set up VS Code and Python on your laptop first so you can write your first script.",
            is_read=False
        )
        db.session.add_all([msg1, msg2, msg3])

        # 2. Completed Swap between Rahul and Ashika with 5-star rating!
        swap_rahul_ashika = SwapRequest(
            sender_id=rahul.id,
            receiver_id=ashika.id,
            offered_skill_id=rahul_teach_ui.id,
            requested_skill_id=ash_teach_web.id,
            status="completed",
            message="Hey Ashika, could you guide me through Flask backend architecture? I can teach you Figma prototyping.",
            schedule_note="Completed 4 peer learning sessions"
        )
        db.session.add(swap_rahul_ashika)
        db.session.commit()

        review_from_rahul = Review(
            swap_id=swap_rahul_ashika.id,
            reviewer_id=rahul.id,
            reviewee_id=ashika.id,
            rating=5,
            comment="Ashika is an exceptional mentor! She explained Flask routing and SQLAlchemy with crystal-clear examples. Highly recommended peer teacher!"
        )
        review_from_ashika = Review(
            swap_id=swap_rahul_ashika.id,
            reviewer_id=ashika.id,
            reviewee_id=rahul.id,
            rating=5,
            comment="Rahul is super patient and taught me auto-layout and component design in Figma. Learned so much in just a few sessions!"
        )
        db.session.add_all([review_from_rahul, review_from_ashika])

        # 3. Pending swap proposal from Ananya to Ganavi
        swap_ananya_ganavi = SwapRequest(
            sender_id=ananya.id,
            receiver_id=ganavi.id,
            offered_skill_id=ananya_teach_spanish.id,
            requested_skill_id=gan_teach_photo.id,
            status="pending",
            message="¡Hola Ganavi! I would love to learn landscape photography techniques from you. I can offer conversational Spanish lessons in return!",
            schedule_note="Flexible weekday evenings"
        )
        db.session.add(swap_ananya_ganavi)
        db.session.commit()

        print("\n=======================================================")
        print(" [SUCCESS] SkillSwap Database seeded successfully!")
        print(" Test Accounts:")
        print("  1. Ashika Shetty : ashika@skillswap.com / password123")
        print("  2. Ganavi K.H    : ganavi@skillswap.com / password123")
        print("  3. Rahul Sharma  : rahul@skillswap.com  / password123")
        print("  4. Ananya Rao    : ananya@skillswap.com / password123")
        print("  5. Administrator : admin@skillswap.com  / admin123")
        print("=======================================================\n")

if __name__ == '__main__':
    seed()
