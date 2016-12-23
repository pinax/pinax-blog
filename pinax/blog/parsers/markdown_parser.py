from markdown import Markdown
from markdown.inlinepatterns import ImagePattern, IMAGE_LINK_RE

from pinax.images.models import Image


class ImageLookupImagePattern(ImagePattern):

    def sanitize_url(self, url):
        if url.startswith("http"):
            return url
        else:
            try:
                image = Image.objects.get(pk=int(url))
                return image.image.url
            except Image.DoesNotExist:
                pass
            except ValueError:
                return url
        return ""


def parse(text):
    md = Markdown(extensions=["codehilite", "tables", "smarty", "admonition", "toc", "fenced_code"])
    md.inlinePatterns["image_link"] = ImageLookupImagePattern(IMAGE_LINK_RE, md)
    html = md.convert(text)
    return html
