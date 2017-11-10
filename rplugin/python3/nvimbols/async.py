from threading import Thread, Lock


class Job(Thread):
    def __init__(self, parent, func, result_func):
        self._parent = parent
        self._func = func

        self.result_func = result_func
        self.finished = False
        self.exception = None
        self.result = None

        Thread.__init__(self)

    def run(self):
        try:
            self.result = self._func()
        except Exception as err:
            self.exception = err
        finally:
            self.finished = True
            self._parent.job_finished(self)


class JobQueue:
    def __init__(self):
        self._jobs = []
        self._lock = Lock()

    def is_running(self):
        with self._lock:
            return len(self._jobs) > 0

    def join(self):
        job = None
        with self._lock:
            if(len(self._jobs) == 0):
                return
            job = self._jobs[-1]

        if(job is not None):
            job.join()

        # A new job might have been added during job.join(), so we repeat
        self.join()

    def job_finished(self, job):
        with self._lock:
            # We only care for the last job in the queue
            if(self._jobs[-1] == job):
                job.result_func(job.result, job.exception)

                # Forget all other threads. Let them run and report finished,
                # but their results will never be published
                self._jobs = []

    def add_job(self, func, result_func):
        with self._lock:
            job = Job(self, func, result_func)
            self._jobs += [job]

            job.start()
