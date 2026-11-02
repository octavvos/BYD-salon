from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("test-drive/", views.TestDriveView.as_view(), name="test_drive"),
    path("contacts/", views.ContactView.as_view(), name="contacts"),
]
