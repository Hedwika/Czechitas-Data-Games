import math

from django import forms
from web import models
from web.models import Assignment


class RightAnswer(forms.Form):
    answer = forms.CharField(max_length=200, label="",
                             widget=forms.TextInput(attrs={"class": "form-control"}))

    # TODO: Move this to a method
    # if Assignment.answer_type == 'SEZNAM':
    #     answer_form = answer_form.join(answer_form.split())
    #     answer_form = [answer_form]
    #     answer_form = answer_form.sort()
    #
    # elif Assignment.answer_type == 'ČÍSLO':
    #     def round_half_up(n, decimals=0):
    #         multiplier = 10 ** decimals
    #         return math.floor(n * multiplier + 0.5) / multiplier
    #     answer_form = round_half_up(answer_form , 2)
    #
    # else:
    #     answer_form = answer_form.lower()
    #     answer_form = answer_form.join(answer_form.split())

    def __init__(self, *args, **kwargs):
        self.right_answer = kwargs.pop("right_answer")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        answer = cleaned_data["answer"]

        if answer != self.right_answer:

            if Assignment.answer_type == 'SEZNAM':
                answer_form = answer.split()
                answer_form.sort()

                if answer.__hash__() != answer_form.__hash__():
                    raise forms.ValidationError("Špatná odpověď, zkus to prosím znovu.")

            elif Assignment.answer_type == 'ČÍSLO':

                def round_half_up(n, decimals=0):
                    multiplier = 10 ** decimals
                    return math.floor(n * multiplier + 0.5) / multiplier

                answer_form = round_half_up(answer, 2)

                if answer_form != answer:
                    raise forms.ValidationError("Špatná odpověď, zkus to prosím znovu.")

            elif Assignment.answer_type == 'TEXT':
                answer_form = answer.lower()

                if answer_form != answer:
                    raise forms.ValidationError("Špatná odpověď, zkus to prosím znovu.")

            raise forms.ValidationError("Špatná odpověď, zkus to prosím znovu.")
        return cleaned_data