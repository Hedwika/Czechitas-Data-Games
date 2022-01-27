import math
from datetime import datetime

from django import forms
from web import models
from web.models import Assignment, Team

class NewTeam(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]

    name = forms.CharField(
        required=False,
        label='Jméno týmu',
    )

    def clean_name(self):
        name = self.cleaned_data.get("name")
        qs = Team.objects.filter(name__iexact=name, event=models.Event.objects.filter(end__lt=datetime.now()).first())
        if len(name) <= 1:
            raise forms.ValidationError("Jméno týmu musí mít více než jeden znak.")
        if qs.exists():
            raise forms.ValidationError("Tento tým už existuje, vyberte si prosím jiné jméno týmu.")
        return name

class RightAnswer(forms.Form):
    answer = forms.CharField(max_length=200, label="",
                             widget=forms.TextInput(attrs={"class": "form-control"}))

    assignment: models.Assignment

    def __init__(self, *args, **kwargs):
        self.assignment = kwargs.pop("assignment")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.assignment.answer_type == 'SEZNAM':
            right_answer = list(map(lambda x: x.strip(), self.assignment.right_answer.split(",")))
            answer = cleaned_data["answer"]
            if "," not in answer:
                raise forms.ValidationError("Odpověď musí být seznam a musí obsahovat alespoň dvě "
                                            "hodnoty oddělené čárkou.")
            answer = list(map(lambda x: x.strip(), answer.split(",")))
            if not set(right_answer) == set(answer):
                raise forms.ValidationError("Špatná odpověď, zkus to prosím znovu.")
        elif self.assignment.answer_type == 'ČÍSLO':
            right_answer = float(self.assignment.right_answer)
            answer = cleaned_data["answer"]
            if "," in answer:
                raise forms.ValidationError("Je třeba používat desetinnou tečku, nikoli desetinnou čárku.")
            elif not answer.replace('.', '', 1).isdigit():
                raise forms.ValidationError("Odpověď musí být číslo!")
            else:
                answer = float(cleaned_data["answer"])
            if round(answer, 2) != round(right_answer, 2):
                raise forms.ValidationError("Špatná odpověď, zkus to prosím znovu.")
        else:
            if cleaned_data["answer"] != self.assignment.right_answer:
                raise forms.ValidationError("Špatná odpověď, zkus to prosím znovu.")
        return cleaned_data