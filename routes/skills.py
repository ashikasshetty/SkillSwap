from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import db, SkillOffered, SkillWanted, Category
from routes.auth import login_required

skills_bp = Blueprint('skills', __name__, url_prefix='/skills')

@skills_bp.route('/manage', methods=['GET'])
@login_required
def manage_skills():
    categories = Category.query.order_by(Category.name).all()
    offered = g.user.skills_offered.all()
    wanted = g.user.skills_wanted.all()
    return render_template('manage_skills.html', categories=categories, offered=offered, wanted=wanted)

@skills_bp.route('/offered/add', methods=['POST'])
@login_required
def add_offered_skill():
    skill_name = request.form.get('skill_name', '').strip()
    category_id = request.form.get('category_id', type=int)
    proficiency = request.form.get('proficiency', 'Intermediate')
    description = request.form.get('description', '').strip()

    if not skill_name or not category_id:
        flash('Please provide skill name and select a category.', 'danger')
        return redirect(url_for('skills.manage_skills'))

    new_skill = SkillOffered(
        user_id=g.user.id,
        category_id=category_id,
        skill_name=skill_name,
        proficiency=proficiency,
        description=description
    )
    db.session.add(new_skill)
    db.session.commit()
    flash(f'Skill "{skill_name}" added to your offered skills!', 'success')
    return redirect(url_for('skills.manage_skills'))

@skills_bp.route('/offered/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_offered_skill(skill_id):
    skill = SkillOffered.query.filter_by(id=skill_id, user_id=g.user.id).first_or_404()
    skill_name = skill.skill_name
    db.session.delete(skill)
    db.session.commit()
    flash(f'Skill "{skill_name}" deleted successfully.', 'info')
    return redirect(url_for('skills.manage_skills'))

@skills_bp.route('/wanted/add', methods=['POST'])
@login_required
def add_wanted_skill():
    skill_name = request.form.get('skill_name', '').strip()
    category_id = request.form.get('category_id', type=int)
    target_level = request.form.get('target_level', 'Beginner')
    description = request.form.get('description', '').strip()

    if not skill_name or not category_id:
        flash('Please provide skill name and select a category.', 'danger')
        return redirect(url_for('skills.manage_skills'))

    new_skill = SkillWanted(
        user_id=g.user.id,
        category_id=category_id,
        skill_name=skill_name,
        target_level=target_level,
        description=description
    )
    db.session.add(new_skill)
    db.session.commit()
    flash(f'Skill "{skill_name}" added to your wanted learning list!', 'success')
    return redirect(url_for('skills.manage_skills'))

@skills_bp.route('/wanted/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_wanted_skill(skill_id):
    skill = SkillWanted.query.filter_by(id=skill_id, user_id=g.user.id).first_or_404()
    skill_name = skill.skill_name
    db.session.delete(skill)
    db.session.commit()
    flash(f'Skill "{skill_name}" removed from your learning list.', 'info')
    return redirect(url_for('skills.manage_skills'))
