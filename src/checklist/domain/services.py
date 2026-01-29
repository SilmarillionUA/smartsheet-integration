from checklist.domain.types import ChecklistItem


class TreeBuilder:
    @staticmethod
    def build(items: list[ChecklistItem]) -> list[ChecklistItem]:
        """Build tree from flat list in single pass."""
        items_by_id = {}
        roots = []

        for item in items:
            item.children = []
            items_by_id[item.id] = item

        for item in items:
            if item.parent_id and item.parent_id in items_by_id:
                items_by_id[item.parent_id].children.append(item)
            else:
                roots.append(item)

        return roots

    @staticmethod
    def find_previous_sibling(
        items: list[ChecklistItem], row_id: int
    ) -> ChecklistItem | None:
        """Find sibling directly above target in single pass."""
        items_by_id = {item.id: item for item in items}
        target = items_by_id.get(row_id)
        if not target:
            return None

        prev = None
        for item in items:
            if item.parent_id == target.parent_id:
                if item.id == row_id:
                    return prev
                prev = item
        return None

    @staticmethod
    def find_next_sibling(
        items: list[ChecklistItem], row_id: int
    ) -> ChecklistItem | None:
        """Find sibling directly below target in single pass."""
        items_by_id = {item.id: item for item in items}
        target = items_by_id.get(row_id)
        if not target:
            return None

        found = False
        for item in items:
            if item.parent_id == target.parent_id:
                if found:
                    return item
                if item.id == row_id:
                    found = True
        return None

    @staticmethod
    def find_parent(
        items: list[ChecklistItem], row_id: int
    ) -> ChecklistItem | None:
        """Find parent of target using dict lookup."""
        items_by_id = {item.id: item for item in items}
        target = items_by_id.get(row_id)
        if not target or not target.parent_id:
            return None
        return items_by_id.get(target.parent_id)
