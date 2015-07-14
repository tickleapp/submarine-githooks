import json
from submarine_githooks.checker import checker


# noinspection PyUnusedLocal
@checker
@checker.active_hooks('pre-commit')
@checker.file_extension('.json')
def pre_commit(git_repo, file_path, content_loader):
    """
    :type git_repo: taskr.contrib.git.GitRepo
    :type file_path: str
    :type content_loader: () -> (str | bytes)
    """
    json.loads(content_loader())
