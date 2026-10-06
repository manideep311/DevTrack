import json
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from issues.models import CriticalIssue, Issue, LowPriorityIssue, Reporter

REPORTERS_FILE = Path(settings.BASE_DIR) / 'reporters.json'
ISSUES_FILE = Path(settings.BASE_DIR) / 'issues.json'

def read_json(path):
    if not path.exists():
        return []
    with open(path, 'r') as f:
        return json.load(f)


def write_json(path, records):
    with open(path, 'w') as f:
        json.dump(records, f, indent=2)


def error(message, status):
    return JsonResponse({'error': message}, status=status)


def next_id(records):
    return max((r['id'] for r in records), default=0) + 1



#reporters

@csrf_exempt
def reporters(request):
    if request.method == 'POST':
        return create_reporter(request)
    if request.method == 'GET':
        return get_reporters(request)
    return error('Method not allowed', 405)


def create_reporter(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error('Invalid JSON body', 400)
    records = read_json(REPORTERS_FILE)
    reporter = Reporter(
        data.get('id', next_id(records)),
        data.get('name'),
        data.get('email'),
        data.get('team'),
    )

    try:
        reporter.validate()
    except ValueError as e:
        return error(str(e), 400)

    if any(r['id'] == reporter.id for r in records):
        return error('Reporter with this id already exists', 400)

    records.append(reporter.to_dict())
    write_json(REPORTERS_FILE, records)
    return JsonResponse(reporter.to_dict(), status=201)


def get_reporters(request):
    records = read_json(REPORTERS_FILE)
    reporter_id = request.GET.get('id')

    if reporter_id is None:                      
        return JsonResponse(records, safe=False, status=200)

    try:                                          
        reporter_id = int(reporter_id)
    except ValueError:
        return error('id must be an integer', 400)

    for record in records:
        if record['id'] == reporter_id:
            return JsonResponse(record, status=200)
    return error('Reporter not found', 404)


#issues

@csrf_exempt
def issues(request):
    if request.method == 'POST':
        return create_issue(request)
    if request.method == 'GET':
        return get_issues(request)
    return error('Method not allowed', 405)


def create_issue(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error('Invalid JSON body', 400)

    records = read_json(ISSUES_FILE)
    issue_id = data.get('id', next_id(records))
    title = data.get('title')
    description = data.get('description', '')
    status = data.get('status')
    priority = data.get('priority')
    reporter_id = data.get('reporter_id')

    if priority == 'critical':
        issue = CriticalIssue(issue_id, title, description, status, priority, reporter_id)
    elif priority == 'low':
        issue = LowPriorityIssue(issue_id, title, description, status, priority, reporter_id)
    else:
        issue = Issue(issue_id, title, description, status, priority, reporter_id)

    try:
        issue.validate()
    except ValueError as e:
        return error(str(e), 400)

    if any(i['id'] == issue.id for i in records):
        return error('Issue with this id already exists', 400)

    if not any(r['id'] == issue.reporter_id for r in read_json(REPORTERS_FILE)):
        return error('Reporter not found', 404)

    records.append(issue.to_dict())
    write_json(ISSUES_FILE, records)

    response_data = issue.to_dict()
    response_data['message'] = issue.describe()
    return JsonResponse(response_data, status=201)


def get_issues(request):
    records = read_json(ISSUES_FILE)
    issue_id = request.GET.get('id')
    status = request.GET.get('status')

    if issue_id is not None:                     
        try:
            issue_id = int(issue_id)
        except ValueError:
            return error('id must be an integer', 400)
        for record in records:
            if record['id'] == issue_id:
                return JsonResponse(record, status=200)
        return error('Issue not found', 404)

    if status is not None:                       
        records = [r for r in records if r['status'] == status]

    return JsonResponse(records, safe=False, status=200)  
