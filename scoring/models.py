# coding=utf-8
from __future__ import unicode_literals

from django.core import validators
from django.db import models


class ScoringInfo(models.Model):
    status_of_existing_checking_account = models.IntegerField(
        verbose_name='Статус текущего счета',
        choices=[
            (0, '... < 0 руб.'),
            (1, '0 <= ... < 200 руб.'),
            (2, '... >= 200 руб.'),
            (3, 'нет счета'),
        ]
    )
    credit_history = models.IntegerField(
        verbose_name='Кредитная история',
        choices=[
            (0, 'кредиты не брались / все кредиты погашены'),
            (1, 'все кредиты в нашем банке выплачивались своевременно'),
            (2, 'текущие кредиты выплачиваются вовремя'),
            (3, 'имели место несвоевременные выплаты в прошлом'),
            (4, 'критический аккаунт'),
        ]
    )
    purpose = models.IntegerField(
        verbose_name='Цель',
        choices=[
            (0, 'автомобиль (новый)'),
            (1, 'автомобиль (б/у)'),
            (2, 'мебель / оборудывание'),
            (3, 'радио / телевидение'),
            (4, 'бытовая техника'),
            (5, 'ремонт'),
            (6, 'образование'),
            (7, 'отпуск'),
            (8, 'переквалификация'),
            (9, 'бизнес'),
            (10, 'другое'),
        ]
    )
    present_employment_since = models.IntegerField(
        verbose_name='Время на текущем месте работы',
        choices=[
            (0, 'безработный'),
            (1, '... < 1 года'),
            (2, '1 <= ... < 4 года'),
            (3, '4 <= ... < 7 лет'),
            (4, '... >= 7 лет'),
        ]
    )
    personal_status = models.IntegerField(
        verbose_name='Семейное положение и пол',
        choices=[
            (0, 'мужской, разведен'),
            (1, 'женский, разведена / замужем'),
            (2, 'мужской, холост'),
            (3, 'мужской, женат'),
            (4, 'женский, не замужем'),
        ]
    )
    other_debtors = models.IntegerField(
        verbose_name='Поручители',
        choices=[
            (0, 'нет'),
            (1, 'созаявитель'),
            (2, 'гарант'),
        ]
    )
    property = models.IntegerField(
        verbose_name='Имущество',
        choices=[
            (0, 'недвижимость'),
            (1, 'страхование жизни'),
            (2, 'автомобиль'),
            (3, 'нет данных / нет имущества')
        ]
    )
    installment_plans = models.IntegerField(
        verbose_name='Другие рассрочки',
        choices=[
            (0, 'банк'),
            (1, 'магазин'),
            (2, 'нет')
        ]
    )
    housing = models.IntegerField(
        verbose_name='Жилье',
        choices=[
            (0, 'съемное'),
            (1, 'собственное'),
            (2, 'бесплатное')
        ]
    )
    job = models.IntegerField(
        verbose_name='Тип занятости',
        choices=[
            (0, 'безработный / неквалифицированный - нерезидент'),
            (1, 'неквалифицированный - резидент'),
            (2, 'квалифицированный'),
            (3, 'менеджмент / высококвалифицированный')
        ]
    )
    telephone = models.IntegerField(
        verbose_name='Телефон',
        choices=[
            (0, 'нет'),
            (1, 'есть')
        ]
    )
    foreign_worker = models.IntegerField(
        verbose_name='Иностранный работник',
        choices=[
            (0, 'да'),
            (1, 'нет')
        ]
    )

    credit_amount = models.IntegerField()
    request_id = models.CharField(max_length=50)
    age = models.IntegerField()
    duration_in_month = models.IntegerField()

    def to_dict(self):
        schema = [
            ('age', None),
            ('credit_amount', None),
            ('credit_history', 5),
            ('duration_in_month', None),
            ('foreign_worker', 'b'),
            ('housing', 3),
            ('installment_plans', 3),
            ('job', 4),
            ('other_debtors', 3),
            ('personal_status', 5),
            ('present_employment_since', 5),
            ('property', 4),
            ('purpose', 11),
            ('status_of_existing_checking_account', 4),
            ('telephone', 'b')
        ]

        form = {}

        for field_name, conf in schema:
            form[field_name] = getattr(self, field_name)

        return form

    @classmethod
    def from_dict(cls, d):
        data = {}
        for f in cls._meta.get_fields():
            if f.attname != 'id':
                value = d[f.attname]
                if f.get_internal_type() == 'IntegerField':
                    value = int(value)
                data[f.attname] = value

        return cls(**data)

    def to_kv(self, show_special=False):
        special_fields = ['age', 'credit_amount', 'duration_in_month', 'request_id']
        data = []
        for field in self._meta.get_fields():
            if field.attname == 'id':
                continue

            if not show_special and field.attname in special_fields:
                continue

            name = field.verbose_name
            choices_reverse_map = dict(field.choices)
            value = getattr(self, field.attname)

            if choices_reverse_map:
                value = choices_reverse_map[value]

            data.append((name, str(value)))

        return data
