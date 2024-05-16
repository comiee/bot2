from webpage.comm.View import View
from django.shortcuts import render
from django.http import HttpResponseRedirect


class Index(View):
    url = ''

    def post(self, request):
        if 'qq' not in request.session:
            return HttpResponseRedirect('/login')
        return render(request, 'index.html')
