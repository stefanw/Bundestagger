import math
import urllib

from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed

class FakeRequest(object):
    def __init__(self, path, get_dict=None):
        self.path = path
        self.GET = get_dict or {}

def get_page(index, max_per_page):
    return int(math.ceil(float(index) / max_per_page))

def padd_zeros(num, padd_base=3):
    num = str(num)
    for k in range(padd_base-len(num)):
        num = "0"+num
    return num
    
def get_cache_key(request, prefix=''):
    cache_key = urllib.quote(request.path.encode("utf-8"))
    if request.GET:
        cache_key += "."+":".join(["%s:%s" % (k,v) for k,v in request.GET.items()])
    return prefix+cache_key

def invalidate_cache(path, *args):
    page = None
    if len(args)==2:
        index, max_per_page = args
        page = get_page(index, max_per_page)
    if page is not None and page != 1:
        request = FakeRequest(path, {"page": page})
    else:
        request = FakeRequest(path)
    cache.delete(get_cache_key(request))
        
def invalidate_cache_all_pages(path, highest, max_per_page):
    last = get_page(highest,max_per_page)
    request = FakeRequest(path)
    cache.delete(get_cache_key(request))
    for i in range(last-1)+2:
        request = FakeRequest(path, {"page": last})
        cache.delete(get_cache_key(request))
        
def is_method(method, func):
    def need_method_func(*args, **kwargs):
        request = args[0]
        if request.method == method:
            return func(*args, **kwargs)
        else:
            return HttpResponseNotAllowed([method])
    return need_method_func

def is_post(func):
    return is_method("POST", func)
    
def is_get(func):
    return is_method("GET", func)