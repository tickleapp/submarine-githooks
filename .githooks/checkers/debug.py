from submarine_githooks.checker import checker


@checker
def func(*args):
    print('submarine-githooks debug: ' + str(args))
