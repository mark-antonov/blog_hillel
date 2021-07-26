from random import randint

from blog.models import Comment, Post

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
# from django.contrib.auth.models import User as User
from django.core.management.base import BaseCommand

from faker import Faker

fake = Faker()
UserModel = get_user_model()


class Command(BaseCommand):
    help = 'This command is for inserting Comments and Post into database.' \
           'Insert 50 Users, 250 Posts, 1250 Comments.'  # noqa A003

    def handle(self, *args, **kwargs):
        # clear database
        Post.objects.all().delete()
        Comment.objects.all().delete()

        # create 50 users
        self.stdout.write('creating users')
        # for i in range(50):
        #     User.objects.create(username=fake.name(), password=make_password('password'), is_staff=0)
        objs = [
            UserModel(
                username=fake.name(),
                email=fake.email(),
                password=make_password('password'),
                is_staff=0
            )
            for _ in range(50)
        ]
        UserModel.objects.bulk_create(objs)

        # create up to 5 posts for each user
        self.stdout.write('creating posts')
        posts = []
        for user in UserModel.objects.all():
            for i in range(5):
                posts.append(Post(title=fake.sentence(nb_words=3), short_description=fake.sentence(nb_words=5),
                                  full_description=fake.text(), posted=randint(0, 1), author=user))
        Post.objects.bulk_create(posts)
        self.stdout.write('posts created')

        # add 5 comments to each post
        self.stdout.write('creating comments')
        comments = []
        for post in Post.objects.all():
            for i in range(5):
                comments.append(Comment(text=fake.sentence(nb_words=4), username=fake.name(), post=post,
                                        moderated=randint(0, 1)))
        Comment.objects.bulk_create(comments)
        self.stdout.write('comments created')

        self.stdout.write(self.style.SUCCESS('Successfully'))
