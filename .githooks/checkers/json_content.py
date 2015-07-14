import json
from submarine_githooks.checker import checker


# noinspection PyUnusedLocal
@checker
@checker.active_hooks('pre-commit')
@checker.file_extension('.json')
def pre_commit(git_repo, file_path, content_loader):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param file_path: the path to of a file to be committed
    :type file_path: str
    :param content_loader: a callable that will return the content of staged file to be committed
    :type content_loader: () -> (str | bytes)
    """
    json.loads(content_loader())
