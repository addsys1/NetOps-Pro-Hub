from django.db import models
from django.utils.text import slugify


class VendorChoices(models.TextChoices):
    CISCO = 'cisco', 'Cisco'
    FORTINET = 'fortinet', 'Fortinet'
    PALOALTO = 'paloalto', 'Palo Alto'
    JUNIPER = 'juniper', 'Juniper'
    ARUBA = 'aruba', 'Aruba / HP'
    GENERIC = 'generic', 'Générique'


class PlatformChoices(models.TextChoices):
    IOS = 'ios', 'Cisco IOS'
    IOS_XE = 'ios-xe', 'Cisco IOS-XE'
    NX_OS = 'nx-os', 'Cisco NX-OS'
    ASA = 'asa', 'Cisco ASA'
    FORTIOS = 'fortios', 'FortiOS'
    JUNOS = 'junos', 'JunOS'
    GENERIC = 'generic', 'Générique'


class DeviceTypeChoices(models.TextChoices):
    SWITCH = 'switch', 'Switch'
    ROUTER = 'router', 'Routeur'
    FIREWALL = 'firewall', 'Firewall'
    WIRELESS = 'wireless', 'Contrôleur Wifi'
    GENERIC = 'generic', 'Générique'


class DifficultyChoices(models.TextChoices):
    BEGINNER = 'beginner', 'Débutant'
    INTERMEDIATE = 'intermediate', 'Intermédiaire'
    ADVANCED = 'advanced', 'Avancé'
    EXPERT = 'expert', 'Expert'


class CriticalityChoices(models.TextChoices):
    LOW = 'low', 'Faible'
    MEDIUM = 'medium', 'Moyenne'
    HIGH = 'high', 'Haute'
    CRITICAL = 'critical', 'Critique'


class StatusChoices(models.TextChoices):
    DRAFT = 'draft', 'Brouillon'
    REVIEW = 'review', 'En révision'
    PUBLISHED = 'published', 'Publiée'
    DEPRECATED = 'deprecated', 'Dépréciée'


class FieldTypeChoices(models.TextChoices):
    TEXT = 'text', 'Texte'
    NUMBER = 'number', 'Nombre'
    IP = 'ip', 'Adresse IP'
    SUBNET = 'subnet', 'Masque de sous-réseau'
    VLAN = 'vlan', 'ID VLAN'
    INTERFACE = 'interface', 'Interface'
    SELECT = 'select', 'Liste de choix'


class CheckTypeChoices(models.TextChoices):
    PRE = 'pre', 'Pré-check'
    POST = 'post', 'Post-check'
    VALIDATION = 'validation', 'Validation'
    TROUBLESHOOTING = 'troubleshooting', 'Dépannage'


class ProcedureCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    icon = models.CharField(max_length=50, default='bi-folder', verbose_name="Icône Bootstrap")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Procedure(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True, max_length=220, verbose_name="Slug")
    summary = models.CharField(max_length=300, verbose_name="Résumé court")
    objective = models.TextField(verbose_name="Objectif")
    use_cases = models.TextField(blank=True, verbose_name="Cas d'usage")
    prerequisites = models.TextField(blank=True, verbose_name="Prérequis")
    expected_outcome = models.TextField(blank=True, verbose_name="Résultat attendu")
    best_practices = models.TextField(blank=True, verbose_name="Bonnes pratiques")
    common_pitfalls = models.TextField(blank=True, verbose_name="Pièges fréquents")
    notes = models.TextField(blank=True, verbose_name="Notes")

    vendor = models.CharField(
        max_length=20, choices=VendorChoices.choices,
        default=VendorChoices.CISCO, verbose_name="Vendor"
    )
    platform = models.CharField(
        max_length=20, choices=PlatformChoices.choices,
        default=PlatformChoices.IOS, verbose_name="Plateforme"
    )
    device_type = models.CharField(
        max_length=20, choices=DeviceTypeChoices.choices,
        default=DeviceTypeChoices.SWITCH, verbose_name="Type d'équipement"
    )
    difficulty = models.CharField(
        max_length=20, choices=DifficultyChoices.choices,
        default=DifficultyChoices.INTERMEDIATE, verbose_name="Difficulté"
    )
    criticality = models.CharField(
        max_length=20, choices=CriticalityChoices.choices,
        default=CriticalityChoices.MEDIUM, verbose_name="Criticité"
    )
    estimated_duration = models.PositiveSmallIntegerField(
        default=15, verbose_name="Durée estimée (min)"
    )
    requires_maintenance_window = models.BooleanField(
        default=False, verbose_name="Fenêtre de maintenance requise"
    )
    save_config_required = models.BooleanField(
        default=True, verbose_name="Sauvegarde de config requise"
    )
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices,
        default=StatusChoices.DRAFT, verbose_name="Statut"
    )
    category = models.ForeignKey(
        ProcedureCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='procedures',
        verbose_name="Catégorie"
    )
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Procédure"
        verbose_name_plural = "Procédures"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('procedures:detail', kwargs={'slug': self.slug})

    @property
    def step_count(self):
        return self.steps.count()

    @property
    def has_rollback_plan(self):
        try:
            return bool(self.rollback)
        except Exception:
            return False


