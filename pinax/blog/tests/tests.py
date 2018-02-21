from __future__ import absolute_import

import random

from django.core.exceptions import ValidationError
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.text import slugify

from test_plus import TestCase

from ..context_processors import scoped
from ..models import Blog, Post, Section

ascii_lowercase = "abcdefghijklmnopqrstuvwxyz"


def randomword(length):
    return "".join(random.choice(ascii_lowercase) for i in range(length))


class TestBlog(TestCase):

    def setUp(self):
        """
        Create default Sections and Posts.
        """
        self.blog = Blog.objects.first()
        self.apples = Section.objects.create(name="Apples", slug="apples")
        self.oranges = Section.objects.create(name="Oranges", slug="oranges")

        self.user = self.make_user("patrick")
        self.markup = "markdown"

        # Create two published Posts, one in each section.
        self.orange_title = "Orange You Wonderful"
        self.orange_slug = slugify(self.orange_title)
        self.orange_post = Post.objects.create(blog=self.blog,
                                               section=self.oranges,
                                               title=self.orange_title,
                                               slug=self.orange_slug,
                                               author=self.user,
                                               markup=self.markup,
                                               state=Post.STATE_CHOICES[-1][0])

        self.apple_title = "Apple of My Eye"
        self.apple_slug = slugify(self.apple_title)
        self.apple_post = Post.objects.create(blog=self.blog,
                                              section=self.apples,
                                              title=self.apple_title,
                                              slug=self.apple_slug,
                                              author=self.user,
                                              markup=self.markup,
                                              state=Post.STATE_CHOICES[-1][0])


class TestViewGetSection(TestBlog):

    def test_invalid_section_slug(self):
        """
        Ensure invalid section slugs do not cause site crash.
        """
        invalid_slug = "bananas"
        url = reverse("pinax_blog:blog_section", kwargs={"section": invalid_slug})
        try:
            response = self.get(url)
        except Section.DoesNotExist:
            self.fail("section '{}' does not exist".format(invalid_slug))
        self.assertEqual(response.status_code, 404)

    def test_valid_section_slug(self):
        """
        Verify that existing section slug works fine
        """
        valid_slug = "oranges"
        url = reverse("pinax_blog:blog_section", kwargs={"section": valid_slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestViewGetPosts(TestBlog):

    def test_section_posts(self):
        """
        Verify only the expected Post is in context for section "orange".
        """
        url = reverse("pinax_blog:blog_section", kwargs={"section": "oranges"})
        response = self.client.get(url)
        self.assertIn(self.orange_post, response.context_data["post_list"])
        self.assertNotIn(self.apple_post, response.context_data["post_list"])

    def test_all_posts(self):
        """
        Verify all Posts are in context for All.
        """
        url = reverse("pinax_blog:blog")
        response = self.client.get(url)
        self.assertEqual(response.context_data["post_list"].count(), 2)
        self.assertIn(self.orange_post, response.context_data["post_list"])
        self.assertIn(self.apple_post, response.context_data["post_list"])


class TestModelFieldValidation(TestBlog):

    def test_overlong_slug(self):
        title_len = Post._meta.get_field("title").max_length
        title = randomword(title_len)
        slug_len = Post._meta.get_field("slug").max_length
        slug = randomword(slug_len + 1)
        slug_post = Post(blog=self.blog,
                         section=self.apples,
                         title=title,
                         slug=slug,
                         author=self.user,
                         state=Post.STATE_CHOICES[-1][0])

        with self.assertRaises(ValidationError) as context_manager:
            slug_post.save()

        the_exception = context_manager.exception
        self.assertIn(
            "Ensure this value has at most {} characters (it has {})."
            .format(slug_len, len(slug)),
            the_exception.messages
        )


class TestContextProcessors(TestBlog):

    def test_no_resolver_match(self):
        """
        Ensure no problem when `request.resolver_match` is None
        """
        request = HttpRequest()
        self.assertEqual(request.resolver_match, None)
        result = scoped(request)
        self.assertEqual(result, {"scoper_lookup": ""})


class TestViews(TestBlog):

    def test_manage_post_create_get(self):
        """
        Ensure template with external URL references renders properly
        for user with proper credentials.
        """
        with self.login(self.user):
            response = self.client.get("pinax_blog:manage_post_create")
            self.assertEqual(response.status_code, 404)

        self.user.is_staff = True
        self.user.save()
        with self.login(self.user):
            self.get("pinax_blog:manage_post_create")
            self.response_200()
            self.assertTemplateUsed("pinax/blog/manage_post_create")
            pinax_images_upload_url = reverse("pinax_images:imageset_new_upload")
            self.assertResponseContains(pinax_images_upload_url, html=False)

    def test_manage_post_create_post(self):
        """
        Ensure template with external URL references renders properly
        for user with proper credentials.
        """
        self.user.is_staff = True
        self.user.save()
        post_title = "You'll never believe what happened next!"
        post_data = dict(
            section=self.apples.pk,
            title=post_title,
            teaser="teaser",
            content="content",
            description="description",
            state=Post.STATE_CHOICES[-1][0],
        )
        with self.login(self.user):
            self.post("pinax_blog:manage_post_create", data=post_data)
            self.assertRedirects(self.last_response, reverse("pinax_blog:manage_post_list"))
            self.assertTrue(Post.objects.get(title=post_title))
