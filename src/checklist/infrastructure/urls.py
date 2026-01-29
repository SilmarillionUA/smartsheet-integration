from django.urls import path

from checklist.infrastructure import views

app_name = "checklist"

urlpatterns = [
    path("sheets/", views.SheetListView.as_view(), name="sheet-list"),
    path(
        "sheets/<uuid:sheet_uuid>/",
        views.SheetDetailView.as_view(),
        name="sheet-detail",
    ),
    path(
        "sheets/<uuid:sheet_uuid>/items/",
        views.ChecklistView.as_view(),
        name="item-list",
    ),
    path(
        "sheets/<uuid:sheet_uuid>/items/create/",
        views.ItemCreateView.as_view(),
        name="item-create",
    ),
    path(
        "sheets/<uuid:sheet_uuid>/items/<int:row_id>/",
        views.ItemDetailView.as_view(),
        name="item-detail",
    ),
    path(
        "sheets/<uuid:sheet_uuid>/items/<int:row_id>/indent/",
        views.ItemIndentView.as_view(),
        name="item-indent",
    ),
    path(
        "sheets/<uuid:sheet_uuid>/items/<int:row_id>/outdent/",
        views.ItemOutdentView.as_view(),
        name="item-outdent",
    ),
    path(
        "sheets/<uuid:sheet_uuid>/items/<int:row_id>/move-up/",
        views.ItemMoveUpView.as_view(),
        name="item-move-up",
    ),
    path(
        "sheets/<uuid:sheet_uuid>/items/<int:row_id>/move-down/",
        views.ItemMoveDownView.as_view(),
        name="item-move-down",
    ),
]
