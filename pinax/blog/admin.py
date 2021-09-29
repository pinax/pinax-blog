from functools import partial as curry

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pinax.images.admin import ImageInline
from pinax.images.models import ImageSet

from .conf import settings
from .forms import AdminPostForm
from .models import Blog, Post, ReviewComment, Section


class PostImageSet(ImageSet):
    class Meta:
        proxy = True


class ReviewInline(admin.TabularInline):
    model = ReviewComment


def make_published(modeladmin, request, queryset):
    queryset = queryset.exclude(state=Post.STATE_CHOICES[-1][0], published__isnull=False)
    queryset.update(state=Post.STATE_CHOICES[-1][0])
    queryset.filter(published__isnull=True).update(published=timezone.now())


make_published.short_description = _("Publish selected posts")


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
        "sharable_url",
        "state",
        "published",
        "image_set"  # maybe this https://github.com/anziem/django_reverse_admin
    ]
    readonly_fields = ["sharable_url"]

    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        ReviewInline,
    ]

    def show_secret_share_url(self, obj):
        return '<a href="{}">{}</a>'.format(obj.sharable_url, obj.sharable_url)
    show_secret_share_url.short_description = _("Share this url")
    show_secret_share_url.allow_tags = True

    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs.get("request")
        if db_field.name == "author":
            ff = super().formfield_for_dbfield(db_field, **kwargs)
            ff.initial = request.user.id
            return ff
        return super().formfield_for_dbfield(db_field, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update({
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        })
        return super().get_form(request, obj, **kwargs)

    def save_form(self, request, form, change):
        # this is done for explicitness that we want form.save to commit
        # form.save doesn't take a commit kwarg for this reason
        return form.save(Blog.objects.first() if not settings.PINAX_BLOG_SCOPING_MODEL else None)


if settings.PINAX_BLOG_SCOPING_MODEL:
    PostAdmin.fields.insert(0, "blog")
    PostAdmin.list_filter.append("blog__scoper")


class SectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Post, PostAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(
    PostImageSet,
    list_display=["blog_post", "primary_image", "created_by", "created_at"],
    raw_id_fields=["created_by"],
    inlines=[ImageInline],
)
