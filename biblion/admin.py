from django.contrib import admin
from django.utils.functional import curry

from biblion.forms import AdminPostForm
from biblion.models import Post, Image, ReviewComment
from biblion.utils import can_tweet


class ImageInline(admin.TabularInline):
    model = Image
    fields = ["image_path"]


class ReviewInline(admin.TabularInline):
    model = ReviewComment


class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "published_flag", "section", "show_secret_share_url"]
    list_filter = ["section"]
    form = AdminPostForm
    fields = [
        "section",
        "title",
        "slug",
        "author",
        "markup",
        "teaser",
        "content",
        "description",
        "primary_image",
        "sharable_url",
        "publish",
    ]
    readonly_fields = ["sharable_url"]

    if can_tweet():
        fields.append("tweet")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        ImageInline,
        ReviewInline,
    ]

    def show_secret_share_url(self, obj):
        return '<a href="%s">%s</a>' % (obj.sharable_url, obj.sharable_url)
    show_secret_share_url.short_description = "Share this url"
    show_secret_share_url.allow_tags = True

    def published_flag(self, obj):
        return bool(obj.published)
    published_flag.short_description = "Published"
    published_flag.boolean = True

    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs.get("request")
        if db_field.name == "author":
            ff = super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            ff.initial = request.user.id
            return ff
        return super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update({
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        })
        return super(PostAdmin, self).get_form(request, obj, **kwargs)

    def save_form(self, request, form, change):
        # this is done for explicitness that we want form.save to commit
        # form.save doesn't take a commit kwarg for this reason
        return form.save()


admin.site.register(Post, PostAdmin)
admin.site.register(Image)
