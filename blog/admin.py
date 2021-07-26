from django.contrib import admin
from django.utils import timezone

from .models import Comment, Post


def make_posted(modeladmin, request, queryset):
    queryset.update(posted=True, published_date=timezone.now())
make_posted.short_description = "Mark selected posts as moderated"  # noqa:E305


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 3


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'title', 'short_description', 'created_date', 'published_date',
                    'posted']
    fields = ['author', 'title', 'short_description', 'full_description', ('created_date', 'published_date'), 'posted']
    list_filter = ['author', 'posted']
    search_fields = ['title']
    date_hierarchy = "published_date"
    inlines = [CommentInline]
    list_per_page = 10
    actions = [make_posted]


def make_moderated(modeladmin, request, queryset):
    queryset.update(moderated=True)
make_moderated.short_description = "Mark selected comments as moderated"  # noqa:E305


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['username', 'text', 'post', 'moderated']
    fields = ['username', 'text', 'post', 'moderated']
    list_filter = ['moderated', 'username']
    search_fields = ['text']
    actions = [make_moderated]
    ordering = ['moderated']
