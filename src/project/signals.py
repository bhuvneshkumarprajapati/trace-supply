import json
from typing import Protocol, cast

from celery import shared_task
from django.db import transaction
from django.dispatch import Signal
from django.utils.module_loading import import_string


class _DelayedTask(Protocol):
    def delay(self, *args: str) -> object: ...


@shared_task
def _dispatch_reliable_receiver(receiver_path: str, kwargs_json: str) -> None:
    receiver = import_string(receiver_path)
    receiver(**json.loads(kwargs_json))


class ReliableSignal(Signal):
    """A Django signal dispatched asynchronously after transaction commit."""

    def send_reliable(self, sender, **kwargs) -> None:
        payload = json.dumps(kwargs)
        sync_receivers, async_receivers = self._live_receivers(sender)
        dispatch = cast(_DelayedTask, _dispatch_reliable_receiver)
        for receiver in (*sync_receivers, *async_receivers):
            path = f"{receiver.__module__}.{receiver.__qualname__}"
            transaction.on_commit(lambda p=path: dispatch.delay(p, payload))
