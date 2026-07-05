from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = [
            "rating",
            "comment",
        ]

        from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = [
            "rating",
            "comment",
        ]

        widgets = {
            "rating": forms.Select(attrs={"class": "form-select",}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Write your review...",}),
        }

    def clean_comment(self):

        comment = self.cleaned_data["comment"]

        if len(comment.strip()) < 10:

            raise forms.ValidationError(
                "Review must contain at least 10 characters."
            )

        return comment

        