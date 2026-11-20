from typing import Protocol


class Identifiable(Protocol):
    id: int

class BaseService[T: Identifiable]:
    def __init__(self) -> None:
        self.items: dict[int, T] = {}

    def list_items(self) -> list[T]:
        return list(self.items.values())
    
    def get_item(self, id: int) -> T:
        return self.items.get(id)
    
    def create_item(self, item: T) -> T:
        if item.id in self.items:
            raise ValueError(f"Item {item.id} already exists")

        self.items[item.id] = item
        return item