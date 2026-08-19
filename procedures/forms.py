from django import forms
from .models import (
    Procedure, ProcedureCategory,
    VendorChoices, DeviceTypeChoices, DifficultyChoices, PlatformChoices,
)


class ProcedureFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher une procédure...',
            'autocomplete': 'off',
        })
    )
    category = forms.ModelChoiceField(
        queryset=ProcedureCategory.objects.all(),
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vendor = forms.ChoiceField(
        choices=[('', 'Tous les vendors')] + list(VendorChoices.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    platform = forms.ChoiceField(
        choices=[('', 'Toutes les plateformes')] + list(PlatformChoices.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    device_type = forms.ChoiceField(
        choices=[('', 'Tous les équipements')] + list(DeviceTypeChoices.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    difficulty = forms.ChoiceField(
        choices=[('', 'Tous les niveaux')] + list(DifficultyChoices.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class DynamicProcedureForm(forms.Form):
    """
    Formulaire généré dynamiquement depuis les ProcedureVariable.
    Supporte les types text, number, ip, subnet, vlan, interface, select.
    """

    def __init__(self, *args, variables=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not variables:
            return

        for var in variables:
            field_kwargs = {
                'label': var.label,
                'required': var.required,
                'initial': var.default_value or None,
                'help_text': var.help_text or None,
            }

            widget_attrs = {'class': 'form-control', 'autocomplete': 'off'}
            if var.placeholder:
                widget_attrs['placeholder'] = var.placeholder

            if var.field_type == 'number':
                field = forms.IntegerField(**field_kwargs)
                field.widget = forms.NumberInput(attrs=widget_attrs)

            elif var.field_type == 'select' and var.select_options:
                options = [(o.strip(), o.strip()) for o in var.select_options.split(',') if o.strip()]
                field = forms.ChoiceField(
                    choices=[('', '— Sélectionner —')] + options,
                    **field_kwargs
                )
                field.widget = forms.Select(attrs={'class': 'form-select'})

            elif var.field_type == 'ip':
                field = forms.GenericIPAddressField(**field_kwargs)
                field.widget = forms.TextInput(attrs={**widget_attrs, 'placeholder': var.placeholder or '192.168.1.1'})

            else:
                field = forms.CharField(**field_kwargs)
                field.widget = forms.TextInput(attrs=widget_attrs)

            self.fields[var.name] = field
