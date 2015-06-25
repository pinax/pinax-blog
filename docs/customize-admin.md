# Customize Admin

Customizing the admin functionality can be as complex as overriding the `ModelAdmin`
and `ModelForm` that ships with `pinax-blog` or as simple as just overriding
the `admin/blog/post/change_form.html` template.

Here is an example of an actual customization to use the [ACE Editor](http://ace.c9.io/) for
teaser and body content:

    {% extends "admin/change_form.html" %}
    {% load i18n admin_urls %}
    {% block extrahead %}
        {{ block.super }}
        <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/ace/1.1.8/ace.js"></script>
        <script>
        $(function () {
            var contentDiv = $("<div>").attr("id", "content-editor"),
                teaserDiv = $("<div>").attr("id", "teaser-editor"),
                setupEditor = function (editor, textarea) {
                    editor.setTheme("ace/theme/twilight");
                    editor.getSession().setMode("ace/mode/markdown");
                    editor.getSession().setValue(textarea.val());
                    editor.getSession().setUseWrapMode(true);
                    editor.getSession().on('change', function(){
                      textarea.val(editor.getSession().getValue());
                    });
                    editor.getSession().setTabSize(4);
                    editor.getSession().setUseSoftTabs(true);
                };
            $(".field-content div").append(contentDiv);
            $(".field-teaser div").append(teaserDiv);
            var editor1 = ace.edit("content-editor");
            var editor2 = ace.edit("teaser-editor");
            var textarea1 = $('textarea[name="content"]').hide();
            var textarea2 = $('textarea[name="teaser"]').hide();
            setupEditor(editor1, textarea1);
            setupEditor(editor2, textarea2);
        });
        </script>
        <style type="text/css" media="screen">
        #content-editor {
            min-height: 300px;
            width: 80%;
            min-width: 800px;
        }
        #teaser-editor {
            min-height: 100px;
            width: 80%;
            min-width: 800px;
        }
    </style>
    {% endblock %}
