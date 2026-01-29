from dataclasses import dataclass, field


@dataclass
class ChecklistItem:
    id: int
    name: str
    status: str
    assignee: str
    notes: str
    parent_id: int | None = None
    indent: int = 0
    children: list["ChecklistItem"] = field(default_factory=list)


@dataclass
class ColumnMap:
    name: int
    status: int
    assignee: int
    notes: int
