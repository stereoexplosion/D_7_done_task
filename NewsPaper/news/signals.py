from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import PostCategory, Author
from .tasks.basic import new_post_notify

@receiver(m2m_changed, sender=PostCategory)
def notification_post_created(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        new_post_notify(instance)

