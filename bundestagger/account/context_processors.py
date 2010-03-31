from django.conf import settings

def openid(request):
    return {'openid': getattr(request, "openid", None)}
    
def user(request):
    if hasattr(request, "session"):
        return {'bundesuser': request.session.get("bundesuser", None)}
    
def next(request):
    return {'next': request.get_full_path()}
    
def domain(request):
    return {'SITE_DOMAIN': settings.SITE_DOMAIN}
