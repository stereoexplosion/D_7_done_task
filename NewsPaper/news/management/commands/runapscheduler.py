import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from ...models import Post, Subscription
from django.contrib.auth.models import User
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def my_job():
    posts = Post.objects.all()
    posts_apscheduler = posts.filter(post_create_time__gte=datetime.now() - timedelta(minutes=2880))
    users = Subscription.objects.all().values_list('user_id', flat=True).distinct()
    for user in users:
        category_sub = []
        posts_for_send = []
        user_email = User.objects.filter(id=user).values_list('email', flat=True)
        print(user_email)
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

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(minute="00", hour="18", day_of_week='fri'),
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")