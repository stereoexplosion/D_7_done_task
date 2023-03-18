from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from .models import Post, Subscription
from django.contrib.auth.models import User
from datetime import datetime, timedelta

@shared_task
def new_post_notify(preview, pk, post_header, user_emails, category):
    subject = f'Новая публикация в вашей любимой категории {category}'
    text_content = (
        f'Заголовок: {post_header}\n'
        f'Превью: {preview}\n\n'
        f'Ссылка на публикацию: http://127.0.0.1:8000/posts/{pk}'
    )
    html_content = (
        f'Заголовок: {post_header}<br>'
        f'Превью: {preview}<br><br>'
        f'<a href="http://127.0.0.1:8000/posts/{pk}">'
        f'Ссылка на публикацию</a>'
    )
    for email in user_emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

@shared_task
def weekly_subscribers_email():
    posts = Post.objects.all()
    posts_apscheduler = posts.filter(post_create_time__gte=datetime.now() - timedelta(minutes=60*24*7))
    users = Subscription.objects.all().values_list('user_id', flat=True).distinct()
    for user in users:
        category_sub = []
        posts_for_send = []
        user_email = User.objects.filter(id=user).values_list('email', flat=True)
        for category in Subscription.objects.filter(user=user).values_list('category', flat=True):
            category_sub.append(category)
        for post in posts_apscheduler:
            for category_p in post.post_category.all():
                if category_p.id in category_sub:
                    posts_for_send.append(post)
        subject = f'За последнюю неделю в ваших любимых категориях вышли следующие публикации:'
        text_content = ''
        html_content = ''
        for publication in posts_for_send:
            text_content_que = (
                f'Заголовок: {publication.post_header}\n'
                f'Превью: {Post.preview(publication)}\n'
                f'Ссылка на публикацию: http://127.0.0.1:8000{publication.get_absolute_url()}\n\n'
            )
            text_content += text_content_que
            html_content_que = (
                f'Заголовок: {publication.post_header}<br>'
                f'Превью: {Post.preview(publication)}<br>'
                f'<a href="http://127.0.0.1:8000{publication.get_absolute_url()}">'
                f'Ссылка на публикацию</a><br><br>'
            )
            html_content += html_content_que
        for email in user_email:
            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
