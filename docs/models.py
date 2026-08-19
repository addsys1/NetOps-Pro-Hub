from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class DocCategory(models.TextChoices):
    CONFIGURATION   = 'config',          'Configuration'
    SECURITE        = 'securite',        'Securite'
    TROUBLESHOOTING = 'troubleshooting', 'Troubleshooting'
    REFERENCE       = 'reference',       'Reference'
    FORMATION       = 'formation',       'Formation'
    AUTRE           = 'autre',           'Autre'


class DocType(models.TextChoices):
    PDF      = 'pdf',  'PDF'
    HTML     = 'html', 'HTML'
    TEXT     = 'text', 'Texte / Markdown'


class TechnicalDocument(models.Model):
    title           = models.CharField(max_length=200)
    slug            = models.SlugField(max_length=220, unique=True, blank=True)
    description     = models.TextField(blank=True)
    category        = models.CharField(max_length=30, choices=DocCategory.choices, default=DocCategory.AUTRE)
    tags            = models.CharField(max_length=300, blank=True, help_text="Tags separes par virgule")
    document_type   = models.CharField(max_length=10, choices=DocType.choices, default=DocType.PDF)
    file            = models.FileField(upload_to='docs/%Y/%m/', blank=True, null=True)
    html_content    = models.TextField(blank=True, help_text="Contenu HTML (si type HTML sans fichier)")
    related_procedure = models.ForeignKey(
        'procedures.Procedure', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='documents'
    )
    related_concept = models.ForeignKey(
        'concepts.NetworkConcept', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='documents'
    )
    is_published    = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Document technique'
        verbose_name_plural = 'Documents techniques'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('docs:detail', kwargs={'slug': self.slug})

    @property
    def category_icon(self):
        return {
            'config':          'bi-gear',
            'securite':        'bi-shield',
            'troubleshooting': 'bi-bug',
            'reference':       'bi-book',
            'formation':       'bi-mortarboard',
            'autre':           'bi-file-earmark',
        }.get(self.category, 'bi-file-earmark')

    @property
    def type_icon(self):
        return {
            'pdf':  'bi-file-earmark-pdf',
            'html': 'bi-file-earmark-code',
            'text': 'bi-file-earmark-text',
        }.get(self.document_type, 'bi-file-earmark')

    @property
    def type_color(self):
        return {
            'pdf':  'danger',
            'html': 'primary',
            'text': 'secondary',
        }.get(self.document_type, 'secondary')

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]
