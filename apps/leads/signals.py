from html import escape

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ContactRequest, TestDriveRequest
from .notifications import send_telegram


@receiver(post_save, sender=TestDriveRequest)
def notify_test_drive(sender, instance, created, **kwargs):
    if not created:
        return
    text = (
        "🚗 <b>Yangi test-drayv arizasi</b>\n"
        f"Model: {escape(str(instance.car or '—'))}\n"
        f"Mijoz: {escape(instance.full_name)}\n"
        f"Telefon: {instance.phone}\n"
        f"Sana: {instance.preferred_date:%d.%m.%Y}, {instance.get_time_slot_display()}"
    )
    if instance.comment:
        text += f"\nIzoh: {escape(instance.comment)}"
    transaction.on_commit(lambda: send_telegram(text))


@receiver(post_save, sender=ContactRequest)
def notify_contact(sender, instance, created, **kwargs):
    if not created:
        return
    text = (
        f"📩 <b>Yangi murojaat: {instance.get_topic_display()}</b>\n"
        f"Mijoz: {escape(instance.full_name)}\n"
        f"Telefon: {instance.phone}"
    )
    if instance.car:
        text += f"\nModel: {escape(str(instance.car))}"
    if instance.message:
        text += f"\nXabar: {escape(instance.message)}"
    transaction.on_commit(lambda: send_telegram(text))
