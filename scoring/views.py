from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.edit import FormView

from scoring.forms import ScoringForm
from scoring.models import ScoringInfo


class ScoringView(FormView):
    template_name = 'scoring_form.html'
    form_class = ScoringForm
    success_url = 'http://pb.somee.com/Request/ClientViewRequests'

    def get(self, request, *args, **kwargs):
        if 'id' not in request.GET:
            return HttpResponseBadRequest('A required argument id is not specified')
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.initial['application_id'] = request.GET.get('id')
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

    def form_valid(self, form):
        form.save()
        return super(ScoringView, self).form_valid(form)


def get_scoring_res(request):
    id_ = request.GET.get('id')

    if id_ is None:
        return HttpResponseBadRequest('A required argument id is not specified')

    scoring_info = ScoringInfo.objects.filter(application_id=id_).first()
    if scoring_info is None:
        return HttpResponseNotFound()

    return JsonResponse({'prob': scoring_info.repayment_prob, 'prob_dummy': scoring_info.repayment_dummy_prob})


def get(request):
    id_ = request.GET.get('id')

    if id_ is None:
        return HttpResponseBadRequest('A required argument id is not specified')

    scoring_info = ScoringInfo.objects.filter(application_id=id_).first()

    if scoring_info is None:
        return HttpResponseNotFound()

    return render(request, 'view.html', context={'data': scoring_info.to_kv()})


def copy(request):
    src, dst = request.GET.get('src_id'), request.GET.get('dst_id')

    scoring_info = ScoringInfo.objects.filter(application_id=src).first()

    if scoring_info is None:
        return HttpResponseNotFound()

    scoring_info.application_id = dst
    scoring_info.save()
    return HttpResponse(status=200)
