from django import template
from django.template.defaultfilters import stringfilter, linebreaks_filter
from django.utils.safestring import mark_safe
from django.conf import settings
from bleach.sanitizer import Cleaner
import mistune

register = template.Library()
cleaner = Cleaner(
    tags=[
        "a",
        "abbr",
        "acronym",
        "b",
        "blockquote",
        "code",
        "em",
        "i",
        "li",
        "ol",
        "strong",
        "ul",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "hr",
        "pre",
        "img",
    ],
    attributes={
        "a": ["href", "title"],
        "img": ["alt", "src", "title"],
        "abbr": ["title"],
        "acronym": ["title"],
    },
)


@register.filter()
@stringfilter
def format_text(text):
    if settings.RICH_TEXT_ENABLED:
        return parse_markdown(text)
    else:
        return linebreaks_filter(text)


def parse_markdown(text):
    md = mistune.create_markdown()
    html = md(text)
    sanitized = cleaner.clean(html)
    return mark_safe(sanitized)
