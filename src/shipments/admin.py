from django.contrib import admin

from shipments.models import Shipment, ShipmentEvent


class ShipmentEventInline(admin.TabularInline):
    model = ShipmentEvent
    fields = ("id", "status", "location", "note", "occurred_at")
    readonly_fields = ("id", "occurred_at")
    extra = 0
    show_change_link = True


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "origin", "destination", "created_at")
    list_filter = ("status",)
    list_per_page = 25
    search_fields = ("id", "origin", "destination")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("id",)}),
        ("Route", {"fields": ("origin", "destination")}),
        ("Details", {"fields": ("status",)}),
        ("Important Dates", {"fields": ("created_at", "updated_at")}),
    )
    inlines = (ShipmentEventInline,)


@admin.register(ShipmentEvent)
class ShipmentEventAdmin(admin.ModelAdmin):
    list_display = ("id", "shipment", "status", "location", "occurred_at")
    list_per_page = 25
    search_fields = ("id", "shipment__id")
    readonly_fields = ("id", "occurred_at")
    ordering = ("-occurred_at",)
    list_select_related = ("shipment",)
    fieldsets = (
        (None, {"fields": ("id",)}),
        ("Details", {"fields": ("status", "location", "note")}),
        ("Relations", {"fields": ("shipment",)}),
        ("Important Dates", {"fields": ("occurred_at",)}),
    )
