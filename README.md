# NetOps Pro Hub

Base de connaissances centralisée pour les procédures réseau et sécurité.
Application Django interne pour ingénieurs réseau : catalogue de procédures guidées,
générateur de commandes dynamiques, pré/post checks, rollbacks.

---

## Stack technique

- Python 3.12+
- Django 5.x
- SQLite (MVP) → PostgreSQL ready
- Bootstrap 5 + Bootstrap Icons
- Django Crispy Forms

---

## Installation rapide

### 1. Créer et activer l'environnement virtuel

**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**
```bat
python -m venv venv
venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Initialiser la base de données

```bash
python manage.py migrate
```

### 4. Créer un superutilisateur (admin)

```bash
python manage.py createsuperuser
```

### 5. Charger les données de démonstration

```bash
python manage.py seed_data
```

Pour repartir de zéro (flush + reload) :
```bash
python manage.py seed_data --flush
```

### 6. Lancer le serveur

```bash
python manage.py runserver
```

L'application est accessible sur : http://127.0.0.1:8000

---

## Accès

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Dashboard |
| http://127.0.0.1:8000/procedures/ | Catalogue des procédures |
| http://127.0.0.1:8000/admin/ | Administration Django |

---

## Structure du projet

```
netops_pro_hub/
├── manage.py
├── README.md
├── requirements.txt
├── netops_pro_hub/          # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                    # App principale (dashboard)
│   ├── views.py
│   ├── urls.py
│   └── templatetags/
│       └── netops_tags.py
├── procedures/              # App procédures
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── renderer.py
│   └── management/
│       └── commands/
│           └── seed_data.py
├── templates/
│   ├── base.html
│   ├── core/
│   │   └── dashboard.html
│   ├── procedures/
│   │   ├── procedure_list.html
│   │   ├── procedure_detail.html
│   │   └── procedure_generate.html
│   └── partials/
│       └── _procedure_card.html
└── static/
    ├── css/
    │   └── netops.css
    └── js/
        └── netops.js
```

---

## Fonctionnalités

- **Dashboard** : statistiques, procédures mises en avant, récentes, catégories, vendors
- **Catalogue** : liste paginée avec recherche full-text et filtres (vendor, catégorie, équipement, difficulté)
- **Détail procédure** : objectif, prérequis, pré-checks, étapes avec commandes, post-checks, validation, rollback, notes
- **Générateur** : formulaire dynamique basé sur les variables, rendu des commandes, copie en un clic
- **Admin Django** : gestion complète avec inlines pour variables, étapes, checks, rollback

---

## Procédures de démonstration incluses

1. Créer un VLAN sur switch Cisco
2. Configurer un lien trunk Cisco
3. Configurer l'inter-VLAN sur switch L3
4. Ajouter une route statique Cisco
5. Créer une ACL standard Cisco
6. Créer une ACL extended Cisco
7. Configurer NAT Overload (PAT)
8. Configurer OSPF basique
9. Déployer SNMP v2c
10. Diagnostiquer un problème de trunk

---

## Migration vers PostgreSQL

Dans `settings.py`, remplacer la configuration DATABASES :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'netops_pro_hub',
        'USER': 'votre_user',
        'PASSWORD': 'votre_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Puis : `pip install psycopg2-binary && python manage.py migrate`
