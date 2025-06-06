from django.contrib import admin

# Register your models here.
from .models import Category, NewsArticle, Like , SavedNews

admin.site.register(Category)
admin.site.register(NewsArticle)
admin.site.register(Like)
admin.site.register(SavedNews)
