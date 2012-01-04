import datetime

from django import forms

from django.core.exceptions import ImproperlyConfigured

from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from biblion.models import Biblion, Post, Revision, Image
from biblion.signals import post_published
from biblion.utils.twitter import can_tweet
from biblion.utils.slugify import slugify_unique


class BiblionForm(forms.ModelForm):
    
    contributors = forms.ModelMultipleChoiceField(queryset=User.objects.none())
    
    class Meta:
        model = Biblion
        exclude = ("slug",)
    
    def __init__(self, *args, **kwargs):
        super(BiblionForm, self).__init__(*args, **kwargs)
        
        self.fields["contributors"].queryset = self.contributor_queryset()
        self.fields["contributors"].initial = self.instance.biblioncontributor_set.values_list("user", flat=True)
    
    def contributor_queryset(self):
        return User.objects.all()
    
    def save(self, commit=True):
        if not self.instance.slug:
            self.instance.slug = slugify_unique(self.cleaned_data["title"], self.Meta.model)
        instance = super(BiblionForm, self).save(commit=commit)
        if not commit:
            raise NotImplementedError("commit=False is not supported")
        self.save_contributors(instance)
        return instance
    
    def save_contributors(self, instance):
        instance.biblioncontributor_set.all().delete()
        for user in self.cleaned_data["contributors"]:
            instance.biblioncontributor_set.create(user=user)


class ImageForm(forms.ModelForm):
    
    class Meta:
        model = Image
        exclude = ["post", "url"]


class PostForm(forms.ModelForm):
    
    title = forms.CharField(
        max_length = 90,
        widget = forms.TextInput(),
    )
    teaser = forms.CharField(
        widget = forms.Textarea(),
    )
    content = forms.CharField(
        widget = forms.Textarea()
    )
    publish = forms.BooleanField(
        required = False,
        help_text = u"Checking this will publish this article on the site",
    )
    publish_date = forms.DateTimeField(
        required = False,
        help_text = u"Posts will not appear on the site until the publish date.",
    )
    
    if can_tweet():
        tweet = forms.BooleanField(
            required = False,
            help_text = u"Checking this will send out a tweet for this post",
        )
    
    class Meta:
        model = Post
        exclude = ("slug",)
    
    def __init__(self, *args, **kwargs):
        
        biblion = kwargs.pop("biblion")
        user = kwargs.pop("user")
        
        super(PostForm, self).__init__(*args, **kwargs)
        
        self.fields["author"].initial = user
        self.fields["author"].widget = forms.HiddenInput()
        
        # filter sites this post can appear based on what sites are selected
        # for the biblion
        self.fields["sites"].queryset = biblion.sites.all()
        
        post = self.instance
        
        self.fields["biblion"].initial = biblion
        
        # grab the latest revision of the Post instance
        latest_revision = post.latest()
        
        if latest_revision:
            # set initial data from the latest revision
            self.fields["teaser"].initial = latest_revision.teaser
            self.fields["content"].initial = latest_revision.content
            
            # @@@ can a post be unpublished then re-published? should be pulled
            # from latest revision maybe?
            self.fields["publish"].initial = bool(post.published)
            self.fields["publish_date"].initial = post.published
            # @@@ remove it for now when editing
            if self.instance is not None:
                del self.fields["publish"]
                del self.fields["publish_date"]
    
    def save(self):
        post = super(PostForm, self).save(commit=False)
        
        if not post.slug:
            post.slug = slugify_unique(self.cleaned_data["title"], self.Meta.model)
        
        if post.pk is None:
            if self.cleaned_data["publish"]:
                post.published = datetime.datetime.now()
        else:
            if Post.objects.filter(pk=post.pk, published=None).count():
                if self.cleaned_data["publish"]:
                    post.published = datetime.datetime.now()
        
        if self.cleaned_data["publish_date"]:
            post.published = self.cleaned_data["publish_date"]
        
        post.teaser = self.cleaned_data["teaser"]
        post.content = self.cleaned_data["content"]
        post.updated = datetime.datetime.now()
        post.save()
        
        post.sites = self.cleaned_data["sites"]
        
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
    publish_date = forms.DateTimeField(
        required = False,
        help_text = u"Posts will not appear on the site until the publish date."
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
            self.fields["markup_type"].initial = latest_revision.markup_type
            self.fields["teaser"].initial = latest_revision.teaser
            self.fields["content"].initial = latest_revision.content
            
            # @@@ can a post be unpublished then re-published? should be pulled
            # from latest revision maybe?
            self.fields["publish"].initial = bool(post.published)
            self.fields["publish_date"].initial = post.published
    
    def save(self):
        post = super(AdminPostForm, self).save(commit=False)
        # only publish the first time publish has been checked
        if (post.pk is None or Post.objects.filter(pk=post.pk, published=None).count()) and self.cleaned_data["publish"]:
            post.published = datetime.datetime.now()
            send_published_signal = True
        
        if self.cleaned_data["publish_date"]:
            post.published = self.cleaned_data["publish_date"]
        
        post.markup_type = self.cleaned_data["markup_type"]
        post.teaser = self.cleaned_data["teaser"]
        post.content = self.cleaned_data["content"]
        post.updated = datetime.datetime.now()
        post.save()
        
        if send_published_signal:
            post_published.send(sender=self, pk=post.pk)
        
        r = Revision()
        r.post = post
        r.title = post.title
        r.markup_type = self.cleaned_data["markup_type"]
        r.teaser = self.cleaned_data["teaser"]
        r.content = self.cleaned_data["content"]
        r.author = post.author
        r.updated = post.updated
        r.published = post.published
        r.save()
        
        if can_tweet() and self.cleaned_data["tweet"]:
            post.tweet()
        
        return post
