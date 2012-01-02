from django.template.defaultfilters import slugify


def slugify_unique(value, model, slugfield="slug"):
    suffix = 0
    potential = base = slugify(value)
    while True:
        if suffix:
            potential = "-".join([base, str(suffix)])
        if not model.objects.filter(**{slugfield: potential}).count():
            print model.objects.filter(**{slugfield: potential})
            return potential
        suffix += 1
