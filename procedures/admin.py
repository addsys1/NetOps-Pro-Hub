from django.contrib import admin
from .models import (
    ProcedureCategory, Procedure, ProcedureVariable,
    ProcedureStep, ProcedureCheck, ProcedureRollback,
)


@admin.register(ProcedureCategory)
class ProcedureCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ProcedureVariableInline(admin.TabularInline):
    model = ProcedureVariable
    extra = 1
    fields = ('order', 'name', 'label', 'field_type', 'placeholder', 'default_value', 'select_options', 'required')
    ordering = ('order',)


class ProcedureStepInline(admin.StackedInline):
    model = ProcedureStep
    extra = 1
    fields = ('order', 'step_number', 'title', 'explanation', 'command_template', 'real_world_example', 'expected_result', 'warning')
    ordering = ('order',)


class ProcedureCheckInline(admin.TabularInline):
    model = ProcedureCheck
    extra = 1
    fields = ('order', 'check_type', 'title', 'command', 'expected_output')
    ordering = ('check_type', 'order')


class ProcedureRollbackInline(admin.StackedInline):
    model = ProcedureRollback
    extra = 0
    max_num = 1
    fields = ('conditions', 'rollback_commands', 'notes')


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'vendor', 'platform', 'device_type',
        'difficulty', 'criticality', 'status', 'is_featured', 'requires_maintenance_window',
    )
    list_filter = (
        'status', 'vendor', 'platform', 'device_type',
        'difficulty', 'criticality', 'category', 'is_featured', 'requires_maintenance_window',
    )
    search_fields = ('title', 'summary', 'objective', 'best_practices')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status', 'is_featured', 'criticality')
    ordering = ('-created_at',)

    fieldsets = (
        ('Identification', {
            'fields': ('title', 'slug', 'category', 'summary', 'status', 'is_featured')
        }),
        ('Contenu opérationnel', {
            'fields': ('objective', 'use_cases', 'prerequisites', 'expected_outcome')
        }),
        ('Conseils & Risques', {
            'fields': ('best_practices', 'common_pitfalls', 'notes')
        }),
        ('Classification', {
            'fields': (
                'vendor', 'platform', 'device_type',
                'difficulty', 'criticality', 'estimated_duration',
                'requires_maintenance_window', 'save_config_required',
            )
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    inlines = [
        ProcedureVariableInline,
        ProcedureStepInline,
        ProcedureCheckInline,
        ProcedureRollbackInline,
    ]
