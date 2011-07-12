from datetime import datetime

from django import forms

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import curry

from biblion.models import Post, Revision
from biblion.settings import PARSER
from biblion.utils import can_tweet, load_path_attr


class AdminPostForm(forms.ModelForm):
    
    title = forms.CharField(
        max_length = 90,
        widget = forms.TextInput(
            attrs = {"style": "width: 50%;"},
        ),
    )
    slug = forms.CharField(
        widget = forms.TextInput(
            attrs = {"style": "width: 50%;"},
        )
    )
    teaser = forms.CharField(
        widget = forms.Textarea(
            attrs = {"style": "width: 80%;"},
        ),
    )
    content = forms.CharField(
        widget = forms.Textarea(
            attrs = {"style": "width: 80%; height: 300px;"},
        )
    )
    publish = forms.BooleanField(
        required = False,
        help_text = u"Checking this will publish this articles on the site",
    )
    
    if can_tweet():
        tweet = forms.BooleanField(
            required = False,
            help_text = u"Checking this will send out a tweet for this post",
        )
    
    class Meta:
        model = Post
    
    def __init__(self, *args, **kwargs):
        super(AdminPostForm, self).__init__(*args, **kwargs)
        
        post = self.instance
        
        # grab the latest revision of the Post instance
        latest_revision = post.latest()
        
        if latest_revision:
            # set initial data from the latest revision
            self.fields["teaser"].initial = latest_revision.teaser
            self.fields["content"].initial = latest_revision.content
        
            # @@@ can a post be unpublished then re-published? should be pulled
            # from latest revision maybe?
            self.fields["publish"].initial = bool(post.published)
        
    def save(self):
        post = super(AdminPostForm, self).save(commit=False)
        
        if post.pk is None:
            if self.cleaned_data["publish"]:
                post.published = datetime.now()
        else:
            if Post.objects.filter(pk=post.pk, published=None).count():
                if self.cleaned_data["publish"]:
                    post.published = datetime.now()
        
        render_func = curry(load_path_attr(PARSER[0], **PARSER[1]))
        
        post.teaser_html = render_func(self.cleaned_data["teaser"])
        post.content_html = render_func(self.cleaned_data["content"])
        post.updated = datetime.now()
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
        
        return post
