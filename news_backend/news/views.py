from django.shortcuts import render

# Create your views here.
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from news.models import Category
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from .models import UserPreference, SavedNews, Category, NewsArticle
from .serializers import UserPreferenceSerializer, SavedNewsSerializer, NewsArticleSerializer
from django.shortcuts import get_object_or_404
from .summarizer import summarize_text
from newspaper import Article
from .tasks import summarize_article








@api_view(['GET'])
def fetch_news(request):
    category = request.GET.get('category', 'general')
    sort_by = request.GET.get('sort', 'published_at')
    page = request.GET.get("page", "1")  # Default sorting by date
    search_query = request.GET.get("search", "")

    params = {
        "api_token": settings.NEWS_API_KEY,
        "language": "en",
        "categories": category,
        "limit": 3,  
        "sort": sort_by,
        "page":page
    }
    if search_query:
    	params["search"]=search_query

    try:
        response = requests.get("https://api.thenewsapi.com/v1/news/all", params=params)
        response.raise_for_status()  # Raise an error if response is not 200 OK
        data=response.json()
        for article in data.get('data',[]):
            url = article.get('url')
            full_article_content = ""
            try:
                news_article = Article(url)
                news_article.download()
                news_article.parse()
                full_article_content = news_article.text
            except Exception as e:
                print(f"Failed to fetch full content for {url}: {e}")


            db_article,created=NewsArticle.objects.get_or_create(
                title=article.get('title'),
                defaults={
                    'content': article.get('description') or "No content provided.",
                    'source': article.get('source'),
                    'published_at': article.get('published_at'),
                    'category': Category.objects.get_or_create(name=category)[0],
                    'url': url,
                    'full_content': full_article_content,
                }

                )
            if created or not db_article.summary:
                print(f"Queuing summarization for article {db_article.id}")
                summarize_article.delay(db_article.id)

        return JsonResponse(response.json())

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)



	

#fetch available categories from the database
@api_view(['GET'])
def fetch_categories(request):
	categories = Category.objects.values_list('name',flat=True)
	return JsonResponse({"categories": list(categories)})

@api_view(['GET'])
def fetch_top_news(request):
    category = request.GET.get('category', '')  # Get category from request

    params = {
        "api_token": settings.NEWS_API_KEY,
        "language": "en",
        "limit": 3,  
        "categories": category  # Add category filter
    }

        
    

    try:
        response = requests.get("https://api.thenewsapi.com/v1/news/top", params=params)
        response.raise_for_status()  # Raises an error if the API fails
        data=response.json()
        for article in data.get('data', []):
            url = article.get('url')  # Define url here
            full_article_content = ""
            try:
                news_article = Article(url)
                news_article.download()
                news_article.parse()
                full_article_content = news_article.text
            except Exception as e:
                print(f"Failed to fetch full content for {url}: {e}")
            db_article,created = NewsArticle.objects.get_or_create(
                title=article.get('title'),
                defaults={
                    'content': article.get('description') or "No content provided.",
                    'source': article.get('source'),
                    'published_at': article.get('published_at'),
                    'category': Category.objects.get_or_create(name=category if category else "general")[0],
                    'url': article.get('url'),
                    'full_content': full_article_content,
                })
            if created or not db_article.summary:
                print(f"Queuing summarization for article {db_article.id}")
                summarize_article.delay(db_article.id)
        return JsonResponse(response.json())

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)









# Set User Preferences (POST request)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_preferences(request):
    user = request.user
    categories = request.data.get('categories', [])

    # Ensure UserPreference exists
    preference, created = UserPreference.objects.get_or_create(user=user)
    preference.categories.set(Category.objects.filter(id__in=categories))
    return Response({"message": "Preferences updated successfully!"})

# Get User Preferences (GET request)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_preferences(request):
    preference = UserPreference.objects.get(user=request.user)
    serializer = UserPreferenceSerializer(preference)
    return Response(serializer.data)






# Save a News Article (POST request)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_news(request):
    user = request.user
    data = request.data

    # Check if required fields are in the request data
    required_fields = ['article_url', 'article_title', 'article_source']
    for field in required_fields:
        if field not in data:
            return Response({"error": f"Missing required field: {field}"}, status=400)

    # Save the news article
    saved_news, created = SavedNews.objects.get_or_create(
        user=user,
        article_url=data['article_url'],
        defaults={
            'article_title': data['article_title'],
            'article_source': data['article_source']
        }
    )
    
    return Response({"message": "News saved!" if created else "Already saved!"})


# Unsave a News Article (DELETE request)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unsave_news(request):
    user = request.user
    article_url = request.data.get('article_url')

    deleted, _ = SavedNews.objects.filter(user=user, article_url=article_url).delete()
    return Response({"message": "News unsaved!" if deleted else "Article not found!"})



# Get User’s Saved News (GET request)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_news(request):
    saved_news = SavedNews.objects.filter(user=request.user)
    serializer = SavedNewsSerializer(saved_news, many=True)
    return Response(serializer.data)


def get_news_by_category(request, category):
    news_articles = NewsArticle.objects.filter(category__name=category)
    
    if not news_articles.exists():
        return JsonResponse({"error": "No news found for this category"}, status=404)

    data = list(news_articles.values("title", "content", "source", "published_at"))
    return JsonResponse({"data": data}, safe=False)



@api_view(['GET'])
def summarized_article(request, pk):

    article = get_object_or_404(NewsArticle, id=pk)
    text_to_summarize = article.full_content or article.content or ""
    summary = summarize_text(text_to_summarize)
    article.summary = summary
    article.save()
    return Response({
        'title': article.title,
        'summary': summary
    })














