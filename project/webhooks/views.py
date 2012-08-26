from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Commit
from .tasks import process_commit
from .utils import parse_hook_data


@require_POST
@csrf_exempt
def handler(request):
    payload = request.POST.get('payload', '')
    try:
        payload_data = json.loads(payload)
    except ValueError:
        return HttpResponseBadRequest()
    hook_data = parse_hook_data(payload_data)
    hash = hook_data.pop('hash')
    repo_name = hook_data.pop('repo_name')
    repo_user = hook_data.pop('repo_user')

    commit, created = Commit.objects.get_or_create(
        hash=hash, repo_name=repo_name,
        repo_user=repo_user, defaults=hook_data
    )
    process_commit.delay(commit.pk)
    return HttpResponse(status=201 if created else 200)
