import linecache


def disable_linecache_checks():
    # logging calls linecache.checkcache() a lot.
    linecache.checkcache = lambda x: None
