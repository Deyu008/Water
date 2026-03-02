from __future__ import annotations

from datetime import datetime, timedelta

from PySide6.QtCore import QObject, QTimer, Signal, Slot


class ReminderEngine(QObject):
    """
    Manages periodic water drinking reminders.

    Signals:
        remind_triggered: emitted when it's time to drink water
        next_due_changed(str): emitted when next reminder time updates, arg is formatted time string
        state_changed(str): emitted when state changes ('running', 'paused', 'stopped')

    States: running, paused, stopped

    Usage:
        engine = ReminderEngine(interval_minutes=60)
        engine.remind_triggered.connect(on_remind)
        engine.start()
    """

    remind_triggered = Signal()
    next_due_changed = Signal(str)
    state_changed = Signal(str)

    def __init__(self, interval_minutes: int = 60, parent=None):
        super().__init__(parent)

        if interval_minutes <= 0:
            raise ValueError("interval_minutes must be > 0")

        self._interval_ms = int(interval_minutes * 60 * 1000)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

        self._state = "stopped"
        self._next_due: datetime | None = None
        self._remaining_ms: int | None = None

    @Slot()
    def start(self):
        self._remaining_ms = None
        self._start_timer(self._interval_ms)
        self._set_state("running")

    @Slot()
    def pause(self):
        if self._state != "running":
            return

        remaining = self._compute_remaining_ms()
        self._remaining_ms = max(1, remaining)
        self._timer.stop()
        self._next_due = None
        self.next_due_changed.emit("")
        self._set_state("paused")

    @Slot()
    def resume(self):
        if self._state != "paused":
            return

        remaining = self._remaining_ms if self._remaining_ms and self._remaining_ms > 0 else self._interval_ms
        self._start_timer(remaining)
        self._remaining_ms = None
        self._set_state("running")

    @Slot()
    def stop(self):
        self._timer.stop()
        self._remaining_ms = None
        self._next_due = None
        self.next_due_changed.emit("")
        self._set_state("stopped")

    @Slot(int)
    def set_interval(self, minutes: int):
        if minutes <= 0:
            raise ValueError("minutes must be > 0")

        self._interval_ms = int(minutes * 60 * 1000)

        if self._state == "running":
            self._start_timer(self._interval_ms)
        elif self._state == "paused":
            self._remaining_ms = self._interval_ms

    @property
    def state(self) -> str:
        return self._state

    @property
    def next_due(self) -> datetime | None:
        return self._next_due

    def _compute_remaining_ms(self) -> int:
        """Compute remaining ms based on absolute next_due time.

        This is more robust than QTimer.remainingTime() after system
        sleep/resume, because the absolute timestamp doesn't drift.
        """
        if self._next_due is not None:
            delta = (self._next_due - datetime.now()).total_seconds()
            return max(1, int(delta * 1000))
        remaining = self._timer.remainingTime()
        return remaining if remaining > 0 else self._interval_ms

    @Slot()
    def _on_timeout(self):
        if self._state != "running":
            return

        # After system sleep the timer may fire late. Check if we're actually
        # past due (or close enough) before triggering.
        if self._next_due is not None:
            now = datetime.now()
            remaining = (self._next_due - now).total_seconds()
            if remaining > 1:
                # Not yet due (timer fired early or spurious), reschedule
                self._start_timer(int(remaining * 1000))
                return

        self.remind_triggered.emit()
        self._start_timer(self._interval_ms)

    def _start_timer(self, delay_ms: int):
        delay_ms = max(1, int(delay_ms))
        self._next_due = datetime.now() + timedelta(milliseconds=delay_ms)
        self._timer.start(delay_ms)
        self.next_due_changed.emit(self._next_due.strftime("%H:%M"))

    def _set_state(self, state: str):
        if self._state == state:
            return
        self._state = state
        self.state_changed.emit(state)
