import time

class PROFILER:
    def __init__(self):
        self._start = time.ticks_ms()
        self._last = self._start
        print(f"[------] Profiler Start")

    def duration(self,namespace, message):
        now = time.ticks_ms()
        total_elapsed = time.ticks_diff(now, self._start)
        step_elapsed = time.ticks_diff(now, self._last)
        print(f"[{namespace}] +{step_elapsed}ms / {total_elapsed}ms : {message}")
        self._last = now

Profiler = PROFILER()