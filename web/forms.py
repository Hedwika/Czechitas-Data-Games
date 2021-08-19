from django import forms
from web import models
from web.models import Assignment


class RightAnswer(forms.Form):
    answer = forms.CharField(max_length=200, label="Tvoje odpověď",
                             widget=forms.TextInput(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        self.right_answer = kwargs.pop("right_answer")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["answer"] != self.right_answer:
            raise forms.ValidationError("Špatná odpověď, zkus to prosím znovu.")
        return cleaned_data