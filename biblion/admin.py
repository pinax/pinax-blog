from django.contrib import admin

from biblion.models import Post, Image
from biblion.utils import can_tweet


class ImageInline(admin.TabularInline):
    model = Image
    fields = ["image_path"]


class PostAdmin(admin.ModelAdmin):  
    list_display = ["title", "published", "section"]
    list_filter = ["section"]
    fields = [
        "section",
        "title",
        "slug",
        "author",
        "teaser_html",
        "content_html",
        "published",
    ]
    
    if can_tweet():
        fields.append("tweet")
    
    prepopulated_fields = {"slug": ("title",)}
    
    inlines = [
        ImageInline,
    ]

admin.site.register(Post, PostAdmin)
admin.site.register(Image)