class ProcedureVariable(models.Model):
    procedure = models.ForeignKey(
        Procedure, on_delete=models.CASCADE, related_name='variables'
    )
    name = models.CharField(
        max_length=60, verbose_name="Nom de variable",
        help_text="Identifiant utilisé dans les templates (ex: vlan_id)"
    )
    label = models.CharField(max_length=100, verbose_name="Label affiché")
    field_type = models.CharField(
        max_length=20, choices=FieldTypeChoices.choices,
        default=FieldTypeChoices.TEXT, verbose_name="Type de champ"
    )
    placeholder = models.CharField(max_length=100, blank=True, verbose_name="Placeholder")
    default_value = models.CharField(max_length=100, blank=True, verbose_name="Valeur par défaut")
    help_text = models.CharField(max_length=200, blank=True, verbose_name="Aide contextuelle")
    select_options = models.CharField(
        max_length=500, blank=True, verbose_name="Options (séparées par virgule)",
        help_text="Pour le type 'select' uniquement. Ex: GigabitEthernet,FastEthernet,TenGigabit"
    )
    required = models.BooleanField(default=True, verbose_name="Requis")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Variable"
        verbose_name_plural = "Variables"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.procedure.title} — {self.label}"


class ProcedureStep(models.Model):
    procedure = models.ForeignKey(
        Procedure, on_delete=models.CASCADE, related_name='steps'
    )
    step_number = models.PositiveSmallIntegerField(verbose_name="N° d'étape")
    title = models.CharField(max_length=200, verbose_name="Titre de l'étape")
    explanation = models.TextField(verbose_name="Explication")
    command_template = models.TextField(
        blank=True, verbose_name="Template de commandes",
        help_text="Utiliser {{ nom_variable }} pour les substitutions dynamiques"
    )
    expected_result = models.TextField(blank=True, verbose_name="Résultat attendu")
    warning = models.TextField(blank=True, verbose_name="Avertissement")
    real_world_example = models.TextField(blank=True, verbose_name="Exemple concret")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Étape"
        verbose_name_plural = "Étapes"
        ordering = ['order', 'step_number']

    def __str__(self):
        return f"Étape {self.step_number} — {self.title}"


class ProcedureCheck(models.Model):
    procedure = models.ForeignKey(
        Procedure, on_delete=models.CASCADE, related_name='checks'
    )
    check_type = models.CharField(
        max_length=20, choices=CheckTypeChoices.choices,
        verbose_name="Type de check"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    command = models.TextField(verbose_name="Commande")
    expected_output = models.TextField(blank=True, verbose_name="Sortie attendue")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Check"
        verbose_name_plural = "Checks"
        ordering = ['check_type', 'order']

    def __str__(self):
        return f"{self.get_check_type_display()} — {self.title}"


class ProcedureRollback(models.Model):
    procedure = models.OneToOneField(
        Procedure, on_delete=models.CASCADE, related_name='rollback'
    )
    conditions = models.TextField(verbose_name="Conditions de rollback")
    rollback_commands = models.TextField(verbose_name="Commandes de rollback")
    notes = models.TextField(blank=True, verbose_name="Notes de prudence")

    class Meta:
        verbose_name = "Rollback"
        verbose_name_plural = "Rollbacks"

    def __str__(self):
        return f"Rollback — {self.procedure.title}"
