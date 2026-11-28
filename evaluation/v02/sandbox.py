"""Offline candidate execution on Linux using a fresh Bubblewrap namespace."""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile


OUTPUT_LIMIT = 4 * 1024 * 1024
TMP_LIMIT = 64 * 1024 * 1024


def limits():
    import resource
    for name, cap in (('RLIMIT_CPU', 12), ('RLIMIT_AS', 512 * 1024 * 1024),
                      ('RLIMIT_FSIZE', OUTPUT_LIMIT), ('RLIMIT_NOFILE', 128), ('RLIMIT_CORE', 0)):
        kind = getattr(resource, name)
        _, hard = resource.getrlimit(kind)
        bounded = cap if hard == resource.RLIM_INFINITY else min(cap, hard)
        resource.setrlimit(kind, (bounded, bounded))


def run(workspace, argv, timeout=20):
    """Run argv from /work. The caller supplies one disposable, credential-free workspace."""
    if sys.platform != 'linux':
        raise RuntimeError('The v0.2 verifier requires Linux/WSL and Bubblewrap')
    bwrap = shutil.which('bwrap', path='/usr/bin:/bin')
    if not bwrap:
        raise RuntimeError('Bubblewrap is required; no host execution fallback is available')
    workspace = Path(workspace)
    if workspace.is_symlink():
        raise ValueError('Workspace root is a symlink')
    workspace = workspace.resolve(strict=True)
    if not workspace.is_dir() or workspace == Path('/') or workspace.is_relative_to('/usr'):
        raise ValueError('Use a disposable workspace outside the system runtime')
    if any(path.is_symlink() for path in workspace.rglob('*')):
        raise ValueError('Workspace contains a symlink')
    if not argv or not argv[0].startswith('/usr/bin/'):
        raise ValueError('Choose an explicit system executable')
    command = [
        bwrap, '--unshare-all', '--unshare-user', '--disable-userns', '--die-with-parent',
        '--new-session', '--cap-drop', 'ALL', '--clearenv', '--ro-bind', '/usr', '/usr',
        '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
        '--dev', '/dev', '--size', str(TMP_LIMIT), '--tmpfs', '/tmp', '--dir', '/home',
        '--bind', str(workspace), '/work', '--setenv', 'HOME', '/home',
        '--setenv', 'TMPDIR', '/tmp', '--setenv', 'PATH', '/usr/bin:/bin',
        '--setenv', 'LC_ALL', 'C.UTF-8', '--setenv', 'GIT_CONFIG_NOSYSTEM', '1',
        '--setenv', 'GIT_CONFIG_GLOBAL', '/dev/null', '--chdir', '/work', '--', *argv,
    ]
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        with subprocess.Popen(command, env={'PATH': '/usr/bin:/bin'}, stdin=subprocess.DEVNULL,
                              stdout=stdout, stderr=stderr, preexec_fn=limits, start_new_session=True) as proc:
            try:
                code = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait(timeout=5)
                code = 124
        stdout.seek(0)
        stderr.seek(0)
        return subprocess.CompletedProcess(argv, code, stdout.read(OUTPUT_LIMIT), stderr.read(OUTPUT_LIMIT))
