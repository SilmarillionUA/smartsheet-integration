from django.urls import path

from core.views import IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login/", IndexView.as_view(), name="login"),
    path("register/", IndexView.as_view(), name="register"),
    path("sheets/", IndexView.as_view(), name="sheets"),
    path(
        "sheets/<uuid:sheet_uuid>/", IndexView.as_view(), name="sheet-detail"
    ),
]
