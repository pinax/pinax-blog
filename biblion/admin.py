from django.contrib import admin

from biblion.models import Post, Image

class ImageInline(admin.TabularInline):
    model = Image
    fields = ["image_path"]


class PostAdmin(admin.ModelAdmin):  
    list_display = ["title", "published", "section"]
    list_filter = ["section"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        ImageInline,
    ]

admin.site.register(Post, PostAdmin)
admin.site.register(Image)
