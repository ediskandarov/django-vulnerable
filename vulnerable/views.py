from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.views.generic import CreateView
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page

from .models import Upload


def CVE_2014_0472(request):
    if 'next' in request.GET:
        return redirect(request.GET['next'])

    template = r"""
       /\     /\
      {  `---'  }
      {  O   O  }  
    ~~|~   V   ~|~~  
       \  \|/  /   
        `-----'__
        /     \  `^\_
       {       }\ |\_\_   W
       |  \_/  |/ /  \_\_( )
        \__/  /(_E     \__/
          (  /
           MM
    """
    return HttpResponse(template)


@csrf_protect
@cache_page(60 * 10)
def CVE_2014_0473(request):
    if request.POST:
        return HttpResponse('BOOM!')
    return HttpResponse(unicode(csrf(request)['csrf_token']))


class UploadView(CreateView):
    model = Upload
    success_url = '/'


def xss(request):
    context = {'html': ('<script>'
                        'alert("all your base are belong to us")'
                        '</script>&h')}
    return render_to_response('vulnerable/xss.html', context)
