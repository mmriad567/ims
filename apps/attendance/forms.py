from django import forms

from .models import ClassSession


class ClassSessionForm(forms.ModelForm):
    """Form to create a new class session for a specific subject."""

    class Meta:
        model = ClassSession
        fields = ['section', 'date', 'period_no']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded px-3 py-2'}),
        }

    def __init__(self, *args, subject=None, **kwargs):
        """Limit sections to the subject semester and use period choices."""
        super().__init__(*args, **kwargs)
        if subject:
            self.fields['section'].queryset = subject.semester.sections.all()
        self.fields['section'].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})
        self.fields['period_no'] = forms.ChoiceField(
            choices=[(i, f'Period {i}') for i in range(1, 8)],
            widget=forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
        )
