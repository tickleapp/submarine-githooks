# Aquarium Githooks
Git-hooks used by [Tickle](https://tickleapp.com)


## Checkers

### Checker interface

```python
from submarine_githooks.checker import checker

@checker
@checker.active_hooks('pre-commit')
def pre_commit(git_repo, file_path, content_loader):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param file_path: the path to of a file to be committed
    :type file_path: str
    :param content_loader: a callable that will return the content of staged file to be committed
    :type content_loader: () -> (str | bytes)
    """


@checker
@checker.active_hooks('commit-msg')
def commit_msg(git_repo, commit_message_filepath):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param commit_message_filepath: a text file which contains the commit message
    :type commit_message_filepath: str
    """
```
