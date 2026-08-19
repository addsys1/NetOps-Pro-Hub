from django.views.generic import TemplateView
from django.shortcuts import render
from procedures.models import Procedure, ProcedureCategory


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_procedures'] = Procedure.objects.filter(status='published').count()
        ctx['total_categories'] = ProcedureCategory.objects.count()
        ctx['featured_procedures'] = (
            Procedure.objects.filter(status='published', is_featured=True)
            .select_related('category')[:6]
        )
        ctx['recent_procedures'] = (
            Procedure.objects.filter(status='published')
            .select_related('category')
            .order_by('-created_at')[:5]
        )
        ctx['categories'] = ProcedureCategory.objects.all()
        ctx['vendor_counts'] = _count_by_vendor()
        return ctx


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def _count_by_vendor():
    from django.db.models import Count
    return (
        Procedure.objects.filter(status='published')
        .values('vendor')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
