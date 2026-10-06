# DevTrack

A small Django backend for tracking engineering issues, like a stripped-down GitHub Issues.
Engineers file bugs, set priorities and track status. Data is stored in two JSON files:
`reporters.json` and `issues.json`.

## How to run

1. Open a terminal in this folder (the one with `manage.py`).
2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install Django:
   ```
   pip install django
   ```
4. Start the server:
   ```
   python manage.py runserver
   ```
5. The API is now at `http://127.0.0.1:8000/api/`. Test it with Postman.

## Project layout

```
manage.py
reporters.json, issues.json    # data files
devtrack/                      # project settings and main urls.py
issues/models.py               # OOP classes
issues/views.py                # endpoints
issues/urls.py                 # URL routes
```

## Endpoints

| Method | URL | What it does |
|---|---|---|
| POST | `/api/reporters/` | Create a new reporter |
| GET | `/api/reporters/` | Get all reporters |
| GET | `/api/reporters/?id=1` | Get one reporter by ID |
| POST | `/api/issues/` | Create a new issue |
| GET | `/api/issues/` | Get all issues |
| GET | `/api/issues/?id=1` | Get one issue by ID |
| GET | `/api/issues/?status=open` | Get issues with a given status |

Allowed `status`: `open`, `in_progress`, `resolved`, `closed`
Allowed `priority`: `low`, `medium`, `high`, `critical`

### Example: create an issue

`POST /api/issues/`
```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1
}
```

Response `201 Created`:
```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1,
  "message": "[URGENT] Login button not working on mobile — needs immediate attention"
}
```

Errors look like `{"error": "..."}`:
- `400`: invalid data, for example `{"error": "Title cannot be empty"}`
- `404`: not found, for example `{"error": "Issue not found"}`
- `405`: wrong HTTP method

## How the code is organised (OOP)

- `BaseEntity` is an abstract class with `validate()` and `to_dict()`.
- `Reporter` and `Issue` inherit from it.
- `CriticalIssue` and `LowPriorityIssue` inherit from `Issue` and override `describe()`.
  When you create an issue, the view picks the class from its priority
  (critical, low, or the normal `Issue` for medium and high).

## Design decision

**The validation rules live in the model classes, not in the views.**
Each class knows what a valid `Reporter` or `Issue` looks like and raises a `ValueError`
if it is not. The view only catches that error and returns a `400` response.
I did this so `views.py` stays about requests and files, and the rules are in one place
if I add another way to create issues later.

## Postman screenshots

All screenshots are in the `Postman_Screenshots/` folder.

**Success cases**

`POST /api/reporters/` returns 201 Created:

![POST reporter 201](Postman_Screenshots/Screenshot%202026-10-06%20161455.png)

`GET /api/reporters/` returns 200 OK with all reporters:

![GET reporters 200](Postman_Screenshots/Screenshot%202026-10-06%20161548.png)

`GET /api/reporters/?id=1` returns 200 OK with one reporter:

![GET reporter by id 200](Postman_Screenshots/Screenshot%202026-10-06%20161826.png)

`POST /api/issues/` returns 201 Created, with the `[URGENT]` message from `CriticalIssue.describe()`:

![POST issue 201](Postman_Screenshots/Screenshot%202026-10-06%20162210.png)

`GET /api/issues/?status=in_progress` returns 200 OK with the matching issue:

![GET issues by status 200](Postman_Screenshots/Screenshot%202026-10-06%20162433.png)

`GET /api/issues/?status=completed` returns 200 OK with an empty list, because no issue has that status:

![GET issues no match](Postman_Screenshots/Screenshot%202026-10-06%20162406.png)

**Failure case**

`POST /api/reporters/` with an empty name returns 400 Bad Request:

![POST reporter 400](Postman_Screenshots/Screenshot%202026-10-06%20161715.png)
