from django.db import models

# Create your models here.
from django.contrib.auth.models import User
class Category (models.Model):
	name = models.CharField(max_length = 100, unique = True)
	def __str__(self):
		return self.name


class NewsArticle(models.Model):
	title = models.CharField(max_length=255)
	content = models.TextField()
	source = models.CharField(max_length=100)
	published_at = models.DateTimeField()
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True )
	url = models.URLField(unique=True, null=True, blank=True)  # New — to check for duplicates
	summary = models.TextField(blank=True, null=True)  # New — for summarization result
	full_content = models.TextField(blank=True, null=True)  # New field for actual article text
	def __str__(self):
		return self.title

class Like(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	article_url = models.URLField()
	article_title = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	class Meta:
		unique_together = ('user','article_url')

	def __str__(self):
		return f"{self.user.username} liked {self.article_title}"
class UserPreference(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	categories = models.ManyToManyField('Category')

	def __str__(self):
		return f"{self.user.username}'s preferences"



class SavedNews(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	article_url = models.URLField()
	article_title=models.CharField(max_length=255)
	article_source= models.CharField(max_length = 100)
	saved_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('user','article_url')
	def __str__(self):
		return f"{self.user.username} saved {self.article_title}"

