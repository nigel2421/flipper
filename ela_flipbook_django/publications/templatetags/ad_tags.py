# publications/templatetags/ad_tags.py

from django import template
from django.utils.safestring import mark_safe
from publications.models import AdUnit, HouseAd
import random

register = template.Library()

@register.inclusion_tag('publications/partials/_ad_unit.html', takes_context=True)
def render_ad(context, slot_name):
    """
    Renders a GAM ad unit if active, else falls back to a random active House Ad for that slot.
    """
    try:
        ad_unit = AdUnit.objects.get(slot_name=slot_name, is_active=True)
        house_ads = ad_unit.house_ads.filter(is_active=True)
        fallback_ad = random.choice(house_ads) if house_ads.exists() else None
        
        return {
            'ad_unit': ad_unit,
            'fallback_ad': fallback_ad,
            'request': context.get('request'),
        }
    except AdUnit.DoesNotExist:
        return {'ad_unit': None}
