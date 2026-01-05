# Todo Planner

A compact yet feature-rich web application for task management with priorities, deadlines, categories, subtasks, drag & drop, and dark theme support.

## Features

- User registration and login with JWT token authentication.
- Create tasks with priority (`low`, `medium`, `high`), deadline, and category (`work`, `personal`, `study`, `sport`).
- Subtasks for each task with progress tracking (completed/total count).
- Filters (all / active / completed), search by title, sorting by position, deadline, priority, or status.
- Drag & drop task reordering when sorted by position.
- Extended statistics: total tasks, active/completed, weekly/monthly completed, overdue tasks.
- Toggle between light and dark themes.

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite.
- **Frontend**: Pure HTML, CSS, JavaScript.
- **Testing**: `pytest` (unit, integration, e2e), separate levels via DEBUG=1/2/3.
- **Infrastructure**: Dockerfile, GitHub Actions (CI for tests, coverage, and linting).

## Installation and Setup

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
