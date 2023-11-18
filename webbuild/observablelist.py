from typing import Callable, Any


class ObservableList(list):
    def __init__(self, on_length_change: Callable[[int], Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_length_change = on_length_change

    def notify_length_change(self) -> None:
        self.on_length_change(len(self))

    def append(self, item) -> None:
        super().append(item)
        self.notify_length_change()

    def extend(self, items) -> None:
        super().extend(items)
        self.notify_length_change()

    def insert(self, index, item) -> None:
        super().insert(index, item)
        self.notify_length_change()

    def pop(self, index: int = -1) -> Any:
        item = super().pop(index)
        self.notify_length_change()
        return item

    def remove(self, value) -> None:
        super().remove(value)
        self.notify_length_change()

    def clear(self) -> None:
        super().clear()
        self.notify_length_change()
