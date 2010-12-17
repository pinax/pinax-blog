from django.contrib import admin

from biblion.models import Post, Image
from biblion.utils import can_tweet


class ImageInline(admin.TabularInline):
    model = Image
    fields = ["image_path"]


class PostAdmin(admin.ModelAdmin):  
    list_display = ["title", "published_flag", "section"]
    list_filter = ["section"]
    fields = [
        "section",
        "title",
        "slug",
        "author",
        "teaser",
        "content",
        "publish",
    ]
    if can_tweet():
        fields.append("tweet")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        ImageInline,
    ]
    
    def published_flag(self, obj):
        return bool(obj.published)
    published_flag.short_description = "Published"
    published_flag.boolean = True


admin.site.register(Post, PostAdmin)
admin.site.register(Image)
