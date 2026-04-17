"""Tool definition and implementation for listing files in a directory."""

import glob
from tools.utils import is_path_safe


def ls(path='.'):
    """
    List files in a directory, sorted asciibetically.

    >>> import os
    >>> os.makedirs('_test_ls_dir', exist_ok=True)
    >>> ls('_test_ls_dir')
    ''
    >>> ls('.')  # doctest: +ELLIPSIS
    '...'
    >>> ls('/etc')
    'Error: unsafe path'
    >>> import shutil
    >>> shutil.rmtree('_test_ls_dir')
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    files = sorted(glob.glob(f'{path}/*'))
    return '\n'.join(f.split('/')[-1] for f in files)


tool_definition = {
    "type": "function",
    "function": {
        "name": "ls",
        "description": "List files in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory to list. Defaults to current directory.",
                }
            },
            "required": [],
        },
    },
}
