import re

from creole import Parser
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.util import ClassNotFound

from .models import Image


class Rules:
    # For the link targets:
    proto = r"http|https|ftp|nntp|news|mailto|telnet|file|irc"
    extern = r"(?P<extern_addr>(?P<extern_proto>{0}):.*)".format(proto)
    interwiki = r"""
            (?P<inter_wiki> [A-Z][a-zA-Z]+ ) :
            (?P<inter_page> .* )
    """


class HtmlEmitter(object):
    """
    Generate HTML output for the document
    tree consisting of DocNodes.
    """

    addr_re = re.compile(
        "|".join([Rules.extern, Rules.interwiki]),
        re.X | re.U
    )  # for addresses

    def __init__(self, root):
        self.root = root

    def get_text(self, node):
        """Try to emit whatever text is in the node."""
        try:
            return node.children[0].content or ""
        except:
            return node.content or ""

    def html_escape(self, text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def attr_escape(self, text):
        return self.html_escape(text).replace("\"", "&quot")

    # *_emit methods for emitting nodes of the document

    def document_emit(self, node):
        return self.emit_children(node)

    def text_emit(self, node):
        return self.html_escape(node.content)

    def separator_emit(self, node):
        return "<hr>"

    def paragraph_emit(self, node):
        return "<p>%s</p>\n" % self.emit_children(node)

    def bullet_list_emit(self, node):
        return "<ul>\n%s</ul>\n" % self.emit_children(node)

    def number_list_emit(self, node):
        return "<ol>\n%s</ol>\n" % self.emit_children(node)

    def list_item_emit(self, node):
        return "<li>%s</li>\n" % self.emit_children(node)

    def table_emit(self, node):
        return "<table>\n%s</table>\n" % self.emit_children(node)

    def table_row_emit(self, node):
        return "<tr>%s</tr>\n" % self.emit_children(node)

    def table_cell_emit(self, node):
        return "<td>%s</td>" % self.emit_children(node)

    def table_head_emit(self, node):
        return "<th>%s</th>" % self.emit_children(node)

    def emphasis_emit(self, node):
        return "<i>%s</i>" % self.emit_children(node)

    def strong_emit(self, node):
        return "<b>%s</b>" % self.emit_children(node)

    def header_emit(self, node):
        return "<h%d>%s</h%d>\n" % (
            node.level, self.html_escape(node.content), node.level)

    def code_emit(self, node):
        return "<tt>%s</tt>" % self.html_escape(node.content)

    def link_emit(self, node):
        target = node.content
        if node.children:
            inside = self.emit_children(node)
        else:
            inside = self.html_escape(target)
        m = self.addr_re.match(target)
        if m:
            if m.group("extern_addr"):
                return "<a href=\"%s\">%s</a>" % (
                    self.attr_escape(target), inside)
            elif m.group("inter_wiki"):
                raise NotImplementedError
        return "<a href=\"%s\">%s</a>" % (
            self.attr_escape(target), inside)

    def image_emit(self, node):
        target = node.content
        text = self.get_text(node)
        m = self.addr_re.match(target)
        if m:
            if m.group("extern_addr"):
                return "<img src=\"%s\" alt=\"%s\">" % (
                    self.attr_escape(target), self.attr_escape(text))
            elif m.group("inter_wiki"):
                raise NotImplementedError
        return "<img src=\"%s\" alt=\"%s\">" % (
            self.attr_escape(target), self.attr_escape(text))

    def macro_emit(self, node):
        raise NotImplementedError

    def break_emit(self, node):
        return "<br>"

    def preformatted_emit(self, node):
        return "<pre>%s</pre>" % self.html_escape(node.content)

    def default_emit(self, node):
        """Fallback function for emitting unknown nodes."""
        raise TypeError

    def emit_children(self, node):
        """Emit all the children of a node."""
        return "".join([self.emit_node(child) for child in node.children])

    def emit_node(self, node):
        """Emit a single node."""
        emit = getattr(self, "%s_emit" % node.kind, self.default_emit)
        return emit(node)

    def emit(self):
        """Emit the document represented by self.root DOM tree."""
        return self.emit_node(self.root)


class PygmentsHtmlEmitter(HtmlEmitter):

    def preformatted_emit(self, node):
        content = node.content
        lines = content.split("\n")
        if lines[0].startswith("#!code"):
            lexer_name = lines[0].split()[1]
            del lines[0]
        else:
            lexer_name = None
        content = "\n".join(lines)
        try:
            lexer = get_lexer_by_name(lexer_name)
        except ClassNotFound:
            lexer = TextLexer()
        return highlight(content, lexer, HtmlFormatter(cssclass="syntax")).strip()


class ImageLookupHtmlEmitter(HtmlEmitter):

    def image_emit(self, node):
        target = node.content
        if not re.match(r"^\d+$", target):
            return super(ImageLookupHtmlEmitter, self).image_emit(node)
        else:
            try:
                image = Image.objects.get(pk=int(target))
            except Image.DoesNotExist:
                # @@@ do something better here
                return ""
            return "<img src=\"%s\" />" % (image.image_path.url,)


class PinaxBlogHtmlEmitter(PygmentsHtmlEmitter, ImageLookupHtmlEmitter):
    pass


def parse(text, emitter=PinaxBlogHtmlEmitter):
    return emitter(Parser(text).parse()).emit()


def parse_with_highlighting(text, emitter=PygmentsHtmlEmitter):
    return parse(text, emitter=emitter)
