from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    short_description = models.CharField(max_length=250)
    full_description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/%Y/%m/%d/', blank=True, null=True) # noqa DJ01
    # image = models.URLField(max_length=400)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    posted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-published_date',)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class Comment(models.Model):
    username = models.CharField(max_length=250)
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    moderated = models.BooleanField(default=False)

    def __str__(self):
        return self.text
