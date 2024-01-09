from django import template
from allauth.socialaccount.models import SocialAccount

register = template.Library()

@register.filter
def get_picture(username):
    try:
        pic = SocialAccount.objects.filter(user_id=username.id)[0].extra_data['picture']
        return pic
    except:
        return 