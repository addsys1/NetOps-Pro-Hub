from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import NetworkConcept, LevelChoices


class ConceptListView(ListView):
    model = NetworkConcept
    template_name = 'concepts/concept_list.html'
    context_object_name = 'concepts'
    paginate_by = 24

    def get_queryset(self):
        qs = NetworkConcept.objects.all()
        q = self.request.GET.get('q', '').strip()
        level = self.request.GET.get('level', '').strip()
        module = self.request.GET.get('module', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(summary__icontains=q) |
                Q(simple_explanation__icontains=q)
            )
        if level:
            qs = qs.filter(level=level)
        if module:
            qs = qs.filter(module_number=module)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total'] = self.get_queryset().count()
        ctx['levels'] = LevelChoices.choices
        ctx['modules'] = (
            NetworkConcept.objects
            .values('module_number', 'module_name')
            .distinct()
            .order_by('module_number')
        )
        ctx['current_level'] = self.request.GET.get('level', '')
        ctx['current_module'] = self.request.GET.get('module', '')
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx


class ConceptDetailView(DetailView):
    model = NetworkConcept
    template_name = 'concepts/concept_detail.html'
    context_object_name = 'concept'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        concept = self.object
        ctx['prev_concept'] = (
            NetworkConcept.objects
            .filter(module_number=concept.module_number, order__lt=concept.order)
            .order_by('-order').first()
        )
        ctx['next_concept'] = (
            NetworkConcept.objects
            .filter(module_number=concept.module_number, order__gt=concept.order)
            .order_by('order').first()
        )
        return ctx
