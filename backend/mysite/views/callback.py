from django.shortcuts import render, redirect
from django.views import View

from mysite.forms.callback import CallbackForm


class CallbackCreate(View):
    template = 'site/main/main.html'
    raise_exception = True

    def get(self, request):
        form = CallbackForm
        return render(request, self.template, context={'form': form})

    def post(self, request):
        bound_form = CallbackForm(request.POST)
        if bound_form.is_valid():
            bound_form.save()
            return redirect('.')
        return render(request, self.template, context={'form': bound_form})
