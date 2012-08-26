from celery.task import task
from lint.models import Report
from lint.tasks import process_report
from .models import Commit


@task()
def process_commit(commit_pk):
    try:
        commit = Commit.objects.get(pk=commit_pk)
    except Commit.DoesNotExist:
        return
    if commit.report is None:
        commit.report = Report.objects.create(github_url=commit.repo_url)
        commit.save()
    process_report.delay(commit.report.pk, commit.hash)
