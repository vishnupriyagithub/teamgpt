# utils/projects.py
import json
import os

PROJECTS_FILE = "data/projects.json"


def load_projects():
    if not os.path.exists(PROJECTS_FILE):
        return []

    try:
        with open(PROJECTS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []


def save_project(project_id: str):
    projects = load_projects()

    if project_id not in projects:
        projects.append(project_id)

        os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)

        with open(PROJECTS_FILE, "w") as f:
            json.dump(projects, f, indent=2)
