from django.contrib import admin
from .models import NetworkConcept


@admin.register(NetworkConcept)
class NetworkConceptAdmin(admin.ModelAdmin):
    list_display = ('title', 'module_number', 'module_name', 'level', 'order')
    list_filter = ('level', 'module_number', 'module_name')
    search_fields = ('title', 'summary', 'simple_explanation')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('module_number', 'order')
    fieldsets = (
        ('Identification', {
            'fields': ('title', 'slug', 'icon', 'module_number', 'module_name', 'level', 'order'),
        }),
        ('Contenu pedagogique', {
            'fields': ('simple_explanation', 'concrete_example', 'technical_version', 'summary'),
        }),
        ('Mini quiz', {
            'fields': ('quiz_q1', 'quiz_a1', 'quiz_q2', 'quiz_a2'),
        }),
    )
