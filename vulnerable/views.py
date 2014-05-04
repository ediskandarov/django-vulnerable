from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse


def CVE_2014_0472(request):
    if 'next' in request.GET:
        next_url = redirect(request.GET['next'])
    else:
        next_url = '/success/'

    template = """\
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

    next URL %s
    """
    content = template % (next_url,)
    return HttpResponse(content)
