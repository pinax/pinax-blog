from django import forms
from django.utils import timezone
from django.utils.functional import curry

from .conf import settings
from .models import Post, Revision
from .utils import can_tweet, load_path_attr
from .signals import post_published


FIELDS = [
    "section",
    "author",
    "markup",
    "title",
    "slug",
    "teaser",
    "content",
    "description",
    "primary_image",
    "state",
]

if can_tweet():
    FIELDS.append("tweet")


class AdminPostForm(forms.ModelForm):

    title = forms.CharField(
        max_length=90,
        widget=forms.TextInput(attrs={"style": "width: 50%;"}),
    )
    slug = forms.CharField(
        widget=forms.TextInput(attrs={"style": "width: 50%;"})
    )
    teaser = forms.CharField(
        widget=forms.Textarea(attrs={"style": "width: 80%;"}),
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={"style": "width: 80%; height: 300px;"})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"style": "width: 80%;"}),
        required=False
    )
    if can_tweet():
        tweet = forms.BooleanField(
            required=False,
            help_text="Checking this will send out a tweet for this post",
        )

    class Meta:
        model = Post
        fields = FIELDS

    class Media:
        js = ("js/admin_post_form.js",)

    def __init__(self, *args, **kwargs):
        super(AdminPostForm, self).__init__(*args, **kwargs)

        post = self.instance

        # grab the latest revision of the Post instance
        latest_revision = post.latest()

        if latest_revision:
            # set initial data from the latest revision
            self.fields["teaser"].initial = latest_revision.teaser
            self.fields["content"].initial = latest_revision.content

    def save(self):
        published = False
        post = super(AdminPostForm, self).save(commit=False)

        if post.pk is None or Post.objects.filter(pk=post.pk, published=None).count():
            if self.cleaned_data["state"] == Post.STATE_CHOICES[-1][0]:
                post.published = timezone.now()
                published = True

        render_func = curry(
            load_path_attr(
                settings.PINAX_BLOG_MARKUP_CHOICE_MAP[self.cleaned_data["markup"]]["parser"]
            )
        )

        post.teaser_html = render_func(self.cleaned_data["teaser"])
        post.content_html = render_func(self.cleaned_data["content"])
        post.updated = timezone.now()
        post.save()

        r = Revision()
        r.post = post
        r.title = post.title
        r.teaser = self.cleaned_data["teaser"]
        r.content = self.cleaned_data["content"]
        r.author = post.author
        r.updated = post.updated
        r.published = post.published
        r.save()

        if can_tweet() and self.cleaned_data["tweet"]:
            post.tweet()

        if published:
            post_published.send(sender=Post, post=post)

        return post
