# Usage

You work with this app as an author via the Django Admin.

You can [customize](customize-admin.md) the editor for the admin at the site
level or just use the stock text areas.

The `description` field in the admin represents the text that will be used in
different HTML META header tags that are useful for controlling the display
on social networks like Twitter and Facebook.

This is the same idea behind the `primary_image` field in the admin.


## Images

There are custom `markdown` and `creole` extensions for embedding images that
have been uploaded via the inline on the post create or edit form in the admin.

You first upload the image or images you want to use in the post by selecting
them in the file selector in the images section, and then hitting "Save and
Continue Editing". Once the form reloads, you'll see indicators above each
uploaded image with a number between two brackets, e.g. `{{ 25 }}`.

This is the syntax if you are using `creole` for adding that image to your
post. You can just copy and paste that.

If you are using `markdown` however, you will need to use the following
markup in your post:

    ![Alt Text](25)

or without alt text:

    ![](25)

Adjusting for the number of the image, of course.

