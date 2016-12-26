from django.core.urlresolvers import reverse
from django.test import TestCase

from django.contrib.auth import get_user_model

from ..models import Blog, Post, Section


class TestBlog(TestCase):

    def setUp(self):
        """
        Create default Sections and Posts.
        """
        blog = Blog.objects.first()
        apples = Section.objects.create(name="Apples", slug="apples")
        oranges = Section.objects.create(name="Oranges", slug="oranges")

        self.password = "eldarion"
        self.user = get_user_model().objects.create_user(
            username="patrick",
            password=self.password
        )
        self.user.save()

        # Create two published Posts, one in each section.
        self.orange_title = "Orange You Wonderful"
        self.orange_post = Post.objects.create(blog=blog,
                                               section=oranges,
                                               title=self.orange_title,
                                               slug=self.orange_title,
                                               author=self.user,
                                               state=Post.STATE_CHOICES[-1][0])

        self.apple_title = "Apple of My Eye"
        self.apple_post = Post.objects.create(blog=blog,
                                              section=apples,
                                              title=self.apple_title,
                                              slug=self.apple_title,
                                              author=self.user,
                                              state=Post.STATE_CHOICES[-1][0])


class TestViewGetSection(TestBlog):

    def test_invalid_section_slug(self):
        """
        Ensure invalid section slugs do not cause site crash.
        """
        invalid_slug = "bananas"
        url = reverse("pinax_blog:blog_section", kwargs={"section": invalid_slug})
        try:
            response = self.client.get(url)
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
