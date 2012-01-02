from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

from docutils import nodes
from docutils.writers import html4css1
from docutils.core import publish_parts
from docutils.parsers.rst import directives

import markdown
import textile

from django.utils.safestring import mark_safe

from biblion.utils.mdx_codehilite import makeExtension
from biblion.utils import creole_parser


VARIANTS = {}


def pygments_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    try:
        lexer = get_lexer_by_name(arguments[0])
    except (ValueError, IndexError):
        # no lexer found - use the text one instead of an exception
        lexer = TextLexer()
    parsed = highlight(u"\n".join(content), lexer, HtmlFormatter())
    return [nodes.raw("", parsed, format="html")]
pygments_directive.arguments = (0, 1, False)
pygments_directive.content = 1
pygments_directive.options = dict([(key, directives.flag) for key in VARIANTS])

directives.register_directive("sourcecode", pygments_directive)


class HTMLWriter(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator


class HTMLTranslator(html4css1.HTMLTranslator):
    named_tags = []
    
    def visit_literal(self, node):
        # @@@ wrapping fixes.
        self.body.append("<code>%s</code>" % node.astext())
        raise nodes.SkipNode


def rst_to_html(value):
    parts = publish_parts(source=value, writer=HTMLWriter(),
        settings_overrides={"initial_header_level": 2})
    return parts["fragment"]


def markdown_to_html(text):
    """
    Convert markdown to HTML with code hiliting
    """
    return unicode(markdown.markdown(text, extensions=('codehilite',)))


def textile_to_html(text):
    """
    Convert textile to HTML
    @@@ add code hiliting support
    """
    return unicode(textile.textile(text))


def creole_to_html(text):
    """
    Convert creole to HTML
    @@@ add code hiliting support
    """
    return unicode(creole_parser.parse(text, emitter=creole_parser.BiblionHtmlEmitter))


def to_html(obj):
    """
    Markup filter that converts an object to html formatting.
    Syntax hiliting support for rst and markdown only.
    """
    if obj.markup_type == 1:  # HTML
        html = obj.content
    elif obj.markup_type == 2:  # Creole
        html = creole_to_html(obj.content)
    elif obj.markup_type == 3:  # Markdown
        html = markdown_to_html(obj.content)
    elif obj.markup_type == 4:  # reStructuredText
        html = rst_to_html(obj.content)
    elif obj.markup_type == 5:  # Textile
        html = textile_to_html(obj.content)
    return mark_safe(html)
