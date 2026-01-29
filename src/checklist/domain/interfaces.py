from abc import ABC, abstractmethod

from checklist.domain.types import ChecklistItem


class SheetProviderInterface(ABC):
    @abstractmethod
    def get_rows(self) -> list[ChecklistItem]:
        pass

    @abstractmethod
    def add_row(
        self,
        name: str,
        status: str,
        assignee: str,
        notes: str,
        parent_id: int | None = None,
    ) -> ChecklistItem:
        pass

    @abstractmethod
    def update_row(self, row_id: int, **fields) -> ChecklistItem:
        pass

    @abstractmethod
    def delete_row(self, row_id: int) -> None:
        pass

    @abstractmethod
    def move_row(self, row_id: int, parent_id: int | None) -> ChecklistItem:
        pass

    @abstractmethod
    def reorder_row(
        self, row_id: int, sibling_id: int, above: bool = True
    ) -> ChecklistItem:
        pass
