import logging
from functools import lru_cache

import smartsheet
from checklist.domain.interfaces import SheetProviderInterface
from checklist.domain.types import ChecklistItem, ColumnMap

logger = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def get_smartsheet_client(token: str) -> smartsheet.Smartsheet:
    """For session caching purposes"""
    client = smartsheet.Smartsheet(token)
    client.errors_as_exceptions(True)
    return client


SHEET_COLUMNS = [
    {"title": "Task Name", "type": "TEXT_NUMBER", "primary": True},
    {
        "title": "Status",
        "type": "PICKLIST",
        "options": ["Not Started", "In Progress", "Complete"],
    },
    {"title": "Assignee", "type": "TEXT_NUMBER"},
    {"title": "Notes", "type": "TEXT_NUMBER"},
]


class SmartsheetGateway(SheetProviderInterface):
    def __init__(self, token: str, sheet_id: int):
        self.client = get_smartsheet_client(token)
        self.sheet_id = sheet_id
        self._column_map: ColumnMap | None = None

    @classmethod
    def create_sheet(cls, token: str, name: str) -> int:
        client = get_smartsheet_client(token)

        columns = []
        for col in SHEET_COLUMNS:
            column = smartsheet.models.Column()
            column.title = col["title"]
            column.type = col["type"]
            column.primary = col.get("primary", False)
            if col.get("options"):
                column.options = col["options"]
            columns.append(column)

        sheet = smartsheet.models.Sheet()
        sheet.name = name
        sheet.columns = columns

        response = client.Home.create_sheet(sheet)
        logger.info(
            "Created Smartsheet sheet: %s (id=%s)", name, response.result.id
        )
        return response.result.id

    def _get_column_map(self) -> ColumnMap:
        if self._column_map:
            return self._column_map

        sheet = self.client.Sheets.get_sheet(self.sheet_id)
        col_map = {}
        for col in sheet.columns:
            col_map[col.title] = col.id

        self._column_map = ColumnMap(
            name=col_map.get("Task Name", 0),
            status=col_map.get("Status", 0),
            assignee=col_map.get("Assignee", 0),
            notes=col_map.get("Notes", 0),
        )
        return self._column_map

    def _row_to_item(self, row) -> ChecklistItem:
        col_map = self._get_column_map()
        cells = {cell.column_id: cell.value for cell in row.cells}

        return ChecklistItem(
            id=row.id,
            name=cells.get(col_map.name, "") or "",
            status=cells.get(col_map.status, "") or "",
            assignee=cells.get(col_map.assignee, "") or "",
            notes=cells.get(col_map.notes, "") or "",
            parent_id=row.parent_id,
            indent=row.indent or 0,
        )

    def get_rows(self) -> list[ChecklistItem]:
        logger.debug("Fetching rows from sheet %s", self.sheet_id)
        sheet = self.client.Sheets.get_sheet(self.sheet_id)
        logger.debug(
            "Fetched %d rows from sheet %s", len(sheet.rows), self.sheet_id
        )
        return [self._row_to_item(row) for row in sheet.rows]

    def add_row(
        self,
        name: str,
        status: str,
        assignee: str,
        notes: str,
        parent_id: int | None = None,
    ) -> ChecklistItem:
        col_map = self._get_column_map()

        row = smartsheet.models.Row()
        row.to_bottom = True
        if parent_id:
            row.parent_id = parent_id

        row.cells = [
            {"column_id": col_map.name, "value": name},
            {"column_id": col_map.status, "value": status},
            {"column_id": col_map.assignee, "value": assignee},
            {"column_id": col_map.notes, "value": notes},
        ]

        response = self.client.Sheets.add_rows(self.sheet_id, [row])
        logger.info("Added row to sheet %s: %s", self.sheet_id, name)
        return self._row_to_item(response.result[0])

    def update_row(self, row_id: int, **fields) -> ChecklistItem:
        col_map = self._get_column_map()

        row = smartsheet.models.Row()
        row.id = row_id

        cells = []
        if "name" in fields:
            cells.append({"column_id": col_map.name, "value": fields["name"]})
        if "status" in fields:
            cells.append(
                {"column_id": col_map.status, "value": fields["status"]}
            )
        if "assignee" in fields:
            cells.append(
                {"column_id": col_map.assignee, "value": fields["assignee"]}
            )
        if "notes" in fields:
            cells.append(
                {"column_id": col_map.notes, "value": fields["notes"]}
            )

        if cells:
            row.cells = cells
            response = self.client.Sheets.update_rows(self.sheet_id, [row])
            return self._row_to_item(response.result[0])

        sheet = self.client.Sheets.get_sheet(self.sheet_id, row_ids=[row_id])
        return self._row_to_item(sheet.rows[0])

    def delete_row(self, row_id: int) -> None:
        self.client.Sheets.delete_rows(self.sheet_id, [row_id])
        logger.info("Deleted row %s from sheet %s", row_id, self.sheet_id)

    def reorder_row(
        self, row_id: int, sibling_id: int, above: bool = True
    ) -> ChecklistItem:
        row = smartsheet.models.Row()
        row.id = row_id
        row.sibling_id = sibling_id
        if above:
            row.above = True

        response = self.client.Sheets.update_rows(self.sheet_id, [row])
        return self._row_to_item(response.result[0])

    def move_row(self, row_id: int, parent_id: int | None) -> ChecklistItem:
        row = smartsheet.models.Row()
        row.id = row_id
        if parent_id:
            row.parent_id = parent_id
        else:
            row.to_top = True

        response = self.client.Sheets.update_rows(self.sheet_id, [row])
        return self._row_to_item(response.result[0])
