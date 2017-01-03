import logging

import requests
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from powerbank_bot.config import BotApi
from powerbank_bot.helpers.api_wrapper import ApiWrapper
from powerbank_bot.helpers.storage import Storage

from scoring.forms import ScoringForm
from scoring.models import ScoringInfo

logging.basicConfig(level=logging.DEBUG)


def decode_id(id):
    return id[32:]


class ScoringView(FormView):
    template_name = 'scoring_form.html'
    form_class = ScoringForm
    success_url = 'http://pb.somee.com/Request/ClientViewRequests'

    def get(self, request, *args, **kwargs):
        if 'id' not in request.GET:
            return HttpResponseBadRequest('A required argument id is not specified')
        request_id = decode_id(request.GET.get('id'))
        api = ApiWrapper()

        request = api.get_request_by_id(request_id)
        user = api.get_user_by_id(request.user_id)
        credit_type = api.get_credit_type_by_id(request.credit_type_id)

        if not all((request, user, credit_type)):
            return render(request, 'error.html', {'message': 'Произошла ошибка. Попробуйте позже'})

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        form.initial['request_id'] = request_id
        form.initial['credit_amount'] = request.amount
        form.initial['duration_in_month'] = credit_type.duration_in_month
        form.initial['age'] = user.age

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

    def form_valid(self, form):
        try:
            form = ScoringInfo.from_dict(form.data).to_dict()
            # TODO: assume bot api is running on the same machine
            form['result'] = requests.post('http://localhost:{port}/predict_proba'.format(port=BotApi.port),
                                           json=form).json()['prob']
            logging.debug(form)
        except Exception as e:
            logging.exception('Failed to get prediction')
            return render(self.request, 'error.html', {'message': 'Произошла ошибка. Попробуйте позже'})
        else:
            try:
                Storage().update_scoring_form(form)
            except:
                logging.exception('Failed to save form')
                return render(self.request, 'error.html', {'message': 'Произошла ошибка. Попробуйте позже'})
        return redirect(self.success_url)


def get_scoring_res(request):
    request_id = decode_id(request.GET.get('id'))

    form = Storage().get_scoring_form(request_id)
    if not form:
        return HttpResponseNotFound()

    return JsonResponse({'prob': form['result']})


def get(request):
    request_id = decode_id(request.GET.get('id'))

    form = Storage().get_scoring_form(request_id)

    if not form:
        return render(request, 'error.html', {'message': 'Не удалось открыть форму'})

    return render(request, 'view.html', context={'data': ScoringInfo.from_dict(form).to_kv()})
