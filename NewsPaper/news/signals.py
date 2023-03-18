from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import PostCategory
from .tasks import new_post_notify

@receiver(m2m_changed, sender=PostCategory)
def notification_post_created(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        for category in instance.post_category.all():
            user_emails = list(User.objects.filter(
                subscriptions__category=category).values_list('email', flat=True))
        category = str(category)
        print(instance.preview(), instance.pk, instance.post_header, user_emails, category)
        new_post_notify.delay(instance.preview(), instance.pk, instance.post_header, user_emails, category)

