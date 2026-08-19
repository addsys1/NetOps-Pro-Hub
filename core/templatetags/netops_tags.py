from django import template
from django.utils.safestring import mark_safe
import bleach

register = template.Library()

BLEACH_ALLOWED_TAGS = [
    'h1','h2','h3','h4','h5','h6','p','ul','ol','li','strong','em','b','i',
    'a','pre','code','blockquote','br','hr','table','thead','tbody','tr','th','td',
    'img','span','div','dl','dt','dd','sup','sub','small','mark',
]
BLEACH_ALLOWED_ATTRS = {
    '*':   ['class', 'id'],
    'a':   ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'td':  ['colspan', 'rowspan'],
    'th':  ['colspan', 'rowspan'],
}


@register.filter
def safe_html(value):
    if not value:
        return ''
    cleaned = bleach.clean(value, tags=BLEACH_ALLOWED_TAGS, attributes=BLEACH_ALLOWED_ATTRS, strip=True)
    return mark_safe(cleaned)


@register.filter
def get_module_concepts(concept):
    from concepts.models import NetworkConcept
    return NetworkConcept.objects.filter(module_number=concept.module_number).order_by('order')


@register.filter
def difficulty_badge(value):
    return {
        'beginner': 'success',
        'intermediate': 'warning',
        'advanced': 'danger',
        'expert': 'dark',
    }.get(value, 'secondary')


@register.filter
def criticality_badge(value):
    return {
        'low': 'success',
        'medium': 'info',
        'high': 'warning',
        'critical': 'danger',
    }.get(value, 'secondary')


@register.filter
def criticality_icon(value):
    return {
        'low': 'bi-thermometer-low',
        'medium': 'bi-thermometer-half',
        'high': 'bi-thermometer-high',
        'critical': 'bi-exclamation-octagon-fill',
    }.get(value, 'bi-thermometer-half')


@register.filter
def vendor_icon(value):
    return {
        'cisco': 'bi-hdd-network',
        'fortinet': 'bi-shield-fill',
        'paloalto': 'bi-fire',
        'juniper': 'bi-cpu',
        'aruba': 'bi-wifi',
        'generic': 'bi-gear',
    }.get(value, 'bi-hdd-network')


@register.filter
def platform_badge(value):
    return {
        'ios': 'primary',
        'ios-xe': 'info',
        'nx-os': 'purple',
        'asa': 'warning',
        'fortios': 'danger',
        'junos': 'teal',
        'generic': 'secondary',
    }.get(value, 'secondary')


@register.filter
def status_badge(value):
    return {
        'published': 'success',
        'draft': 'secondary',
        'review': 'warning',
        'deprecated': 'danger',
    }.get(value, 'secondary')
