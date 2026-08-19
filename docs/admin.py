from django.contrib import admin
from django.utils.html import format_html
from .models import TechnicalDocument


@admin.register(TechnicalDocument)
class TechnicalDocumentAdmin(admin.ModelAdmin):
    list_display  = ['title', 'doc_type_badge', 'category', 'is_published', 'created_at']
    list_filter   = ['document_type', 'category', 'is_published']
    search_fields = ['title', 'description', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Identification', {
            'fields': ('title', 'slug', 'description', 'category', 'tags', 'is_published'),
        }),
        ('Document', {
            'fields': ('document_type', 'file', 'html_content'),
        }),
        ('Relations (optionnel)', {
            'fields': ('related_procedure', 'related_concept'),
            'classes': ('collapse',),
        }),
        ('Metadonnees', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Type')
    def doc_type_badge(self, obj):
        colors = {'pdf': '#dc2626', 'html': '#2563eb', 'text': '#64748b'}
        color = colors.get(obj.document_type, '#64748b')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:.75rem;font-weight:600;">{}</span>',
            color, obj.get_document_type_display()
        )
