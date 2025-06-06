from rest_framework import serializers
from .models import UserPreference, SavedNews, NewsArticle

# User Preferences Serializer
class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['categories']

# Saved News Serializer
class SavedNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedNews
        fields = ['id', 'article_url', 'article_title', 'article_source', 'saved_at']
class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle  #Ensure this is the correct model
        fields = ["id", "title", "content", "published_at", "source", "category"]  # ✅ Include necessary fields