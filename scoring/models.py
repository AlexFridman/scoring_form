# coding=utf-8
from __future__ import unicode_literals

import os
import pickle

from django.core import validators
from django.db import models


class ScoringInfo(models.Model):
    application_id = models.CharField(max_length=50, primary_key=True)
    status_of_existing_checking_account = models.IntegerField(
        verbose_name='Статус текущего счета',
        choices=[
            (1, '... < 0 руб.'),
            (2, '0 <= ... < 200 руб.'),
            (3, '... >= 200 руб.'),
            (4, 'нет счета'),
        ]
    )
    duration_in_month = models.IntegerField(
        verbose_name='Срок в месяцах',
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(12 * 10),
        ]
    )
    credit_history = models.IntegerField(
        verbose_name='Кредитная история',
        choices=[
            (1, 'кредиты не брались / все кредиты погашены'),
            (2, 'все кредиты в нашем банке выплачивались своевременно'),
            (3, 'текущие кредиты выплачиваются вовремя'),
            (4, 'имели место несвоевременные выплаты в прошлом'),
            (5, 'критический аккаунт'),
        ]
    )
    purpose = models.IntegerField(
        verbose_name='Цель',
        choices=[
            (1, 'автомобиль (новый)'),
            (2, 'автомобиль (б/у)'),
            (3, 'мебель / оборудывание'),
            (4, 'радио / телевидение'),
            (5, 'бытовая техника'),
            (6, 'ремонт'),
            (7, 'образование'),
            (8, 'отпуск'),
            (9, 'переквалификация'),
            (10, 'бизнес'),
            (11, 'другое'),
        ]
    )
    credit_amount = models.IntegerField(
        verbose_name='Размер кредита (руб.)',
        validators=[validators.MinValueValidator(100), validators.MaxValueValidator(10 ** 7)]
    )
    savings_account = models.IntegerField(
        verbose_name='Текущий счет',
        choices=[
            (1, '... < 100 руб.'),
            (2, '100 <= ... < 500 руб.'),
            (3, '500 <= ... < 1000 руб.'),
            (4, '... > 1000 руб.'),
            (5, 'нет данных / нет аккаунта'),
        ]
    )
    present_employment_since = models.IntegerField(
        verbose_name='Время на текущем месте работы',
        choices=[
            (1, 'безработный'),
            (2, '... < 1 года'),
            (3, '1 <= ... < 4 года'),
            (4, '4 <= ... < 7 лет'),
            (5, '... >= 7 лет'),
        ]
    )
    installment_rate = models.IntegerField(
        verbose_name='Процент выплат от дохода',
        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(100)]
    )
    personal_status = models.IntegerField(
        verbose_name='Семейное положение и пол',
        choices=[
            (1, 'мужской, разведен'),
            (2, 'женский, разведена / замужем'),
            (3, 'мужской, холост'),
            (4, 'мужской, женат'),
            (5, 'женский, не замужем'),
        ]
    )
    other_debtors = models.IntegerField(
        verbose_name='Поручители',
        choices=[
            (1, 'нет'),
            (2, 'созаявитель'),
            (3, 'гарант'),
        ]
    )
    present_residence_since = models.IntegerField(
        verbose_name='Время проживания на текущем месте жительства (лет)',
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(100)]
    )
    property = models.IntegerField(
        verbose_name='Имущество',
        choices=[
            (1, 'недвижимость'),
            (2, 'страхование жизни'),
            (3, 'автомобиль'),
            (4, 'нет данных / нет имущества')
        ]
    )
    age = models.IntegerField(
        verbose_name='Возраст (лет)',
        validators=[validators.MinValueValidator(14), validators.MaxValueValidator(100)]
    )
    installment_plans = models.IntegerField(
        verbose_name='Другие рассрочки',
        choices=[
            (1, 'банк'),
            (2, 'магазин'),
            (3, 'нет')
        ]
    )
    housing = models.IntegerField(
        verbose_name='Жилье',
        choices=[
            (1, 'съемное'),
            (2, 'собственное'),
            (3, 'бесплатное')
        ]
    )
    number_of_existing_credits = models.IntegerField(
        verbose_name='Количество текущих кредитов в нашем банке',
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(10)]
    )
    job = models.IntegerField(
        verbose_name='Тип занятости',
        choices=[
            (1, 'безработный / неквалифицированный - нерезидент'),
            (2, 'неквалифицированный - резидент'),
            (3, 'квалифицированный'),
            (4, 'менеджмент / высококвалифицированный')
        ]
    )
    number_of_liable_people = models.IntegerField(
        verbose_name='Количество поручителей',
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(10)]
    )
    telephone = models.IntegerField(
        verbose_name='Телефон',
        choices=[
            (1, 'нет'),
            (2, 'есть')
        ]
    )
    foreign_worker = models.IntegerField(
        verbose_name='Иностранный работник',
        choices=[
            (1, 'да'),
            (2, 'нет')
        ]
    )
    repayment_prob = models.FloatField(blank=True)

    def _to_feature_vector(self):
        schema = [
            ('status_of_existing_checking_account', 4),
            ('duration_in_month', None),
            ('credit_history', 5),
            ('purpose', 11),
            ('credit_amount', None),
            ('savings_account', 5),
            ('present_employment_since', 5),
            ('installment_rate', None),
            ('personal_status', 5),
            ('other_debtors', 3),
            ('present_residence_since', None),
            ('property', 4),
            ('age', None),
            ('installment_plans', 3),
            ('housing', 3),
            ('number_of_existing_credits', None),
            ('job', 4),
            ('number_of_liable_people', None),
            ('telephone', 'b'),
            ('foreign_worker', 'b'),
        ]

        values = []

        for field_name, conf in schema:
            value = getattr(self, field_name)

            if conf is None:
                values.append(value)
            elif conf == 'b':
                values.append(value - 1)
            else:
                cat_value = [0] * conf
                cat_value[value - 1] = 1
                values.extend(cat_value)

        return values

    @staticmethod
    def _load_model():
        with open(os.environ['MODEL_PATH']) as f:
            return pickle.load(f)

    def _predict(self, x):
        model = self._load_model()
        return model.predict_proba(x)[0][0]

    def save(self, *args, **kwargs):
        x = self._to_feature_vector()
        self.repayment_prob = self._predict(x)
        super(ScoringInfo, self).save(*args, **kwargs)

    def to_kv(self):

        data = []
        for field in self._meta.get_fields():
            name = field.verbose_name
            if name not in {'application id', 'repayment prob'}:
                choices_reverse_map = dict(field.choices)
                value = getattr(self, field.attname)
                if choices_reverse_map:
                    value = choices_reverse_map[value]

                data.append((name, unicode(value)))

        return data
