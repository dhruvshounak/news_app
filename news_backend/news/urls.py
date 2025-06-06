from django.urls import path
from .views import fetch_news, fetch_top_news, fetch_categories, set_preferences,get_preferences, save_news, unsave_news, get_saved_news,get_news_by_category,summarized_article

urlpatterns = [
    path('news/', fetch_news, name='fetch_news'),
    path('categories/', fetch_categories, name='fetch_categories'),
    path('preferences/', set_preferences, name='set_preferences'),
    path('preferences/get/', get_preferences, name='get_preferences'),
    path('saved/', get_saved_news, name='get_saved_news'),
    path('save/', save_news, name='save_news'),
    path('unsave/', unsave_news, name='unsave_news'),
    path('top/', fetch_top_news, name='fetch_top_news'),
    path("api/news/<str:category>/", get_news_by_category, name="get-news-by-category"),
    path('summarized/<int:pk>/', summarized_article, name='summarized_article'),

    
]
