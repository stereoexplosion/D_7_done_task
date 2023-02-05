from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum

class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    author_rating = models.IntegerField(default=0)

    def update_rating(self):
        postRAT = self.post_set.aggregate(post_rating=Sum('rating'))
        pRat = 0
        pRat += postRAT.get('post_rating')

        commentRAT = self.author.comment_set.aggregate(comm_rating=Sum('rating'))
        cRat = 0
        cRat += commentRAT.get('comm_rating')

        self.author_rating = pRat * 3 + cRat
        self.save()

    def __str__(self):
        return self.author.username


class Category(models.Model):
    category_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.category_name


class Post(models.Model):
    news = 'NE'
    article = 'AR'
    POSITIONS = [
        (news, 'Новость'),
        (article, 'Статья'),
    ]
    author_post = models.ForeignKey(Author, on_delete=models.CASCADE)
    type_choice = models.CharField(max_length=2, choices=POSITIONS, default=news)
    post_create_time = models.DateTimeField(auto_now_add=True)
    post_category = models.ManyToManyField(Category, through='PostCategory')
    post_header = models.CharField(max_length=128)
    post_text = models.TextField()
    post_rating = models.IntegerField(default=0)

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        return self.post_text[0:123] + '...'

    def __str__(self):
        return self.post_header

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comm_create_time = models.DateTimeField(auto_now_add=True)
    comm_rating = models.IntegerField(default=0)

    def like(self):
        self.comm_rating += 1
        self.save()

    def dislike(self):
        self.comm_rating -= 1
        self.save()
