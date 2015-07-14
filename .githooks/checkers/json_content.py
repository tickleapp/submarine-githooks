import json
from submarine_githooks.checker import checker


# noinspection PyUnusedLocal
@checker
@checker.active_hooks('pre-commit')
@checker.file_extension('.json')
def pre_commit(git_repo, hook_name, file_path):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param hook_name: the hook being executing
    :type hook_name: str
    :param file_path: the path to of a file to be committed
    :type file_path: str
    """
    json.loads(git_repo.file_content(file_path))
