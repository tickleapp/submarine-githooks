# Submarine Githooks
Git-hooks used by [Tickle](https://tickleapp.com)


## Checkers

Submarine will find checkers from Python modules you put under `.githooks/checkers`.
All checkers should be an instance of `submarine_githooks.checker.Checker`, the easiest way to
create a checker is:
```python
from submarine_githooks.checker import checker


@checker
def a_simple_checker(*args):
    pass
```
and then saves it to `.githooks/checkers` as `some_checker.py`

You could reference the arguments which will be passed in at following section.

### Checker settings

#### Active hooks

```python
@checker
@checker.active_hooks('pre-commit')
def a_checker(*args):
    pass


@checker
@checker.active_hooks('pre-commit', 'post-merge')
def another_checker(*args):
    pass
    
    
@checker
@checker.active_hooks('pre-commit')
@checker.active_hooks('post-merge')
def third_checker(*args):
    pass

```

By registering active hooks, the checker will then work only for that type of git hook.
(By default, checkers works for all type of git hooks)

In the above example, the first checker works only for `pre-commit` hook, and the following 2 works for both `pre-commit` and `post-merge`.

Reference: [git hooks types](https://www.digitalocean.com/community/tutorials/how-to-use-git-hooks-to-automate-development-and-deployment-tasks).

#### File pattern and extension

```python
@checker
@checker.file_pattern(r'\.py$')
def a_checker(*args):
    pass
    
@checker
@checker.file_extension('.json')
def another_checker(*args):
    pass
```

You can also register supported file types for a checker.


### Checker implementation

Once if a checker raises any Python exception, the git hook will exit with a non-zero return code.
So, for example, if you want to check all json files are correct and parsable before commit,
you could make a checker like:
```python
@checker
@checker.active_hooks('pre-commit')
@checker.file_extension('.json')
def pre_commit(git_repo, hook_name, file_path):
    json.loads(git_repo.file_content(file_path))

```

So this checker is only active to files which has `.json` extension, and is only active for `pre-commit`.
If the content is not JSON-parsable (i.e. the `json.loads` method raises a `ValueError` exception), the `pre-commit` hook exits with a non-zero return code. And then the `git commit` is aborted.

Note, you should use the `git_repo` object to fetch file content but not read directly from disk 
because the content you should check is the one which has been added into git index.


### Checker function signatrues

```python
from submarine_githooks.checker import checker

@checker
@checker.active_hooks('pre-commit')
def pre_commit(git_repo, hook_name, file_path):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param hook_name: the hook being executing
    :type hook_name: str
    :param file_path: the path to of a file to be committed
    :type file_path: str
    """


@checker
@checker.active_hooks('commit-msg')
def commit_msg(git_repo, hook_name, commit_message_filepath):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param hook_name: the hook being executing
    :type hook_name: str
    :param commit_message_filepath: the path to of file holding the commit message
    :type commit_message_filepath: str
    """


@checker
@checker.active_hooks('post-merge')
def post_merge(git_repo, hook_name, file_path, source_commit, squash_merge):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param hook_name: the hook being executing
    :type hook_name: str
    :param file_path: the path to of a file which has been merged
    :type file_path: str
    :param source_commit: the commit id of merge source
    :type source_commit: str
    :param squash_merge: a flag indicating this is a squash merge or not
    :type suqsh_merge: bool
    """


@checker
@checker.active_hooks('post-checkout')
def post_checkout(git_repo, hook_name, file_path, source_commit_id, destination_commit_id):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param hook_name: the hook being executing
    :type hook_name: str
    :param file_path: the path to of a file which is changed during the checkout
    :type file_path: str
    :param source_commit_id: ref of the previous HEAD
    :type source_commit_id: str
    :param destination_commit_id: ref of the new HEAD
    :type destination_commit_id: str
    """


@checker
@checker.active_hooks('pre-push')
def pre_push(git_repo, hook_name,
             remote_name, remote_url,
             local_ref, local_commit_id,
             remote_ref, remote_commit_id,
             branch_deleted_from_local,
             new_branch_to_remote):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param hook_name: the hook being executing
    :type hook_name: str
    :param remote_name: name of the remote to push to
    :type remote_name: str
    :param remote_url: url of the remote to push to
    :type remote_url: str
    :param local_ref: ref of local branch to be pushed
    :type local_ref: str
    :param local_commit_id: SHA of local branch to be pushed
    :type local_commit_id: str
    :param remote_ref: ref of remote branch to push to
    :type remote_ref: str
    :param remote_commit_id: SHA of remote branch to push to
    :type remote_commit_id: str
    :param branch_deleted_from_local: a flag indicating that local branch has been removed
    :type branch_deleted_from_local: bool
    :param new_branch_to_remote: a flag indicating that this is a new branch to be pushed to remote
    :type new_branch_to_remote: bool
    """
```
