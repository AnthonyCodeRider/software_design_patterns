from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Publisher(Protocol):
    def subscribe(self, message_type: str, observer: Observer): ...

    def unsubscribe(self, message_type: str, observer: Observer): ...

    def notify(self, message: Message): ...


class Observer(Protocol):
    def update(self, message: Message): ...


@dataclass
class Message:
    content: str
    message_type: str


class MessageBroker:
    def __init__(self):
        self._observers: dict[str, list[Observer]] = {}

    def subscribe(self, message_type: str, observer: Observer):
        observers = self._observers.setdefault(message_type, [])
        if observer not in observers:
            observers.append(observer)

    def unsubscribe(self, message_type: str, observer: Observer):
        """Detaching an observer that is not subscribed is a no-op."""
        observers = self._observers.get(message_type)

        if observers is None or observer not in observers:
            return

        observers.remove(observer)

        if not observers:
            del self._observers[message_type]  # don't accumulate empty buckets

    def notify(self, message: Message):
        # Iterate a snapshot: an observer may subscribe or unsubscribe from inside update() without disturbing the broadcast in progress.
        for observer in tuple(self._observers.get(message.message_type, ())):
            try:
                observer.update(message)
            except Exception as error:
                print(f"MessageBroker: {type(observer).__name__}.update failed: {error!r}")

    def publish(self, message: Message):
        print(f"MessageBroker: New message published: {message.content}")
        self.notify(message)


class EmailObserver:
    def update(self, message: Message):
        print(f"EmailObserver received: {message.content}")


class SMSObserver:
    def update(self, message: Message):
        print(f"SMSObserver received: {message.content}")


class PushNotificationObserver:
    def update(self, message: Message):
        print(f"PushNotificationObserver received: {message.content}")


class OneShotObserver:
    def __init__(self, publisher: Publisher, message_type: str):
        self._publisher = publisher
        self._message_type = message_type

    def update(self, message: Message):
        print(f"OneShotObserver received: {message.content} (and unsubscribes)")
        self._publisher.unsubscribe(self._message_type, self)


class BrokenObserver:
    """Always fails, to show that it cannot break the broadcast for the others."""

    def update(self, message: Message):
        raise RuntimeError("this observer is misconfigured")


if __name__ == "__main__":
    broker = MessageBroker()

    email_observer = EmailObserver()
    sms_observer = SMSObserver()
    push_observer = PushNotificationObserver()

    broker.subscribe("email", email_observer)
    broker.subscribe("sms", sms_observer)
    broker.subscribe("push", push_observer)
    broker.subscribe("email", sms_observer)  # one observer, several message types
    broker.subscribe("email", email_observer)  # duplicate subscription is ignored

    broker.publish(Message(content="You've got mail!", message_type="email"))
    broker.publish(Message(content="New SMS received!", message_type="sms"))
    broker.publish(Message(content="New push notification!", message_type="push"))

    broker.unsubscribe("sms", sms_observer)
    broker.unsubscribe("sms", sms_observer)  # detaching twice is harmless
    broker.publish(Message(content="Another SMS received!", message_type="sms"))
    broker.publish(Message(content="Another email received!", message_type="email"))

    # Publishing to a message type nobody subscribed to registers nothing.
    broker.publish(Message(content="Nobody is listening", message_type="webhook"))

    # An observer may detach itself mid-broadcast, and a failing one is contained.
    broker.subscribe("email", OneShotObserver(broker, "email"))
    broker.subscribe("email", BrokenObserver())
    broker.publish(Message(content="Broadcast to a changing observer list", message_type="email"))
    broker.publish(Message(content="The one-shot observer is gone now", message_type="email"))
