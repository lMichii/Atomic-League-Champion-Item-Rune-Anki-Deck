"""Shared CLI/UI build operation and nonblocking project transaction guard."""
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
import os
import threading
from .io import inside


class OperationBusy(ValueError):
    pass


_locks = {}
_locks_guard = threading.Lock()
_active = threading.local()


@contextmanager
def project_operation(root):
    """Serialize writes/builds across threads, UI servers and CLI processes.

    OS advisory locks release on process exit; the empty lock file is not a
    stale-lock sentinel. Nested operations in the same thread are supported.
    """
    root = Path(root).resolve()
    key = str(root).casefold() if os.name == 'nt' else str(root)
    active = getattr(_active, 'roots', set())
    if key in active:
        yield
        return
    with _locks_guard:
        lock = _locks.setdefault(key, threading.Lock())
    if not lock.acquire(blocking=False):
        raise OperationBusy('Another project operation is running. Wait for it to finish, then retry.')
    stream = None
    acquired = False
    try:
        path = root/'build/.pipeline-operation.lock'
        path.parent.mkdir(parents=True, exist_ok=True)
        stream = path.open('a+b')
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as ex:
            raise OperationBusy('Another project operation is running. Wait for it to finish, then retry.') from ex
        acquired = True
        _active.roots = active | {key}
        yield
    finally:
        _active.roots = active
        if stream:
            if acquired:
                stream.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            stream.close()
        lock.release()


def serialized(function):
    @wraps(function)
    def wrapped(owner, *args, **kwargs):
        with project_operation(owner.root):
            return function(owner, *args, **kwargs)
    return wrapped


@serialized
def run_pipeline(project, output=None, export=True):
    """The existing validation/report/build path shared by CLI and local UI."""
    from .validation import validate, save_report
    from .package import build
    report = validate(project)
    save_report(report, inside(project.root, project.config.get('report_dir', 'build/reports')))
    if report['errors']:
        raise ValueError(f"Export blocked by {report['errors']} validation errors; inspect the validation report")
    if not export:
        return {k: v for k, v in report.items() if k != 'findings'}
    output = inside(project.root, output or project.config.get('default_output', 'build/LoL_Pilot.apkg'))
    if output.is_relative_to(project.legacy) or not output.is_relative_to(project.root/'build'):
        raise ValueError('Packages must be written under build/, preserving original APKG')
    return {'validation': {'errors': report['errors'], 'warnings': report['warnings']},
            'package': build(project, output), 'output': str(output)}
