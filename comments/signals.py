from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.models import Comment, Log


@receiver(post_save, sender=Comment)
def log_comment_saved(sender, instance, **kwargs):
    Log.objects.create(
        message=f"comment {instance.text} is saved"
    )
