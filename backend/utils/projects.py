from db import SessionLocal
from models.db_models import Project, ProjectMember, User


def save_project(user_id, project_id):
    db = SessionLocal()

    # Check if project already exists for this user
    existing = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()

    if not existing:
        project = Project(
            id=project_id,
            user_id=user_id,
            owner_id=user_id,
            name=project_id
        )
        db.add(project)
        db.flush()
        member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            invited_by=user_id,
            role="team_lead"
        )
        db.add(member)
        db.commit()

    db.close()


def get_projects(user_id):
    db = SessionLocal()

    memberships = db.query(ProjectMember).filter(
        ProjectMember.user_id == user_id
    ).all()
    result = [m.project_id for m in memberships]
    db.close()
    return result

def get_project_role(user_id, project_id):
    """Returns 'team_lead', 'member', or None if no access."""
    db = SessionLocal()
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    db.close()
    return membership.role if membership else None
# # utils/projects.py
# import json
# import os

# PROJECTS_FILE = "data/projects.json"


# def load_projects():
#     if not os.path.exists(PROJECTS_FILE):
#         return []

#     try:
#         with open(PROJECTS_FILE, "r") as f:
#             content = f.read().strip()
#             if not content:
#                 return []
#             return json.loads(content)
#     except json.JSONDecodeError:
#         return []


# def save_project(project_id: str):
#     projects = load_projects()

#     if project_id not in projects:
#         projects.append(project_id)

#         os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)

#         with open(PROJECTS_FILE, "w") as f:
#             json.dump(projects, f, indent=2)
