from django.contrib import admin
from django.utils import timezone
from django.utils.functional import curry

from .forms import AdminPostForm
from .models import Post, Image, ReviewComment, Section
from .utils import can_tweet


class ImageInline(admin.TabularInline):
    model = Image
    fields = ["image_path"]


class ReviewInline(admin.TabularInline):
    model = ReviewComment


def make_published(modeladmin, request, queryset):
    queryset = queryset.exclude(state=Post.STATE_CHOICES[-1][0], published__isnull=False)
    queryset.update(state=Post.STATE_CHOICES[-1][0])
    queryset.filter(published__isnull=True).update(published=timezone.now())
make_published.short_description = "Publish selected posts"


class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "state", "section", "published", "show_secret_share_url"]
    list_filter = ["section", "state"]
    form = AdminPostForm
    actions = [make_published]
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
        "state"
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


class SectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Post, PostAdmin)
admin.site.register(Image)
admin.site.register(Section, SectionAdmin)
