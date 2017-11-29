from threading import Thread, Lock

from nvimbols.util import on_error


class JobQueue:
    def __init__(self, tasks=1, vim=None, threadsafe=False):
        self._tasks = tasks
        self._vim = vim
        self._threadsafe = threadsafe
        if threadsafe:
            self._tasks = 1

        self._lock = Lock()
        self._jobs = []
        self._running_jobs = 0

    def is_empty(self):
        """
        Returns True if there are no jobs waiting. However, there might be some working
        """
        with self._lock:
            return len(self._jobs) == 0

    def is_done(self):
        """
        Returns True if there are no jobs waiting and jobs executing
        """
        with self._lock:
            return len(self._jobs) == 0 and self._running_jobs == 0

    def job(self, job):
        with self._lock:
            self._jobs += [job]

        self._dispatch()

    def _next_job(self):
        with self._lock:
            if len(self._jobs) == 0:
                return None
            else:
                job = self._jobs[0]
                del self._jobs[0]
                return job

    def _dispatch(self):
        with self._lock:
            while self._running_jobs < self._tasks:
                if self._threadsafe:
                    self._vim.session.threadsafe_call(lambda: self._action())
                else:
                    Thread(target=lambda: self._action()).start()
                self._running_jobs += 1

    def _on_task_finished(self):
        with self._lock:
            if self._running_jobs < 1:
                raise Exception("Unexpected call to _on_task_finished")
            self._running_jobs -= 1

        self._dispatch()

    def _action(self):
        try:
            job = self._next_job()

            if job is not None:
                repeat = job() is not None

                if repeat:
                    self.job(job)
        except Exception as err:
            on_error(self._vim, err)
        finally:
            self._on_task_finished()
