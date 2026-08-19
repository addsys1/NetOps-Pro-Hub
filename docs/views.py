from django.views.generic import ListView, DetailView
from .models import TechnicalDocument, DocCategory, DocType


class DocListView(ListView):
    model = TechnicalDocument
    template_name = 'docs/doc_list.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        qs = TechnicalDocument.objects.filter(is_published=True)
        q        = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '')
        doc_type = self.request.GET.get('type', '')
        if q:
            qs = (
                TechnicalDocument.objects.filter(is_published=True, title__icontains=q) |
                TechnicalDocument.objects.filter(is_published=True, description__icontains=q) |
                TechnicalDocument.objects.filter(is_published=True, tags__icontains=q)
            ).distinct()
        if category:
            qs = qs.filter(category=category)
        if doc_type:
            qs = qs.filter(document_type=doc_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query']    = self.request.GET.get('q', '')
        ctx['current_category'] = self.request.GET.get('category', '')
        ctx['current_type']    = self.request.GET.get('type', '')
        ctx['categories']      = DocCategory.choices
        ctx['doc_types']       = DocType.choices
        ctx['total']           = TechnicalDocument.objects.filter(is_published=True).count()
        return ctx


class DocDetailView(DetailView):
    model = TechnicalDocument
    template_name = 'docs/doc_detail.html'
    context_object_name = 'doc'

    def get_queryset(self):
        return TechnicalDocument.objects.filter(is_published=True)
