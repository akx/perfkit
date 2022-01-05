import logging
import textwrap


# get_log_tree is via
# https://github.com/brandon-rhodes/logging_tree/blob/b2d7cee13c0fe0a2601b5a2b705ff59375978a2f/logging_tree/nodes.py
# which is BSD licensed


def get_log_tree():
    """Return a tree of tuples representing the logger layout.
    Each tuple looks like ``('logger-name', <Logger>, [...])`` where the
    third element is a list of zero or more child tuples that share the
    same layout.
    """
    root = ("<root>", logging.root, [])
    nodes = {}
    for name, logger in sorted(logging.root.manager.loggerDict.items()):
        nodes[name] = node = (name, logger, [])
        i = name.rfind(".", 0, len(name) - 1)  # same formula used in `logging`
        if i == -1:
            parent = root
        else:
            parent = nodes[name[:i]]
        parent[2].append(node)
    return root


def dump_log_config():
    def print_logger(l_triple, level=0):
        name, logger, children = l_triple
        indent = "  " * level
        if isinstance(logger, logging.PlaceHolder):
            content = f"> {name}"
        elif isinstance(logger, logging.Logger):
            content = (
                f"* {name} "
                f"[{logging.getLevelName(logger.getEffectiveLevel())}] "
                f"{'^' if logger.propagate else '(not propagating)'}"
            )
            for handler in logger.handlers:
                content += f"\n  H: {handler!r}"
                if isinstance(handler, logging.Handler):
                    for filter in handler.filters:
                        content += f"\n  |-F: {filter!r}"

        else:
            content = f"??? {logger!r}"
        print(textwrap.indent(content.strip("\n"), indent))
        for child_triple in children:
            print_logger(child_triple, level=level + 1)

    print_logger(get_log_tree())
