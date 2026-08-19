from django.views.generic import ListView, DetailView, FormView
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Procedure, ProcedureCategory, CheckTypeChoices
from .forms import ProcedureFilterForm, DynamicProcedureForm
from .renderer import render_command_template


class ProcedureListView(ListView):
    model = Procedure
    template_name = 'procedures/procedure_list.html'
    context_object_name = 'procedures'
    paginate_by = 12

    def get_queryset(self):
        qs = Procedure.objects.filter(status='published').select_related('category')
        form = ProcedureFilterForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            category = form.cleaned_data.get('category')
            vendor = form.cleaned_data.get('vendor')
            platform = form.cleaned_data.get('platform')
            device_type = form.cleaned_data.get('device_type')
            difficulty = form.cleaned_data.get('difficulty')
            if q:
                qs = qs.filter(
                    Q(title__icontains=q) | Q(summary__icontains=q) | Q(objective__icontains=q)
                )
            if category:
                qs = qs.filter(category=category)
            if vendor:
                qs = qs.filter(vendor=vendor)
            if platform:
                qs = qs.filter(platform=platform)
            if device_type:
                qs = qs.filter(device_type=device_type)
            if difficulty:
                qs = qs.filter(difficulty=difficulty)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = ProcedureFilterForm(self.request.GET)
        ctx['categories'] = ProcedureCategory.objects.all()
        # self.object_list is already the evaluated queryset — no second DB hit
        ctx['total_results'] = self.object_list.count()
        return ctx


class ProcedureDetailView(DetailView):
    model = Procedure
    template_name = 'procedures/procedure_detail.html'
    context_object_name = 'procedure'
    slug_field = 'slug'

    def get_queryset(self):
        return (
            Procedure.objects
            .filter(status='published')
            .prefetch_related('variables', 'steps', 'checks')
            .select_related('category')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        p = self.object
        ctx['pre_checks'] = p.checks.filter(check_type=CheckTypeChoices.PRE).order_by('order')
        ctx['post_checks'] = p.checks.filter(check_type=CheckTypeChoices.POST).order_by('order')
        ctx['validations'] = p.checks.filter(check_type=CheckTypeChoices.VALIDATION).order_by('order')
        ctx['troubleshootings'] = p.checks.filter(check_type=CheckTypeChoices.TROUBLESHOOTING).order_by('order')
        ctx['has_rollback'] = p.has_rollback_plan
        ctx['steps'] = p.steps.order_by('order', 'step_number')
        return ctx


class ProcedureGenerateView(FormView):
    template_name = 'procedures/procedure_generate.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # resolve once, reuse everywhere in this request
        self._procedure = get_object_or_404(
            Procedure.objects.prefetch_related('variables', 'steps', 'checks')
            .select_related('category'),
            slug=kwargs['slug'],
            status='published',
        )

    def get_form(self, form_class=None):
        variables = list(self._procedure.variables.order_by('order'))
        return DynamicProcedureForm(variables=variables, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['procedure'] = self._procedure
        return ctx

    def form_valid(self, form):
        procedure = self._procedure
        values = form.cleaned_data

        # Render configuration steps
        rendered_steps = [
            {
                'step': step,
                'rendered_command': render_command_template(step.command_template, values),
            }
            for step in procedure.steps.order_by('order', 'step_number')
        ]

        # Render checks with variable substitution
        def render_checks(check_type):
            return [
                {
                    'check': c,
                    'rendered_command': render_command_template(c.command, values),
                }
                for c in procedure.checks.filter(check_type=check_type).order_by('order')
            ]

        rendered_pre = render_checks(CheckTypeChoices.PRE)
        rendered_post = render_checks(CheckTypeChoices.POST)
        rendered_validations = render_checks(CheckTypeChoices.VALIDATION)

        # Render rollback
        rendered_rollback = None
        if procedure.has_rollback_plan:
            rb = procedure.rollback
            rendered_rollback = {
                'conditions': rb.conditions,
                'commands': render_command_template(rb.rollback_commands, values),
                'notes': rb.notes,
            }

        ctx = self.get_context_data(form=form)
        ctx.update({
            'rendered_steps': rendered_steps,
            'rendered_pre': rendered_pre,
            'rendered_post': rendered_post,
            'rendered_validations': rendered_validations,
            'rendered_rollback': rendered_rollback,
            'user_values': values,
            'generated': True,
        })
        return self.render_to_response(ctx)
