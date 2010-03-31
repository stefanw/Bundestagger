from django.core.exceptions import PermissionDenied
from bundestagger.account.models import User

def get_user(request):
    if "bundesuser" in request.session:
        return request.session["bundesuser"]
    return None

def login(request, openid):
    try:
        user = User.objects.get(openid=openid)
    except User.DoesNotExist:
        user = User.objects.create(openid=openid, username="Nutzer")
        user.username = "%s%d" % (user.username,user.id)
        user.save()
    request.session["bundesuser"] = user
    return True
    
def logout(request):
    if "bundesuser" in request.session:
        del request.session["bundesuser"]
    if "openids" in request.session:
        del request.session["openids"]
    if "openid" in request.session:
        del request.session["openid"]

        
def logged_in(func):
    def loggedin_func(*args, **kwargs):
        request = args[0]
        if "bundesuser" in request.session:
            request.bundesuser = request.session["bundesuser"]
            return func(*args, **kwargs)
        raise PermissionDenied
    return loggedin_func