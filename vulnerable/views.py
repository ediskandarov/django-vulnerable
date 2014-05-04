from django.http import HttpResponse
from django.shortcuts import redirect


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
