from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class LevelChoices(models.TextChoices):
    BASE = 'base', 'Base'
    INTERMEDIATE = 'intermediate', 'Intermediaire'
    ADVANCED = 'advanced', 'Avance'


class NetworkConcept(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    module_number = models.PositiveSmallIntegerField(default=1)
    module_name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LevelChoices.choices, default=LevelChoices.BASE)
    icon = models.CharField(max_length=60, default='bi-lightbulb')
    order = models.PositiveSmallIntegerField(default=0)

    simple_explanation = models.TextField()
    concrete_example = models.TextField()
    technical_version = models.TextField()
    summary = models.CharField(max_length=300)

    quiz_q1 = models.CharField(max_length=300)
    quiz_a1 = models.TextField()
    quiz_q2 = models.CharField(max_length=300)
    quiz_a2 = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['module_number', 'order']
        verbose_name = 'Concept reseau'
        verbose_name_plural = 'Concepts reseau'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('concepts:detail', kwargs={'slug': self.slug})

    @property
    def level_color(self):
        return {'base': 'success', 'intermediate': 'warning', 'advanced': 'danger'}.get(self.level, 'secondary')

    @property
    def level_label(self):
        return {'base': 'Base', 'intermediate': 'Intermediaire', 'advanced': 'Avance'}.get(self.level, self.level)
