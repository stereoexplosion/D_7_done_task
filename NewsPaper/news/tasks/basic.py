from django.contrib.auth.models import User
from django.core.mail.message import EmailMultiAlternatives

from ..models import Post


def new_post_notify(instance):
    for category in instance.post_category.all():
        user_emails = User.objects.filter(
        subscriptions__category=category).values_list('email', flat=True)
        subject = f'Новая публикация в вашей любимой категории {category}'
        text_content = (
            f'Заголовок: {instance.post_header}\n'
            f'Превью: {Post.preview(instance)}\n\n'
            f'Ссылка на публикацию: http://127.0.0.1:8000{instance.get_absolute_url()}'
        )
        html_content = (
            f'Заголовок: {instance.post_header}<br>'
            f'Превью: {Post.preview(instance)}<br><br>'
            f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
            f'Ссылка на публикацию</a>'
        )
        for email in user_emails:
            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()