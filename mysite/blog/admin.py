from django.contrib import admin
from . import models

@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status', 'author', 'publish', 'created']
    list_filter = ['title', 'status', 'author', 'publish', 'created']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)} # will automatically fill the slug when you enter the title field
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
