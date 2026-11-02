from django.contrib import admin

from .models import ContactRequest, LeadStatus, TestDriveRequest


@admin.action(description="Holat: Jarayonda")
def mark_in_progress(modeladmin, request, queryset):
    queryset.update(status=LeadStatus.IN_PROGRESS)


@admin.action(description="Holat: Yakunlangan")
def mark_done(modeladmin, request, queryset):
    queryset.update(status=LeadStatus.DONE)


class BaseLeadAdmin(admin.ModelAdmin):
    list_editable = ["status"]
    search_fields = ["full_name", "phone"]
    readonly_fields = ["created_at"]
    actions = [mark_in_progress, mark_done]
    date_hierarchy = "created_at"
    list_per_page = 30


@admin.register(TestDriveRequest)
class TestDriveRequestAdmin(BaseLeadAdmin):
    list_display = ["full_name", "phone", "car", "preferred_date", "time_slot", "status", "created_at"]
    list_filter = ["status", "car", "time_slot", "preferred_date"]
    autocomplete_fields = ["car"]


@admin.register(ContactRequest)
class ContactRequestAdmin(BaseLeadAdmin):
    list_display = ["full_name", "phone", "topic", "car", "status", "created_at"]
    list_filter = ["status", "topic"]
    autocomplete_fields = ["car"]
