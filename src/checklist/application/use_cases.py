from dataclasses import dataclass

from checklist.domain.interfaces import SheetProviderInterface
from checklist.domain.services import TreeBuilder
from checklist.domain.types import ChecklistItem


@dataclass
class CreateItemInput:
    name: str
    status: str = "Not Started"
    assignee: str = ""
    notes: str = ""
    parent_id: int | None = None


@dataclass
class UpdateItemInput:
    name: str | None = None
    status: str | None = None
    assignee: str | None = None
    notes: str | None = None


class GetChecklist:
    def __init__(self, provider: SheetProviderInterface):
        self.provider = provider

    def execute(self) -> list[ChecklistItem]:
        items = self.provider.get_rows()
        return TreeBuilder.build(items)


class AddItem:
    def __init__(self, provider: SheetProviderInterface):
        self.provider = provider

    def execute(self, data: CreateItemInput) -> list[ChecklistItem]:
        self.provider.add_row(
            name=data.name,
            status=data.status,
            assignee=data.assignee,
            notes=data.notes,
            parent_id=data.parent_id,
        )
        return GetChecklist(self.provider).execute()


class UpdateItem:
    def __init__(self, provider: SheetProviderInterface):
        self.provider = provider

    def execute(
        self, row_id: int, data: UpdateItemInput
    ) -> list[ChecklistItem]:
        fields = {k: v for k, v in vars(data).items() if v is not None}
        if fields:
            self.provider.update_row(row_id, **fields)
        return GetChecklist(self.provider).execute()


class DeleteItem:
    def __init__(self, provider: SheetProviderInterface):
        self.provider = provider

    def execute(self, row_id: int) -> list[ChecklistItem]:
        self.provider.delete_row(row_id)
        return GetChecklist(self.provider).execute()


class IndentItem:
    def __init__(self, provider: SheetProviderInterface):
        self.provider = provider

    def execute(self, row_id: int) -> list[ChecklistItem]:
        items = self.provider.get_rows()
        sibling = TreeBuilder.find_previous_sibling(items, row_id)
        if not sibling:
            raise ValueError("Cannot indent: no sibling above")
        self.provider.move_row(row_id, parent_id=sibling.id)
        return GetChecklist(self.provider).execute()


class MoveItemUp:
    def __init__(self, provider: SheetProviderInterface):
        self.provider = provider

    def execute(self, row_id: int) -> list[ChecklistItem]:
        items = self.provider.get_rows()
        sibling = TreeBuilder.find_previous_sibling(items, row_id)
        if not sibling:
            raise ValueError("Cannot move up: already at the top")
        self.provider.reorder_row(row_id, sibling_id=sibling.id, above=True)
        return GetChecklist(self.provider).execute()


class MoveItemDown:
    def __init__(self, provider: SheetProviderInterface):
        self.provider = provider

    def execute(self, row_id: int) -> list[ChecklistItem]:
        items = self.provider.get_rows()
        sibling = TreeBuilder.find_next_sibling(items, row_id)
        if not sibling:
            raise ValueError("Cannot move down: already at the bottom")
        self.provider.reorder_row(row_id, sibling_id=sibling.id, above=False)
        return GetChecklist(self.provider).execute()


class OutdentItem:
    def __init__(self, provider: SheetProviderInterface):
        self.provider = provider

    def execute(self, row_id: int) -> list[ChecklistItem]:
        items = self.provider.get_rows()
        parent = TreeBuilder.find_parent(items, row_id)
        if not parent:
            raise ValueError("Cannot outdent: already at top level")
        grandparent = TreeBuilder.find_parent(items, parent.id)
        new_parent_id = grandparent.id if grandparent else None
        self.provider.move_row(row_id, parent_id=new_parent_id)
        return GetChecklist(self.provider).execute()
