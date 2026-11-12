from flask import Blueprint, render_template, request, g, redirect, url_for
from sqlalchemy import or_
from models import db, User, Category, SkillOffered, SkillWanted, SwapRequest, Review

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Platform statistics
    stats = {
        'users_count': User.query.filter_by(is_active=True).count(),
        'skills_offered_count': SkillOffered.query.count(),
        'skills_wanted_count': SkillWanted.query.count(),
        'completed_swaps_count': SwapRequest.query.filter_by(status='completed').count(),
    }
    
    # Recent skills added
    recent_skills = SkillOffered.query.order_by(SkillOffered.created_at.desc()).limit(6).all()
    categories = Category.query.order_by(Category.name).all()
    
    # Featured users
    featured_users = User.query.filter_by(is_active=True).limit(4).all()
    
    # Recent testimonials/reviews
    reviews = Review.query.order_by(Review.created_at.desc()).limit(3).all()
    
    return render_template(
        'index.html',
        stats=stats,
        recent_skills=recent_skills,
        categories=categories,
        featured_users=featured_users,
        reviews=reviews
    )

@main_bp.route('/explore')
def explore():
    query_text = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    filter_type = request.args.get('type', 'offered')  # 'offered', 'wanted', or 'users'
    proficiency = request.args.get('proficiency', '')

    categories = Category.query.order_by(Category.name).all()
    
    # Search logic
    if filter_type == 'wanted':
        skills_query = SkillWanted.query.join(User).filter(User.is_active == True)
        if category_id:
            skills_query = skills_query.filter(SkillWanted.category_id == category_id)
        if proficiency:
            skills_query = skills_query.filter(SkillWanted.target_level == proficiency)
        if query_text:
            skills_query = skills_query.filter(
                or_(
                    SkillWanted.skill_name.ilike(f'%{query_text}%'),
                    SkillWanted.description.ilike(f'%{query_text}%'),
                    User.full_name.ilike(f'%{query_text}%')
                )
            )
        skills = skills_query.order_by(SkillWanted.created_at.desc()).all()
        return render_template(
            'explore.html',
            items=skills,
            categories=categories,
            filter_type=filter_type,
            selected_cat=category_id,
            q=query_text,
            proficiency=proficiency
        )
    else:
        # Default: filter offered skills
        skills_query = SkillOffered.query.join(User).filter(User.is_active == True)
        if category_id:
            skills_query = skills_query.filter(SkillOffered.category_id == category_id)
        if proficiency:
            skills_query = skills_query.filter(SkillOffered.proficiency == proficiency)
        if query_text:
            skills_query = skills_query.filter(
                or_(
                    SkillOffered.skill_name.ilike(f'%{query_text}%'),
                    SkillOffered.description.ilike(f'%{query_text}%'),
                    User.full_name.ilike(f'%{query_text}%')
                )
            )
        skills = skills_query.order_by(SkillOffered.created_at.desc()).all()
        return render_template(
            'explore.html',
            items=skills,
            categories=categories,
            filter_type='offered',
            selected_cat=category_id,
            q=query_text,
            proficiency=proficiency
        )

@main_bp.route('/matches')
def matches():
    """Smart Skill Matching Engine."""
    if not g.user:
        return render_template('matches.html', is_logged_in=False)

    my_offered = g.user.skills_offered.all()
    my_wanted = g.user.skills_wanted.all()

    my_offered_names = {s.skill_name.strip().lower(): s for s in my_offered}
    my_wanted_names = {s.skill_name.strip().lower(): s for s in my_wanted}

    # Fetch other active users
    other_users = User.query.filter(User.id != g.user.id, User.is_active == True).all()

    perfect_matches = []
    learn_opportunities = []
    teach_opportunities = []

    for other in other_users:
        other_offered = other.skills_offered.all()
        other_wanted = other.skills_wanted.all()

        # What other person can teach me
        can_teach_me = [
            s for s in other_offered
            if any(w_name in s.skill_name.lower() or s.skill_name.lower() in w_name for w_name in my_wanted_names)
        ]

        # What I can teach other person
        i_can_teach = [
            s for s in my_offered
            if any(ow.skill_name.lower() in s.skill_name.lower() or s.skill_name.lower() in ow.skill_name.lower() for ow in other_wanted)
        ]

        if can_teach_me and i_can_teach:
            # 100% Reciprocal Match!
            compatibility = min(100, 60 + (len(can_teach_me) * 20) + (len(i_can_teach) * 20))
            perfect_matches.append({
                'user': other,
                'can_teach_me': can_teach_me,
                'i_can_teach': i_can_teach,
                'compatibility': compatibility
            })
        elif can_teach_me:
            learn_opportunities.append({
                'user': other,
                'can_teach_me': can_teach_me,
                'other_wanted': other_wanted
            })
        elif i_can_teach:
            teach_opportunities.append({
                'user': other,
                'i_can_teach': i_can_teach,
                'other_wanted': other_wanted
            })

    # Sort perfect matches by compatibility descending
    perfect_matches.sort(key=lambda x: x['compatibility'], reverse=True)

    return render_template(
        'matches.html',
        is_logged_in=True,
        has_skills=(len(my_offered) > 0 or len(my_wanted) > 0),
        perfect_matches=perfect_matches,
        learn_opportunities=learn_opportunities,
        teach_opportunities=teach_opportunities
    )
