"""
Commande de seed additionnelle : python manage.py seed_extra
Ajoute de nouvelles procedures sans toucher aux donnees existantes.
Utilise get_or_create pour les categories et verifie les slugs avant insertion.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from procedures.models import (
    ProcedureCategory, Procedure, ProcedureVariable,
    ProcedureStep, ProcedureCheck, ProcedureRollback,
)

# Nouvelles categories (creees seulement si absentes)
NEW_CATEGORIES = [
    {
        'name': 'Haute Disponibilite',
        'slug': 'haute-disponibilite',
        'icon': 'bi-arrow-repeat',
        'description': 'HSRP, VRRP, redondance et basculement automatique',
    },
]

PROCEDURES_DATA = [

    # ── 1. Basic Router Configuration ─────────────────────────────────────────
    {
        'title': 'Configuration de base d\'un routeur Cisco',
        'summary': 'Initialisation complete d\'un routeur Cisco : hostname, mots de passe, interfaces, banniere et securite de base.',
        'objective': 'Appliquer une configuration initiale standardisee sur un routeur Cisco IOS avant sa mise en production.',
        'use_cases': (
            '- Deploiement d\'un nouveau routeur en production\n'
            '- Reinitialisation d\'un equipement reconditionne\n'
            '- Standardisation du parc routeurs\n'
            '- Formation et labos Cisco'
        ),
        'prerequisites': (
            '- Acces console (cable rollover)\n'
            '- IOS charge et operationnel\n'
            '- Plan d\'adressage defini\n'
            '- Politique de mots de passe validee'
        ),
        'expected_outcome': (
            'Le routeur repond au hostname configure, les interfaces sont up/up avec leurs IP, '
            'l\'acces console et VTY sont proteges, la configuration est sauvegardee en NVRAM.'
        ),
        'best_practices': (
            '- Toujours definir un hostname explicite des la premiere connexion\n'
            '- Chiffrer tous les mots de passe avec service password-encryption\n'
            '- Configurer une banniere MOTD pour avertissement legal\n'
            '- Desactiver les services inutiles (CDP si non necessaire, HTTP server)\n'
            '- Utiliser des mots de passe enable secret (MD5) plutot qu\'enable password'
        ),
        'common_pitfalls': (
            '- Oublier "no shutdown" sur les interfaces (restent down par defaut)\n'
            '- Ne pas sauvegarder la config (perte au redemarrage)\n'
            '- Laisser le mot de passe console vide\n'
            '- Oublier "login" sur les lignes VTY (acces sans authentification)\n'
            '- Configurer une IP sur la mauvaise interface'
        ),
        'notes': 'La commande "service password-encryption" utilise un chiffrement faible (type 7). Privilegier "enable secret" pour le mot de passe enable.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'beginner',
        'criticality': 'high',
        'estimated_duration': 20,
        'status': 'published',
        'category': 'routage',
        'is_featured': True,
        'requires_maintenance_window': False,
        'save_config_required': True,
        'variables': [
            {'name': 'hostname',       'label': 'Hostname du routeur',    'field_type': 'text',    'placeholder': 'R1-PROD',          'order': 1},
            {'name': 'enable_secret',  'label': 'Mot de passe enable',    'field_type': 'text',    'placeholder': 'P@ssw0rd!',        'order': 2},
            {'name': 'console_pass',   'label': 'Mot de passe console',   'field_type': 'text',    'placeholder': 'Console123',       'order': 3},
            {'name': 'vty_pass',       'label': 'Mot de passe VTY (SSH)', 'field_type': 'text',    'placeholder': 'Vty@Pass123',      'order': 4},
            {'name': 'interface_wan',  'label': 'Interface WAN',          'field_type': 'interface','placeholder': 'GigabitEthernet0/0','order': 5},
            {'name': 'ip_wan',         'label': 'IP interface WAN',       'field_type': 'ip',      'placeholder': '203.0.113.1',      'order': 6},
            {'name': 'mask_wan',       'label': 'Masque WAN',             'field_type': 'text',    'placeholder': '255.255.255.252',  'order': 7},
            {'name': 'interface_lan',  'label': 'Interface LAN',          'field_type': 'interface','placeholder': 'GigabitEthernet0/1','order': 8},
            {'name': 'ip_lan',         'label': 'IP interface LAN',       'field_type': 'ip',      'placeholder': '192.168.1.1',      'order': 9},
            {'name': 'mask_lan',       'label': 'Masque LAN',             'field_type': 'text',    'placeholder': '255.255.255.0',    'order': 10},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer le hostname et les mots de passe',
                'explanation': 'Definir l\'identite de l\'equipement et securiser les acces privilegies et console.',
                'command_template': (
                    'enable\n'
                    'configure terminal\n'
                    'hostname {{ hostname }}\n'
                    'enable secret {{ enable_secret }}\n'
                    'service password-encryption\n'
                    'no ip domain-lookup'
                ),
                'expected_result': 'Prompt affiche {{ hostname }}(config)#. Recherches DNS desactivees.',
                'warning': '',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Securiser la ligne console et les lignes VTY',
                'explanation': 'Proteger l\'acces physique (console) et les acces distants (VTY 0-4) par mot de passe.',
                'command_template': (
                    'line console 0\n'
                    ' password {{ console_pass }}\n'
                    ' login\n'
                    ' logging synchronous\n'
                    ' exec-timeout 10 0\n'
                    'line vty 0 4\n'
                    ' password {{ vty_pass }}\n'
                    ' login\n'
                    ' transport input ssh telnet\n'
                    ' exec-timeout 10 0'
                ),
                'expected_result': 'Acces console et VTY proteges par mot de passe. Session fermee apres 10 min d\'inactivite.',
                'warning': 'Ne pas oublier "login" — sans cette commande, le mot de passe n\'est pas demande.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer l\'interface WAN',
                'explanation': 'Assigner l\'adresse IP et activer l\'interface connectee au reseau WAN ou FAI.',
                'command_template': (
                    'interface {{ interface_wan }}\n'
                    ' description WAN-UPLINK\n'
                    ' ip address {{ ip_wan }} {{ mask_wan }}\n'
                    ' no shutdown'
                ),
                'expected_result': '{{ interface_wan }} est up/up avec l\'IP {{ ip_wan }}.',
                'warning': '',
                'order': 3,
            },
            {
                'step_number': 4,
                'title': 'Configurer l\'interface LAN',
                'explanation': 'Assigner l\'adresse IP de la passerelle LAN et activer l\'interface.',
                'command_template': (
                    'interface {{ interface_lan }}\n'
                    ' description LAN-LOCAL\n'
                    ' ip address {{ ip_lan }} {{ mask_lan }}\n'
                    ' no shutdown'
                ),
                'expected_result': '{{ interface_lan }} est up/up avec l\'IP {{ ip_lan }}.',
                'warning': '',
                'order': 4,
            },
            {
                'step_number': 5,
                'title': 'Configurer la banniere MOTD et sauvegarder',
                'explanation': 'Ajouter un message d\'avertissement legal et persister la configuration en NVRAM.',
                'command_template': (
                    'banner motd # Acces reserve au personnel autorise. Toute connexion non autorisee sera poursuivie. #\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Banniere visible a la prochaine connexion. Configuration sauvegardee [OK].',
                'warning': '',
                'order': 5,
            },
        ],
        'checks': [
            {'check_type': 'pre',  'title': 'Verifier la version IOS',          'command': 'show version',                           'expected_output': 'Version IOS et type de plateforme affiches.',                         'order': 1},
            {'check_type': 'pre',  'title': 'Verifier la config actuelle',       'command': 'show running-config',                    'expected_output': 'Configuration vide ou par defaut — confirmer avant modification.',    'order': 2},
            {'check_type': 'post', 'title': 'Verifier les interfaces',           'command': 'show interfaces brief',                  'expected_output': '{{ interface_wan }} et {{ interface_lan }} up/up avec leurs IP.',     'order': 1},
            {'check_type': 'post', 'title': 'Verifier la config sauvegardee',    'command': 'show startup-config | include hostname',  'expected_output': 'hostname {{ hostname }}',                                           'order': 2},
            {'check_type': 'validation', 'title': 'Ping passerelle LAN',        'command': 'ping {{ ip_lan }}',                      'expected_output': 'Success rate is 100 percent (5/5)',                                  'order': 1},
        ],
        'rollback': {
            'conditions': 'Mauvaise configuration causant une perte de connectivite ou un conflit d\'adressage.',
            'rollback_commands': (
                'configure terminal\n'
                'no hostname\n'
                'interface {{ interface_wan }}\n'
                ' no ip address\n'
                ' shutdown\n'
                'interface {{ interface_lan }}\n'
                ' no ip address\n'
                ' shutdown\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'En cas de perte totale d\'acces, utiliser le cable console pour recuperer la main.',
        },
    },

    # ── 2. Basic Switch Configuration ─────────────────────────────────────────
    {
        'title': 'Configuration de base d\'un switch Cisco',
        'summary': 'Initialisation complete d\'un switch Cisco Catalyst : hostname, mots de passe, interface de gestion, SSH et securite de base.',
        'objective': 'Appliquer une configuration initiale standardisee sur un switch Cisco avant integration dans le reseau.',
        'use_cases': (
            '- Deploiement d\'un nouveau switch en production\n'
            '- Remplacement d\'un switch defaillant\n'
            '- Standardisation du parc switching\n'
            '- Mise en conformite securite'
        ),
        'prerequisites': (
            '- Acces console (cable rollover)\n'
            '- Switch alimente, IOS charge\n'
            '- VLAN de gestion defini\n'
            '- Adresse IP de gestion disponible'
        ),
        'expected_outcome': (
            'Le switch repond au hostname, l\'interface de gestion SVI est up avec son IP, '
            'SSH est configure, les acces console et VTY sont proteges.'
        ),
        'best_practices': (
            '- Utiliser un VLAN de gestion dedie (pas le VLAN 1)\n'
            '- Activer SSH v2 (plus securise que Telnet)\n'
            '- Configurer un nom de domaine pour la generation des cles RSA\n'
            '- Desactiver les ports inutilises (shutdown)\n'
            '- Activer PortFast sur les ports d\'acces utilisateurs'
        ),
        'common_pitfalls': (
            '- Oublier la passerelle par defaut (ip default-gateway) sur un switch L2\n'
            '- Creer la SVI sans que le VLAN existe dans la base VLAN\n'
            '- Oublier "crypto key generate rsa" pour SSH\n'
            '- Ne pas definir "ip domain-name" avant la generation RSA\n'
            '- Laisser DTP actif sur les ports d\'acces'
        ),
        'notes': 'Sur les switches L2, "ip default-gateway" est obligatoire pour joindre le switch depuis un autre reseau. Sur les switches L3, utiliser "ip route 0.0.0.0 0.0.0.0".',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'beginner',
        'criticality': 'high',
        'estimated_duration': 20,
        'status': 'published',
        'category': 'vlan-switching',
        'is_featured': True,
        'requires_maintenance_window': False,
        'save_config_required': True,
        'variables': [
            {'name': 'hostname',       'label': 'Hostname du switch',       'field_type': 'text', 'placeholder': 'SW1-PROD',        'order': 1},
            {'name': 'enable_secret',  'label': 'Mot de passe enable',      'field_type': 'text', 'placeholder': 'P@ssw0rd!',       'order': 2},
            {'name': 'mgmt_vlan',      'label': 'VLAN de gestion',          'field_type': 'vlan', 'placeholder': '99',              'order': 3},
            {'name': 'mgmt_ip',        'label': 'IP de gestion (SVI)',      'field_type': 'ip',   'placeholder': '192.168.99.10',   'order': 4},
            {'name': 'mgmt_mask',      'label': 'Masque de gestion',        'field_type': 'text', 'placeholder': '255.255.255.0',   'order': 5},
            {'name': 'default_gw',     'label': 'Passerelle par defaut',    'field_type': 'ip',   'placeholder': '192.168.99.1',    'order': 6},
            {'name': 'domain_name',    'label': 'Nom de domaine',           'field_type': 'text', 'placeholder': 'netops.local',    'order': 7},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer hostname et securite de base',
                'explanation': 'Definir l\'identite de l\'equipement, chiffrer les mots de passe et securiser l\'acces privilegied.',
                'command_template': (
                    'enable\n'
                    'configure terminal\n'
                    'hostname {{ hostname }}\n'
                    'enable secret {{ enable_secret }}\n'
                    'service password-encryption\n'
                    'no ip domain-lookup'
                ),
                'expected_result': 'Prompt {{ hostname }}(config)# affiché.',
                'warning': '',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Creer le VLAN de gestion et configurer la SVI',
                'explanation': 'Creer le VLAN dedie a la gestion et lui assigner une adresse IP via l\'interface virtuelle SVI.',
                'command_template': (
                    'vlan {{ mgmt_vlan }}\n'
                    ' name MGMT\n'
                    'interface vlan {{ mgmt_vlan }}\n'
                    ' ip address {{ mgmt_ip }} {{ mgmt_mask }}\n'
                    ' no shutdown\n'
                    'ip default-gateway {{ default_gw }}'
                ),
                'expected_result': 'SVI Vlan{{ mgmt_vlan }} up/up avec IP {{ mgmt_ip }}. Passerelle configuree.',
                'warning': 'Le VLAN {{ mgmt_vlan }} doit exister et avoir au moins un port actif pour que la SVI passe up.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer SSH v2',
                'explanation': 'Activer SSH version 2 pour les acces distants securises. Remplace Telnet (non chiffre).',
                'command_template': (
                    'ip domain-name {{ domain_name }}\n'
                    'crypto key generate rsa modulus 2048\n'
                    'ip ssh version 2\n'
                    'line vty 0 15\n'
                    ' transport input ssh\n'
                    ' login local\n'
                    ' exec-timeout 10 0'
                ),
                'expected_result': 'Cles RSA 2048 bits generees. SSH v2 actif. Telnet bloque sur VTY.',
                'warning': 'La generation RSA peut prendre quelques secondes sur les anciens materiels.',
                'order': 3,
            },
            {
                'step_number': 4,
                'title': 'Securiser la console et sauvegarder',
                'explanation': 'Proteger l\'acces physique console et persister la configuration.',
                'command_template': (
                    'line console 0\n'
                    ' logging synchronous\n'
                    ' exec-timeout 10 0\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier la version IOS',       'command': 'show version',                          'expected_output': 'Version IOS et modele du switch.',                           'order': 1},
            {'check_type': 'post',      'title': 'Verifier la SVI de gestion',    'command': 'show interfaces vlan {{ mgmt_vlan }}',   'expected_output': 'Vlan{{ mgmt_vlan }} is up, line protocol is up',           'order': 1},
            {'check_type': 'post',      'title': 'Verifier SSH',                  'command': 'show ip ssh',                           'expected_output': 'SSH Enabled - version 2.0',                                'order': 2},
            {'check_type': 'validation','title': 'Ping depuis le switch',         'command': 'ping {{ default_gw }}',                 'expected_output': 'Success rate is 100 percent (5/5)',                        'order': 1},
        ],
        'rollback': {
            'conditions': 'Mauvaise configuration de la SVI ou conflit d\'adressage rendant le switch inaccessible.',
            'rollback_commands': (
                'configure terminal\n'
                'no interface vlan {{ mgmt_vlan }}\n'
                'no ip default-gateway {{ default_gw }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Utiliser le cable console pour recuperer l\'acces en cas de perte totale de connectivite.',
        },
    },

    # ── 3. EIGRP Configuration ─────────────────────────────────────────────────
    {
        'title': 'Configurer EIGRP sur routeur Cisco',
        'summary': 'Mise en place du protocole EIGRP pour le routage dynamique interne, avec Router-ID, annonces reseau et interfaces passives.',
        'objective': 'Activer EIGRP (Enhanced Interior Gateway Routing Protocol) entre plusieurs routeurs Cisco pour un echange automatique de routes.',
        'use_cases': (
            '- Routage interne dans un reseau d\'entreprise Cisco\n'
            '- Migration depuis RIP vers un protocole plus performant\n'
            '- Environnements necessitant une convergence rapide\n'
            '- Labos CCNA/CCNP preparation'
        ),
        'prerequisites': (
            '- Connectivite L3 entre les routeurs\n'
            '- Interfaces configurees avec adresses IP\n'
            '- Meme numero d\'AS EIGRP sur tous les routeurs\n'
            '- Acces privilege 15'
        ),
        'expected_outcome': (
            'Les adjacences EIGRP sont etablies (state FULL). Les routes apprises apparaissent '
            'avec le tag "D" dans la table de routage. La convergence est inferieure a 5 secondes.'
        ),
        'best_practices': (
            '- Utiliser un Router-ID fixe et unique (eviter les changements en cas de panne d\'interface)\n'
            '- Configurer les interfaces vers les utilisateurs en passive-interface\n'
            '- Utiliser "no auto-summary" (desactive par defaut en IOS 15+)\n'
            '- Authentifier les echanges EIGRP en production\n'
            '- Documenter le numero d\'AS et les reseaux annonces'
        ),
        'common_pitfalls': (
            '- Numero d\'AS EIGRP different entre les routeurs (adjacence impossible)\n'
            '- Reseau annonce avec le mauvais masque wildcard\n'
            '- Auto-summary actif creant des routes agregees incorrectes (IOS < 15)\n'
            '- K-values differentes entre routeurs (adjacence refusee)\n'
            '- Oublier les interfaces secondaires dans les annonces network'
        ),
        'notes': 'EIGRP est un protocole proprietaire Cisco (partiellement ouvert depuis 2013). Le numero d\'AS EIGRP est local — il ne correspond pas au numero d\'AS BGP.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'intermediate',
        'criticality': 'high',
        'estimated_duration': 25,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'as_number',       'label': 'Numero d\'AS EIGRP',        'field_type': 'text',    'placeholder': '100',              'order': 1},
            {'name': 'router_id',       'label': 'Router-ID',                 'field_type': 'ip',      'placeholder': '1.1.1.1',          'order': 2},
            {'name': 'network1',        'label': 'Reseau annonce 1',          'field_type': 'ip',      'placeholder': '192.168.1.0',      'order': 3},
            {'name': 'wildcard1',       'label': 'Wildcard reseau 1',         'field_type': 'text',    'placeholder': '0.0.0.255',        'order': 4},
            {'name': 'network2',        'label': 'Reseau annonce 2',          'field_type': 'ip',      'placeholder': '10.0.0.0',         'order': 5},
            {'name': 'wildcard2',       'label': 'Wildcard reseau 2',         'field_type': 'text',    'placeholder': '0.0.0.3',          'order': 6},
            {'name': 'passive_iface',   'label': 'Interface passive (LAN)',   'field_type': 'interface','placeholder': 'GigabitEthernet0/1','order': 7},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Activer EIGRP et configurer le Router-ID',
                'explanation': 'Creer le processus EIGRP avec le numero d\'AS et definir un Router-ID stable.',
                'command_template': (
                    'configure terminal\n'
                    'router eigrp {{ as_number }}\n'
                    ' eigrp router-id {{ router_id }}\n'
                    ' no auto-summary'
                ),
                'expected_result': 'Processus EIGRP {{ as_number }} actif avec Router-ID {{ router_id }}.',
                'warning': '',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Annoncer les reseaux dans EIGRP',
                'explanation': 'Declarer les reseaux directement connectes que EIGRP doit annoncer aux voisins.',
                'command_template': (
                    ' network {{ network1 }} {{ wildcard1 }}\n'
                    ' network {{ network2 }} {{ wildcard2 }}'
                ),
                'expected_result': 'EIGRP commence a envoyer des Hello sur les interfaces correspondantes.',
                'warning': 'Verifier que le masque wildcard est correct (inverse du masque de sous-reseau).',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer les interfaces passives',
                'explanation': 'Empecher l\'envoi de Hellos EIGRP sur les interfaces LAN (securite et economies de ressources).',
                'command_template': (
                    ' passive-interface {{ passive_iface }}\n'
                    'end'
                ),
                'expected_result': 'Aucun paquet Hello EIGRP envoye sur {{ passive_iface }}.',
                'warning': 'Ne pas rendre passive une interface connectee a un autre routeur EIGRP.',
                'order': 3,
            },
            {
                'step_number': 4,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration EIGRP en NVRAM.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier connectivite vers voisin',  'command': 'ping <ip_voisin>',                  'expected_output': 'Success rate is 100 percent',                                     'order': 1},
            {'check_type': 'pre',       'title': 'Verifier absence EIGRP existant',    'command': 'show ip protocols',                 'expected_output': 'Aucun processus EIGRP actif (ou AS different)',                    'order': 2},
            {'check_type': 'post',      'title': 'Verifier les voisins EIGRP',         'command': 'show ip eigrp neighbors',           'expected_output': 'Voisins listes avec Uptime et Q Cnt = 0',                         'order': 1},
            {'check_type': 'post',      'title': 'Verifier les routes apprises',       'command': 'show ip route eigrp',               'expected_output': 'Routes "D" presentes dans la table de routage',                   'order': 2},
            {'check_type': 'post',      'title': 'Verifier la topologie EIGRP',        'command': 'show ip eigrp topology',            'expected_output': 'Routes en etat Passive (P) — Successors et FD affiches',          'order': 3},
            {'check_type': 'validation','title': 'Ping reseau distant via EIGRP',      'command': 'ping {{ network1 }}',               'expected_output': 'Success rate is 100 percent (5/5)',                               'order': 1},
            {'check_type': 'troubleshooting','title': 'Debugger les hellos EIGRP',     'command': 'debug ip eigrp',                    'expected_output': 'Paquets Hello/Update/ACK visibles — desactiver avec undebug all', 'order': 1},
        ],
        'rollback': {
            'conditions': 'EIGRP cause des problemes de routage ou des boucles apres activation.',
            'rollback_commands': (
                'configure terminal\n'
                'no router eigrp {{ as_number }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'La suppression du processus EIGRP retire immediatement toutes les routes apprises via ce protocole. Prevoir un acces de secours.',
        },
    },

    # ── 4. Port Security Configuration ────────────────────────────────────────
    {
        'title': 'Configurer Port Security sur switch Cisco',
        'summary': 'Activation de la securite de port pour limiter les adresses MAC autorisees et prevenir les attaques MAC flooding.',
        'objective': 'Restreindre l\'acces a un port switch a un nombre limite d\'adresses MAC et definir l\'action en cas de violation.',
        'use_cases': (
            '- Protection contre les attaques MAC flooding (CAM table overflow)\n'
            '- Controle d\'acces physique aux ports switch\n'
            '- Prevention du branchement de switches non autorises\n'
            '- Conformite PCI-DSS / securite reseau entreprise'
        ),
        'prerequisites': (
            '- Port en mode access (pas trunk)\n'
            '- Droits enable/configuration\n'
            '- Politique de securite definie (max MACs, action violation)\n'
            '- DTP desactive sur le port'
        ),
        'expected_outcome': (
            'Le port accepte uniquement les adresses MAC autorisees. '
            'En cas de violation, l\'action configuree est declenchee (shutdown/restrict/protect). '
            '"show port-security interface" affiche Security Enabled: Yes.'
        ),
        'best_practices': (
            '- Utiliser "sticky" pour apprendre automatiquement les MACs legitimes\n'
            '- Privilegier le mode "restrict" en production (log + drop sans couper le port)\n'
            '- Limiter a 1 ou 2 MACs maximum sur les ports utilisateurs\n'
            '- Configurer err-disable recovery pour eviter une intervention manuelle\n'
            '- Documenter les MACs autorisees par port'
        ),
        'common_pitfalls': (
            '- Activer port-security sur un port trunk (non supporte)\n'
            '- Oublier que "shutdown" (defaut) met le port en err-disabled — necessite intervention\n'
            '- Les adresses sticky ne sont pas sauvegardees si on ne fait pas copy run start\n'
            '- Changer le mode de port apres port-security peut causer des erreurs\n'
            '- Oublier de reactiver le port apres une violation (err-disabled)'
        ),
        'notes': 'Le mode "shutdown" est le plus securise mais necessite une intervention manuelle (no shutdown) pour retablir le port. Preferer "restrict" avec surveillance SNMP/Syslog.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'intermediate',
        'criticality': 'medium',
        'estimated_duration': 15,
        'status': 'published',
        'category': 'securite-acl',
        'is_featured': False,
        'requires_maintenance_window': False,
        'save_config_required': True,
        'variables': [
            {'name': 'interface_name',  'label': 'Interface a securiser',     'field_type': 'interface', 'placeholder': 'FastEthernet0/1',  'order': 1},
            {'name': 'max_mac',         'label': 'Nombre max d\'adresses MAC','field_type': 'text',      'placeholder': '2',                'order': 2},
            {
                'name': 'violation_mode',
                'label': 'Mode de violation',
                'field_type': 'select',
                'placeholder': 'restrict',
                'order': 3,
                'select_options': 'shutdown|Shutdown (err-disabled)\nrestrict|Restrict (log + drop)\nprotect|Protect (drop silencieux)',
            },
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer le port en mode access et activer port-security',
                'explanation': 'Forcer le mode access sur le port et activer la securite de port.',
                'command_template': (
                    'configure terminal\n'
                    'interface {{ interface_name }}\n'
                    ' switchport mode access\n'
                    ' switchport nonegotiate\n'
                    ' switchport port-security'
                ),
                'expected_result': 'Port-security active sur {{ interface_name }}.',
                'warning': 'Port-security ne fonctionne que sur les ports en mode access. Verifier que le port n\'est pas trunk.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Configurer le nombre max de MACs et le mode sticky',
                'explanation': 'Limiter le nombre d\'adresses MAC autorisees et activer l\'apprentissage automatique (sticky).',
                'command_template': (
                    ' switchport port-security maximum {{ max_mac }}\n'
                    ' switchport port-security mac-address sticky'
                ),
                'expected_result': 'Le port apprendra et retiendra automatiquement jusqu\'a {{ max_mac }} adresses MAC.',
                'warning': '',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer le mode de violation',
                'explanation': 'Definir le comportement du switch lorsqu\'une adresse MAC non autorisee est detectee.',
                'command_template': (
                    ' switchport port-security violation {{ violation_mode }}\n'
                    'end'
                ),
                'expected_result': 'Mode de violation {{ violation_mode }} actif sur {{ interface_name }}.',
                'warning': 'Le mode "shutdown" met le port en err-disabled. Configurer err-disable recovery si necessaire.',
                'order': 3,
            },
            {
                'step_number': 4,
                'title': 'Sauvegarder (important pour les MACs sticky)',
                'explanation': 'Persister la configuration incluant les adresses MAC sticky apprises.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration et MACs sticky sauvegardees [OK].',
                'warning': '',
                'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier le mode du port',             'command': 'show interfaces {{ interface_name }} switchport', 'expected_output': 'Administrative Mode: access',                              'order': 1},
            {'check_type': 'post',      'title': 'Verifier port-security actif',         'command': 'show port-security interface {{ interface_name }}', 'expected_output': 'Port Security: Enabled, Maximum MAC Addresses: {{ max_mac }}, Violation Mode: {{ violation_mode }}', 'order': 1},
            {'check_type': 'post',      'title': 'Verifier les MACs apprises',           'command': 'show port-security address',                       'expected_output': 'Adresses sticky listees pour {{ interface_name }}',          'order': 2},
            {'check_type': 'post',      'title': 'Verifier les violations = 0',          'command': 'show port-security',                               'expected_output': 'Security Violation Count: 0 — aucune violation en cours',   'order': 3},
            {'check_type': 'validation','title': 'Verifier connectivite apres config',   'command': 'show interfaces {{ interface_name }} status',       'expected_output': 'connected — port non en err-disabled',                     'order': 1},
        ],
        'rollback': {
            'conditions': 'Port en err-disabled suite a une violation ou port-security causant des problemes de connectivite.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ interface_name }}\n'
                ' no switchport port-security\n'
                ' shutdown\n'
                ' no shutdown\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Si le port est en err-disabled : "shutdown" puis "no shutdown" apres avoir supprime port-security.',
        },
    },

    # ── 6. IPv6 Interface Configuration ───────────────────────────────────────
    {
        'title': 'Configurer une interface IPv6 sur routeur Cisco',
        'summary': 'Activation d\'IPv6, configuration d\'adresses statiques ou EUI-64 et verification de la connectivite IPv6.',
        'objective': 'Activer IPv6 sur un routeur Cisco, assigner des adresses statiques ou EUI-64 sur les interfaces et verifier la connectivite.',
        'use_cases': (
            '- Migration reseau vers IPv6 (dual-stack)\n'
            '- Labos CCNA/CCNP IPv6\n'
            '- Connectivite IPv6 native avec un FAI\n'
            '- Preparation a l\'epuisement des adresses IPv4'
        ),
        'prerequisites': (
            '- IOS 12.4(15)T ou superieur\n'
            '- Interfaces configurees et up\n'
            '- Plan d\'adressage IPv6 defini (/64 recommande pour les LANs)\n'
            '- Droits privilege 15'
        ),
        'expected_outcome': (
            'Les interfaces affichent leurs adresses IPv6 (link-local + globale) dans "show ipv6 interface brief". '
            'Le ping IPv6 fonctionne entre interfaces directement connectees.'
        ),
        'best_practices': (
            '- Toujours activer "ipv6 unicast-routing" avant de configurer les interfaces\n'
            '- Utiliser EUI-64 pour generer automatiquement la partie hote de l\'adresse\n'
            '- Documenter les prefixes /64 assignes par interface\n'
            '- Configurer un lien-local explicite pour la lisibilite (optionnel)\n'
            '- Verifier la presence de l\'adresse link-local auto-generee (FE80::)'
        ),
        'common_pitfalls': (
            '- Oublier "ipv6 unicast-routing" : le routage IPv6 ne fonctionne pas\n'
            '- Utiliser un prefixe /128 au lieu de /64 sur une interface LAN\n'
            '- Confondre l\'adresse link-local (FE80::/10) et l\'adresse globale (2000::/3)\n'
            '- Ne pas activer "ipv6 enable" sur les interfaces sans adresse globale\n'
            '- Oublier "no shutdown" apres configuration'
        ),
        'notes': 'Chaque interface IPv6 active possede automatiquement une adresse link-local (FE80::) utilisee pour les protocoles de voisinage (NDP) et les protocoles de routage IPv6.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'intermediate',
        'criticality': 'medium',
        'estimated_duration': 20,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': False,
        'save_config_required': True,
        'variables': [
            {'name': 'interface_name', 'label': 'Interface a configurer',  'field_type': 'interface', 'placeholder': 'GigabitEthernet0/0', 'order': 1},
            {'name': 'ipv6_address',   'label': 'Adresse IPv6 / prefixe', 'field_type': 'text',      'placeholder': '2001:db8:acad:1::1/64', 'order': 2},
            {'name': 'interface_lan',  'label': 'Interface LAN (EUI-64)', 'field_type': 'interface', 'placeholder': 'GigabitEthernet0/1', 'order': 3},
            {'name': 'prefix_lan',     'label': 'Prefixe LAN (/64)',      'field_type': 'text',      'placeholder': '2001:db8:acad:2::/64', 'order': 4},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Activer le routage IPv6 global',
                'explanation': 'Activer IPv6 unicast routing pour permettre au routeur de forwarder des paquets IPv6.',
                'command_template': 'configure terminal\nipv6 unicast-routing',
                'expected_result': 'Routage IPv6 actif sur le routeur.',
                'warning': 'Sans cette commande, les interfaces IPv6 sont configurees mais le routeur ne route pas les paquets IPv6.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Configurer une adresse IPv6 statique sur l\'interface WAN',
                'explanation': 'Assigner une adresse IPv6 globale avec son prefixe et activer l\'interface.',
                'command_template': (
                    'interface {{ interface_name }}\n'
                    ' ipv6 address {{ ipv6_address }}\n'
                    ' no shutdown'
                ),
                'expected_result': '{{ interface_name }} affiche l\'adresse {{ ipv6_address }} et une link-local FE80::x.',
                'warning': '',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer une adresse EUI-64 sur l\'interface LAN',
                'explanation': 'EUI-64 derive automatiquement la partie hote de l\'adresse IPv6 depuis l\'adresse MAC de l\'interface.',
                'command_template': (
                    'interface {{ interface_lan }}\n'
                    ' ipv6 address {{ prefix_lan }} eui-64\n'
                    ' no shutdown\n'
                    'end'
                ),
                'expected_result': '{{ interface_lan }} affiche une adresse IPv6 globale derivee du prefixe {{ prefix_lan }} + MAC EUI-64.',
                'warning': '',
                'order': 3,
            },
            {
                'step_number': 4,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration IPv6.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier IPv6 unicast-routing',      'command': 'show running-config | include ipv6 unicast',     'expected_output': 'ipv6 unicast-routing',                                      'order': 1},
            {'check_type': 'post',      'title': 'Verifier les adresses IPv6',         'command': 'show ipv6 interface brief',                      'expected_output': 'Interfaces up avec adresses globales et link-local',        'order': 1},
            {'check_type': 'post',      'title': 'Verifier la table de routage IPv6',  'command': 'show ipv6 route',                                'expected_output': 'Routes C (connected) pour les prefixes configures',         'order': 2},
            {'check_type': 'validation','title': 'Ping IPv6 vers voisin',              'command': 'ping ipv6 <adresse_ipv6_voisin>',                'expected_output': 'Success rate is 100 percent (5/5)',                         'order': 1},
        ],
        'rollback': {
            'conditions': 'Conflit d\'adressage IPv6 ou besoin de desactiver IPv6 sur une interface.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ interface_name }}\n'
                ' no ipv6 address\n'
                'interface {{ interface_lan }}\n'
                ' no ipv6 address\n'
                'no ipv6 unicast-routing\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'La suppression de "ipv6 unicast-routing" desactive le routage IPv6 sur tout le routeur.',
        },
    },

    # ── 7. ACL Extended Configuration ─────────────────────────────────────────
    {
        'title': 'Configurer une ACL etendue Cisco',
        'summary': 'Creation d\'une ACL etendue filtrant le trafic sur la source, la destination, le protocole et le port. Plus precise que les ACL standard.',
        'objective': 'Creer une ACL etendue nommee pour filtrer le trafic reseau avec granularite (IP source + destination + port TCP/UDP) et l\'appliquer sur une interface.',
        'use_cases': (
            '- Filtrage de trafic applicatif (bloquer HTTP, autoriser HTTPS)\n'
            '- Controle d\'acces entre VLANs\n'
            '- Blocage de protocoles specifiques\n'
            '- Protection de serveurs (autoriser uniquement les services exposes)'
        ),
        'prerequisites': (
            '- Acces privilege 15 sur le routeur/switch L3\n'
            '- Politique de filtrage definie (source, destination, port, action)\n'
            '- Interfaces configurees avec adresses IP\n'
            '- Connaissance du numerotage ACL (100-199 ou nommees)'
        ),
        'expected_outcome': (
            'L\'ACL etendue est creee et visible dans "show access-lists". '
            'Le trafic autorise passe, le trafic bloque est drope (et logge si "log" est ajoute). '
            'Les compteurs (matches) s\'incrementent au passage du trafic.'
        ),
        'best_practices': (
            '- Toujours utiliser des ACL nommees (plus lisibles que les numerotees)\n'
            '- Placer l\'ACL etendue le plus pres de la SOURCE du trafic\n'
            '- Terminer toujours par un "deny any any log" explicite (implicit deny est invisible)\n'
            '- Ordonner les regles du plus specifique au plus general\n'
            '- Tester en "permit" avant de passer en "deny" sur du trafic inconnu'
        ),
        'common_pitfalls': (
            '- Appliquer une ACL in/out dans le mauvais sens (bloquer son propre acces SSH)\n'
            '- Oublier que l\'implicit deny bloque tout sans log — difficile a debugger\n'
            '- Utiliser des adresses hotes sans "host" ou avec un mauvais wildcard\n'
            '- Modifier une ACL en production sans tester l\'impact (risque de coupure)\n'
            '- Oublier d\'autoriser les ACK/RST pour les sessions TCP existantes (stateless)'
        ),
        'notes': 'Les ACL Cisco sont stateless. Pour un firewall stateful, utiliser CBAC (IOS) ou ZBF (Zone-Based Firewall). Les ACL etendues nommees permettent de supprimer des entrees individuelles.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'intermediate',
        'criticality': 'high',
        'estimated_duration': 20,
        'status': 'published',
        'category': 'securite-acl',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'acl_name',        'label': 'Nom de l\'ACL',              'field_type': 'text',      'placeholder': 'ACL-INTERNET-IN',     'order': 1},
            {'name': 'src_network',     'label': 'Reseau source',              'field_type': 'ip',        'placeholder': '192.168.1.0',          'order': 2},
            {'name': 'src_wildcard',    'label': 'Wildcard source',            'field_type': 'text',      'placeholder': '0.0.0.255',            'order': 3},
            {'name': 'dst_network',     'label': 'Reseau destination',         'field_type': 'ip',        'placeholder': '10.0.0.0',             'order': 4},
            {'name': 'dst_wildcard',    'label': 'Wildcard destination',       'field_type': 'text',      'placeholder': '0.0.0.255',            'order': 5},
            {'name': 'permit_port',     'label': 'Port TCP/UDP autorise',      'field_type': 'text',      'placeholder': '443',                  'order': 6},
            {'name': 'interface_acl',   'label': 'Interface d\'application',   'field_type': 'interface', 'placeholder': 'GigabitEthernet0/0',   'order': 7},
            {
                'name': 'direction',
                'label': 'Direction',
                'field_type': 'select',
                'placeholder': 'in',
                'order': 8,
                'select_options': 'in|Inbound (entrant)\nout|Outbound (sortant)',
            },
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Creer l\'ACL etendue nommee',
                'explanation': 'Definir l\'ACL avec des regles permit/deny specifiques au protocole, la source, la destination et le port.',
                'command_template': (
                    'configure terminal\n'
                    'ip access-list extended {{ acl_name }}\n'
                    ' remark Autorise HTTPS depuis LAN vers DMZ\n'
                    ' permit tcp {{ src_network }} {{ src_wildcard }} {{ dst_network }} {{ dst_wildcard }} eq {{ permit_port }}\n'
                    ' remark Autorise les reponses etablies\n'
                    ' permit tcp any any established\n'
                    ' remark Deny implicite avec log\n'
                    ' deny ip any any log'
                ),
                'expected_result': 'ACL {{ acl_name }} creee avec les regles definies.',
                'warning': 'Verifier que la regle "permit tcp any any established" est presente pour ne pas bloquer les sessions TCP retour.',
                'order': 1,
                'real_world_example': 'Exemple : tu veux autoriser uniquement le HTTPS (port 443) depuis le reseau des employes (192.168.1.0/24) vers les serveurs en DMZ (10.10.10.0/24). Avec une ACL standard, tu ne pourrais filtrer que par IP source. Avec l\'ACL etendue, tu peux dire exactement : "IP source 192.168.1.X, destination 10.10.10.X, protocole TCP, port 443 seulement" — tout le reste est bloque.',
            },
            {
                'step_number': 2,
                'title': 'Appliquer l\'ACL sur l\'interface',
                'explanation': 'Lier l\'ACL a une interface dans la direction choisie (in = trafic entrant, out = trafic sortant).',
                'command_template': (
                    'interface {{ interface_acl }}\n'
                    ' ip access-group {{ acl_name }} {{ direction }}\n'
                    'end'
                ),
                'expected_result': 'ACL {{ acl_name }} appliquee {{ direction }} sur {{ interface_acl }}.',
                'warning': 'ATTENTION : si vous appliquez en "in" sur l\'interface de gestion, vous pouvez perdre l\'acces SSH. Toujours inclure une regle permit pour votre IP source.',
                'order': 2,
                'real_world_example': 'Exemple : tu appliques l\'ACL en "in" sur Gi0/0 (l\'interface connectee au reseau des employes). Cela filtre le trafic DES SON ENTREE sur le routeur, avant qu\'il aille plus loin. Si tu l\'appliquais en "out" sur l\'interface vers la DMZ, le routeur traiterait d\'abord le paquet, puis verifierait s\'il peut sortir. La regle ACL etendue : placer au plus pres de la source, donc en "in".',
            },
            {
                'step_number': 3,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration ACL.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier ACL existantes sur l\'interface', 'command': 'show ip interface {{ interface_acl }}',  'expected_output': 'Inbound/Outbound access list is not set',                                    'order': 1},
            {'check_type': 'post',      'title': 'Verifier les regles de l\'ACL',            'command': 'show access-lists {{ acl_name }}',        'expected_output': 'Extended IP access list {{ acl_name }} avec les entrees permit/deny',        'order': 1},
            {'check_type': 'post',      'title': 'Verifier l\'application sur l\'interface', 'command': 'show ip interface {{ interface_acl }}',   'expected_output': '{{ direction }} access list is {{ acl_name }}',                            'order': 2},
            {'check_type': 'validation','title': 'Verifier les compteurs (hitcounts)',        'command': 'show access-lists {{ acl_name }}',        'expected_output': 'matches incrementent sur les regles touchees par le trafic reel',           'order': 1},
        ],
        'rollback': {
            'conditions': 'L\'ACL bloque du trafic legitime ou cause une perte de connectivite.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ interface_acl }}\n'
                ' no ip access-group {{ acl_name }} {{ direction }}\n'
                'no ip access-list extended {{ acl_name }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Supprimer d\'abord l\'application sur l\'interface, puis l\'ACL elle-meme. L\'ordre inverse laisse une ACL orpheline.',
        },
    },

    # ── 8. EtherChannel L2 Configuration ──────────────────────────────────────
    {
        'title': 'Configurer un EtherChannel L2 (LACP)',
        'summary': 'Agregation de liens physiques en un canal logique L2 avec LACP pour augmenter la bande passante et la redondance entre switches.',
        'objective': 'Creer un Port-Channel L2 en agregant plusieurs interfaces physiques avec le protocole LACP (802.3ad) entre deux switches Cisco.',
        'use_cases': (
            '- Uplinks entre switches d\'acces et de distribution\n'
            '- Augmenter la bande passante sans changer le materiel\n'
            '- Redondance de lien (un lien peut tomber sans coupure)\n'
            '- Connexion de serveurs multi-NIC en teaming'
        ),
        'prerequisites': (
            '- Interfaces physiques identiques (meme vitesse, meme duplex)\n'
            '- Meme VLAN/trunk de chaque cote\n'
            '- LACP supporte des deux cotes (ou PAgP pour Cisco-Cisco)\n'
            '- Ports non assignes a d\'autres port-channels'
        ),
        'expected_outcome': (
            '"show etherchannel summary" affiche le Port-Channel en etat "SU" (Layer2, in use). '
            'Les interfaces membres sont en etat "P" (bundled). '
            'La bande passante effective est la somme des liens membres.'
        ),
        'best_practices': (
            '- Utiliser LACP (active/active ou active/passive) plutot que PAgP\n'
            '- Configurer le Port-Channel comme trunk avant d\'ajouter les membres physiques\n'
            '- S\'assurer que TOUS les membres ont la meme configuration (vitesse, duplex, VLAN)\n'
            '- Ne pas depasser 8 liens actifs par port-channel (limite LACP)\n'
            '- Utiliser des interfaces contiguës pour une meilleure gestion'
        ),
        'common_pitfalls': (
            '- Interfaces membres avec des configurations differentes (vitesse, VLAN) : channel ne monte pas\n'
            '- Configurer les membres physiques en trunk avant le Port-Channel (sequence incorrecte)\n'
            '- Melanger LACP et PAgP (incompatibles)\n'
            '- Oublier que STP voit le Port-Channel comme un seul lien\n'
            '- Ne pas verifier les deux cotes avant d\'activer (missmatch de protocole)'
        ),
        'notes': 'LACP (mode active) envoie des PDUs pour negocier le bundle. Mode passive attend les PDUs. Ne jamais mettre les deux cotes en passive (aucun ne negocie).',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'intermediate',
        'criticality': 'high',
        'estimated_duration': 25,
        'status': 'published',
        'category': 'vlan-switching',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'pc_number',       'label': 'Numero du Port-Channel',    'field_type': 'text',      'placeholder': '1',                   'order': 1},
            {'name': 'member_iface1',   'label': 'Interface membre 1',        'field_type': 'interface', 'placeholder': 'GigabitEthernet0/1',  'order': 2},
            {'name': 'member_iface2',   'label': 'Interface membre 2',        'field_type': 'interface', 'placeholder': 'GigabitEthernet0/2',  'order': 3},
            {'name': 'allowed_vlans',   'label': 'VLANs autorises (trunk)',   'field_type': 'text',      'placeholder': '10,20,30,99',          'order': 4},
            {'name': 'native_vlan',     'label': 'VLAN natif',                'field_type': 'vlan',      'placeholder': '99',                   'order': 5},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer l\'interface Port-Channel logique',
                'explanation': 'Creer le Port-Channel logique et le configurer en trunk avec les VLANs autorises avant d\'ajouter les membres.',
                'command_template': (
                    'configure terminal\n'
                    'interface port-channel {{ pc_number }}\n'
                    ' switchport trunk encapsulation dot1q\n'
                    ' switchport mode trunk\n'
                    ' switchport trunk allowed vlan {{ allowed_vlans }}\n'
                    ' switchport trunk native vlan {{ native_vlan }}\n'
                    ' switchport nonegotiate'
                ),
                'expected_result': 'Port-Channel {{ pc_number }} cree en mode trunk.',
                'warning': 'Configurer d\'abord le Port-Channel logique, puis ajouter les membres. L\'ordre inverse peut causer des inconsistances.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Assigner les interfaces physiques au Port-Channel',
                'explanation': 'Configurer les interfaces membres en mode trunk et les lier au Port-Channel via LACP.',
                'command_template': (
                    'interface {{ member_iface1 }}\n'
                    ' switchport trunk encapsulation dot1q\n'
                    ' switchport mode trunk\n'
                    ' switchport nonegotiate\n'
                    ' channel-group {{ pc_number }} mode active\n'
                    'interface {{ member_iface2 }}\n'
                    ' switchport trunk encapsulation dot1q\n'
                    ' switchport mode trunk\n'
                    ' switchport nonegotiate\n'
                    ' channel-group {{ pc_number }} mode active\n'
                    'end'
                ),
                'expected_result': 'Les deux interfaces rejoignent le Port-Channel {{ pc_number }} en mode LACP active.',
                'warning': '',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration EtherChannel.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier l\'etat des interfaces membres', 'command': 'show interfaces {{ member_iface1 }} status',     'expected_output': 'connected, trunking ou notconnect',                              'order': 1},
            {'check_type': 'post',      'title': 'Verifier l\'etat du EtherChannel',        'command': 'show etherchannel summary',                       'expected_output': 'Po{{ pc_number }}  (SU) — membres {{ member_iface1 }} (P) {{ member_iface2 }} (P)', 'order': 1},
            {'check_type': 'post',      'title': 'Verifier le trunk Port-Channel',          'command': 'show interfaces port-channel {{ pc_number }} trunk', 'expected_output': 'VLANs {{ allowed_vlans }} en forwarding state',                'order': 2},
            {'check_type': 'post',      'title': 'Verifier les details LACP',               'command': 'show lacp {{ pc_number }} neighbor',              'expected_output': 'Informations LACP du voisin listees pour chaque membre',        'order': 3},
            {'check_type': 'validation','title': 'Ping entre switches via Port-Channel',    'command': 'show etherchannel {{ pc_number }} detail',         'expected_output': 'Port state = EC-Enbld, bundled, standalone Disabled',          'order': 1},
        ],
        'rollback': {
            'conditions': 'Le Port-Channel ne monte pas ou cause des boucles STP.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ member_iface1 }}\n'
                ' no channel-group {{ pc_number }}\n'
                'interface {{ member_iface2 }}\n'
                ' no channel-group {{ pc_number }}\n'
                'no interface port-channel {{ pc_number }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Supprimer les membres avant l\'interface Port-Channel. Les interfaces retournent en mode standalone trunk.',
        },
    },

    # ── 9. Router-on-a-Stick ──────────────────────────────────────────────────
    {
        'title': 'Configurer le Router-on-a-Stick (ROAS)',
        'summary': 'Routage inter-VLAN via sous-interfaces 802.1Q sur un routeur Cisco connecte a un trunk switch. Alternative economique au switch L3.',
        'objective': 'Permettre le routage entre plusieurs VLANs en utilisant des sous-interfaces (subinterfaces) dot1Q sur un seul lien physique routeur-switch.',
        'use_cases': (
            '- Routage inter-VLAN sans switch L3\n'
            '- Petits reseaux avec routeur unique\n'
            '- Labos CCNA inter-VLAN routing\n'
            '- Environnements ou le switch L3 n\'est pas disponible'
        ),
        'prerequisites': (
            '- Switch configure avec VLANs et lien trunk vers le routeur\n'
            '- Interface physique du routeur connectee au port trunk du switch\n'
            '- Plan d\'adressage defini par VLAN\n'
            '- VLANs crees sur le switch'
        ),
        'expected_outcome': (
            'Chaque sous-interface repond en ping depuis les hotes du VLAN correspondant. '
            'Le trafic entre VLANs passe par le routeur. '
            '"show ip route" montre les routes connectees pour chaque sous-reseau VLAN.'
        ),
        'best_practices': (
            '- Nommer les sous-interfaces avec le numero de VLAN (ex: Gi0/0.10 pour VLAN 10)\n'
            '- Configurer "encapsulation dot1Q" avant "ip address"\n'
            '- Activer l\'interface physique parente avec "no shutdown" (sans IP)\n'
            '- Pour le VLAN natif : utiliser "encapsulation dot1Q <vlan> native"\n'
            '- ROAS est limite en debit car tout le trafic inter-VLAN passe par un seul lien'
        ),
        'common_pitfalls': (
            '- Oublier "no shutdown" sur l\'interface physique parente\n'
            '- Numero de VLAN dans encapsulation dot1Q different du VLAN configure sur le switch\n'
            '- Assigner une IP directement sur l\'interface physique (pas sur la sous-interface)\n'
            '- Switch port du routeur configure en access au lieu de trunk\n'
            '- VLAN non cree sur le switch mais configure sur le routeur'
        ),
        'notes': 'ROAS (Router-on-a-Stick) est limite par le debit du lien physique partage. Pour des environnements a fort trafic inter-VLAN, privilegier un switch L3 avec SVI.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'intermediate',
        'criticality': 'high',
        'estimated_duration': 20,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'phys_interface', 'label': 'Interface physique vers switch', 'field_type': 'interface', 'placeholder': 'GigabitEthernet0/0',    'order': 1},
            {'name': 'vlan1_id',       'label': 'VLAN 1 ID',                     'field_type': 'vlan',      'placeholder': '10',                    'order': 2},
            {'name': 'vlan1_ip',       'label': 'IP passerelle VLAN 1',          'field_type': 'ip',        'placeholder': '192.168.10.1',           'order': 3},
            {'name': 'vlan1_mask',     'label': 'Masque VLAN 1',                 'field_type': 'text',      'placeholder': '255.255.255.0',          'order': 4},
            {'name': 'vlan2_id',       'label': 'VLAN 2 ID',                     'field_type': 'vlan',      'placeholder': '20',                    'order': 5},
            {'name': 'vlan2_ip',       'label': 'IP passerelle VLAN 2',          'field_type': 'ip',        'placeholder': '192.168.20.1',           'order': 6},
            {'name': 'vlan2_mask',     'label': 'Masque VLAN 2',                 'field_type': 'text',      'placeholder': '255.255.255.0',          'order': 7},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Activer l\'interface physique parente (sans IP)',
                'explanation': 'L\'interface physique doit etre active mais sans adresse IP propre. Les IP sont sur les sous-interfaces.',
                'command_template': (
                    'configure terminal\n'
                    'interface {{ phys_interface }}\n'
                    ' no ip address\n'
                    ' no shutdown'
                ),
                'expected_result': '{{ phys_interface }} est up/up sans adresse IP.',
                'warning': '',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Creer la sous-interface pour le VLAN 1',
                'explanation': 'Creer une sous-interface dot1Q pour le premier VLAN et lui assigner l\'adresse IP de passerelle.',
                'command_template': (
                    'interface {{ phys_interface }}.{{ vlan1_id }}\n'
                    ' encapsulation dot1Q {{ vlan1_id }}\n'
                    ' ip address {{ vlan1_ip }} {{ vlan1_mask }}'
                ),
                'expected_result': 'Sous-interface {{ phys_interface }}.{{ vlan1_id }} avec IP {{ vlan1_ip }}, en etat up/up.',
                'warning': 'Le numero apres le point est libre mais utiliser le numero de VLAN par convention.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Creer la sous-interface pour le VLAN 2',
                'explanation': 'Meme procedure pour le second VLAN.',
                'command_template': (
                    'interface {{ phys_interface }}.{{ vlan2_id }}\n'
                    ' encapsulation dot1Q {{ vlan2_id }}\n'
                    ' ip address {{ vlan2_ip }} {{ vlan2_mask }}\n'
                    'end'
                ),
                'expected_result': 'Sous-interface {{ phys_interface }}.{{ vlan2_id }} avec IP {{ vlan2_ip }}, en etat up/up.',
                'warning': '',
                'order': 3,
            },
            {
                'step_number': 4,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration ROAS.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier le trunk cote switch',         'command': 'show interfaces trunk',                                        'expected_output': 'Port switch en mode trunk avec VLANs {{ vlan1_id }} et {{ vlan2_id }}',  'order': 1},
            {'check_type': 'post',      'title': 'Verifier les sous-interfaces',          'command': 'show interfaces {{ phys_interface }}.{{ vlan1_id }}',           'expected_output': '{{ phys_interface }}.{{ vlan1_id }} is up, line protocol is up',        'order': 1},
            {'check_type': 'post',      'title': 'Verifier les routes connectees',        'command': 'show ip route connected',                                      'expected_output': 'Routes C pour {{ vlan1_ip }} et {{ vlan2_ip }}',                         'order': 2},
            {'check_type': 'validation','title': 'Ping passerelle VLAN 1 depuis un hote', 'command': 'ping {{ vlan1_ip }} source {{ phys_interface }}.{{ vlan1_id }}','expected_output': 'Success rate is 100 percent (5/5)',                                     'order': 1},
            {'check_type': 'validation','title': 'Ping inter-VLAN (VLAN1 vers VLAN2)',   'command': 'ping {{ vlan2_ip }} source {{ phys_interface }}.{{ vlan1_id }}','expected_output': 'Success rate is 100 percent (5/5)',                                     'order': 2},
        ],
        'rollback': {
            'conditions': 'Mauvaise configuration des sous-interfaces ou perte de connectivite inter-VLAN.',
            'rollback_commands': (
                'configure terminal\n'
                'no interface {{ phys_interface }}.{{ vlan1_id }}\n'
                'no interface {{ phys_interface }}.{{ vlan2_id }}\n'
                'interface {{ phys_interface }}\n'
                ' shutdown\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Supprimer les sous-interfaces supprime le routage inter-VLAN. Les hotes n\'ont plus de passerelle.',
        },
    },

    # ── 10. DHCP Server Configuration ─────────────────────────────────────────
    {
        'title': 'Configurer un serveur DHCP sur routeur Cisco',
        'summary': 'Mise en place du service DHCP natif sur un routeur Cisco pour distribuer automatiquement les parametres IP aux hotes d\'un reseau.',
        'objective': 'Creer un pool DHCP sur un routeur Cisco pour attribuer automatiquement adresses IP, masque, passerelle et DNS aux hotes du reseau local.',
        'use_cases': (
            '- Distribution d\'adresses IP automatique dans un LAN\n'
            '- Remplacement d\'un serveur DHCP Windows/Linux par le routeur\n'
            '- Labos ou les hotes doivent recevoir une configuration IP automatiquement\n'
            '- Reseaux de succursales avec routeur Cisco en edge'
        ),
        'prerequisites': (
            '- Interface LAN du routeur configuree et up\n'
            '- Plan d\'adressage DHCP defini (plage, exclusions, DNS)\n'
            '- Droits privilege 15\n'
            '- Aucun autre serveur DHCP actif sur le meme sous-reseau'
        ),
        'expected_outcome': (
            'Les hotes du reseau recoivent automatiquement une adresse IP dans la plage definie. '
            '"show ip dhcp binding" liste les baux actifs. '
            '"show ip dhcp pool" affiche les statistiques du pool.'
        ),
        'best_practices': (
            '- Toujours exclure les adresses reservees (routeurs, switches, serveurs, imprimantes)\n'
            '- Utiliser une duree de bail adaptee (courte pour les Wi-Fi, longue pour les postes fixes)\n'
            '- Configurer le DNS et le domain-name dans le pool\n'
            '- Activer les logs DHCP pour le troubleshooting\n'
            '- Documenter les plages DHCP dans le plan d\'adressage'
        ),
        'common_pitfalls': (
            '- Oublier "ip dhcp excluded-address" : les IP reservees sont distribuees\n'
            '- Pool DHCP sur un sous-reseau different de l\'interface LAN (pas de distribution)\n'
            '- Deux serveurs DHCP sur le meme segment (adresses en conflit)\n'
            '- Oublier le default-router : les hotes n\'ont pas de passerelle\n'
            '- Plage DHCP qui chevauche les adresses statiques existantes'
        ),
        'notes': 'Si les hotes sont sur un VLAN different du routeur, configurer "ip helper-address" sur l\'interface SVI du switch L3 pour relayer les broadcasts DHCP.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'beginner',
        'criticality': 'medium',
        'estimated_duration': 15,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': False,
        'save_config_required': True,
        'variables': [
            {'name': 'pool_name',       'label': 'Nom du pool DHCP',          'field_type': 'text', 'placeholder': 'LAN-POOL',          'order': 1},
            {'name': 'network',         'label': 'Reseau DHCP',               'field_type': 'ip',   'placeholder': '192.168.1.0',       'order': 2},
            {'name': 'mask',            'label': 'Masque',                    'field_type': 'text', 'placeholder': '255.255.255.0',     'order': 3},
            {'name': 'excl_start',      'label': 'Exclusion debut',           'field_type': 'ip',   'placeholder': '192.168.1.1',       'order': 4},
            {'name': 'excl_end',        'label': 'Exclusion fin',             'field_type': 'ip',   'placeholder': '192.168.1.20',      'order': 5},
            {'name': 'default_gw',      'label': 'Passerelle par defaut',     'field_type': 'ip',   'placeholder': '192.168.1.1',       'order': 6},
            {'name': 'dns_server',      'label': 'Serveur DNS',               'field_type': 'ip',   'placeholder': '8.8.8.8',           'order': 7},
            {'name': 'domain_name',     'label': 'Nom de domaine',            'field_type': 'text', 'placeholder': 'netops.local',      'order': 8},
            {'name': 'lease_days',      'label': 'Duree du bail (jours)',     'field_type': 'text', 'placeholder': '7',                 'order': 9},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Exclure les adresses reservees',
                'explanation': 'Definir les adresses qui ne seront pas distribuees par DHCP (routeurs, serveurs, equipements avec IP fixe).',
                'command_template': (
                    'configure terminal\n'
                    'ip dhcp excluded-address {{ excl_start }} {{ excl_end }}'
                ),
                'expected_result': 'Les adresses {{ excl_start }} a {{ excl_end }} sont exclues du pool DHCP.',
                'warning': 'Cette commande doit etre saisie AVANT la creation du pool pour eviter toute distribution accidentelle.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Creer et configurer le pool DHCP',
                'explanation': 'Definir le pool avec le reseau, la passerelle, le DNS et la duree de bail.',
                'command_template': (
                    'ip dhcp pool {{ pool_name }}\n'
                    ' network {{ network }} {{ mask }}\n'
                    ' default-router {{ default_gw }}\n'
                    ' dns-server {{ dns_server }}\n'
                    ' domain-name {{ domain_name }}\n'
                    ' lease {{ lease_days }}'
                ),
                'expected_result': 'Pool {{ pool_name }} configure. Le routeur commence a repondre aux requetes DHCP Discover.',
                'warning': '',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration DHCP.',
                'command_template': 'end\ncopy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier l\'absence d\'autre DHCP',   'command': 'show ip dhcp pool',           'expected_output': 'Aucun pool existant ou pool sur un sous-reseau different',        'order': 1},
            {'check_type': 'post',      'title': 'Verifier le pool configure',          'command': 'show ip dhcp pool',           'expected_output': 'Pool {{ pool_name }}, network {{ network }}, default-router {{ default_gw }}', 'order': 1},
            {'check_type': 'post',      'title': 'Verifier les exclusions',             'command': 'show ip dhcp pool',           'expected_output': 'Excluded addresses: {{ excl_start }} - {{ excl_end }}',            'order': 2},
            {'check_type': 'validation','title': 'Verifier les baux attribues',         'command': 'show ip dhcp binding',        'expected_output': 'Adresses IP listees avec MAC clients et expiration du bail',       'order': 1},
            {'check_type': 'validation','title': 'Verifier les statistiques DHCP',      'command': 'show ip dhcp server statistics','expected_output': 'Discover/Offer/Request/Ack > 0 apres connexion d\'un hote',    'order': 2},
        ],
        'rollback': {
            'conditions': 'Conflit d\'adresses ou besoin de desactiver le serveur DHCP.',
            'rollback_commands': (
                'configure terminal\n'
                'no ip dhcp pool {{ pool_name }}\n'
                'no ip dhcp excluded-address {{ excl_start }} {{ excl_end }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Apres suppression, les hotes conservent leurs baux jusqu\'a expiration. Un "ipconfig /release" cote client force le renouvellement.',
        },
    },

    # ── 11. VTP Configuration ─────────────────────────────────────────────────
    {
        'title': 'Configurer VTP sur un domaine de switches Cisco',
        'summary': 'Mise en place de VTP (VLAN Trunking Protocol) pour synchroniser la base de donnees VLAN sur plusieurs switches via un serveur central.',
        'objective': 'Configurer un switch en mode VTP Server et les autres en mode VTP Client pour propager automatiquement les VLANs sur l\'ensemble du domaine.',
        'use_cases': (
            '- Gestion centralisee des VLANs sur un parc de switches\n'
            '- Propagation automatique des nouveaux VLANs sans reconfiguration manuelle\n'
            '- Environnements avec de nombreux switches et VLANs\n'
            '- Reduction des erreurs de configuration VLAN'
        ),
        'prerequisites': (
            '- Liens trunk 802.1Q opérationnels entre les switches\n'
            '- Domaine VTP identique sur tous les switches\n'
            '- Version VTP identique (v1, v2 ou v3)\n'
            '- Acces privilege 15 sur tous les switches'
        ),
        'expected_outcome': (
            'Le switch serveur propage ses VLANs a tous les clients. '
            '"show vtp status" affiche le meme Configuration Revision et Domain Name sur tous les switches.'
        ),
        'best_practices': (
            '- Utiliser VTP v3 (plus securise, supporte les VLANs etendus 1006-4094)\n'
            '- Definir un mot de passe VTP pour eviter les domaines parasites\n'
            '- Configurer les switches non administres en mode Transparent ou Off\n'
            '- Toujours verifier le Configuration Revision avant de connecter un switch inconnu\n'
            '- Documenter le nombre de VLANs et le revision number courant'
        ),
        'common_pitfalls': (
            '- Connecter un switch avec un revision number superieur (ecrase tous les VLANs !)\n'
            '- Domaine VTP mal orthographie (case sensitive en v1/v2)\n'
            '- Mot de passe VTP different entre server et clients (pas de synchronisation)\n'
            '- Oublier que VTP ne propage pas les configurations de ports (juste les VLANs)\n'
            '- Switch en mode Transparent ne propage pas mais transmet les messages VTP'
        ),
        'notes': 'DANGER : Un switch avec un revision number eleve peut ecraser la base VLAN de tout le domaine. Toujours reinitialiser le revision number (changer de domaine puis revenir) avant de connecter un switch reconfigure.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'intermediate',
        'criticality': 'critical',
        'estimated_duration': 20,
        'status': 'published',
        'category': 'vlan-switching',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'domain_name',  'label': 'Nom de domaine VTP',   'field_type': 'text', 'placeholder': 'NETOPS-DOMAIN', 'order': 1},
            {'name': 'vtp_password', 'label': 'Mot de passe VTP',     'field_type': 'text', 'placeholder': 'VTP$ecret123',  'order': 2},
            {
                'name': 'vtp_mode',
                'label': 'Mode VTP',
                'field_type': 'select',
                'placeholder': 'server',
                'order': 3,
                'select_options': 'server|Server (propage les VLANs)\nclient|Client (recoit les VLANs)\ntransparent|Transparent (local uniquement)',
            },
            {'name': 'vtp_version', 'label': 'Version VTP', 'field_type': 'select', 'placeholder': '2',
             'select_options': '1|Version 1\n2|Version 2\n3|Version 3', 'order': 4},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer le domaine VTP, la version et le mot de passe',
                'explanation': 'Definir le domaine VTP commun a tous les switches, la version et un mot de passe pour securiser les echanges.',
                'command_template': (
                    'configure terminal\n'
                    'vtp domain {{ domain_name }}\n'
                    'vtp version {{ vtp_version }}\n'
                    'vtp password {{ vtp_password }}'
                ),
                'expected_result': 'Domaine VTP {{ domain_name }} configure avec mot de passe.',
                'warning': 'Le nom de domaine est sensible a la casse en VTP v1/v2. Utiliser le meme nom exactement sur tous les switches.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Definir le mode VTP',
                'explanation': 'Configurer le mode VTP : Server sur le switch central, Client sur les autres, Transparent sur les switches autonomes.',
                'command_template': (
                    'vtp mode {{ vtp_mode }}\n'
                    'end'
                ),
                'expected_result': 'Switch configure en mode VTP {{ vtp_mode }}.',
                'warning': 'En mode Client, les VLANs ne peuvent pas etre crees localement — ils viennent uniquement du serveur.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration VTP.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier le revision number actuel',    'command': 'show vtp status',          'expected_output': 'Configuration Revision — noter la valeur avant modification',              'order': 1},
            {'check_type': 'post',      'title': 'Verifier le statut VTP',                'command': 'show vtp status',          'expected_output': 'VTP Version: {{ vtp_version }}, Domain: {{ domain_name }}, Mode: {{ vtp_mode }}', 'order': 1},
            {'check_type': 'post',      'title': 'Verifier le mot de passe VTP',          'command': 'show vtp password',        'expected_output': 'VTP Password: {{ vtp_password }}',                                        'order': 2},
            {'check_type': 'validation','title': 'Verifier propagation VLANs (client)',   'command': 'show vlan brief',          'expected_output': 'VLANs du serveur visibles sur les switches clients',                       'order': 1},
        ],
        'rollback': {
            'conditions': 'VTP cause une perte de VLANs ou un ecrasement de la base VLAN.',
            'rollback_commands': (
                'configure terminal\n'
                'vtp mode transparent\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Passer en mode Transparent isole le switch du domaine VTP. Les VLANs locaux sont conserves mais ne se propagent plus.',
        },
    },

    # ── 12. Spanning Tree Basic ────────────────────────────────────────────────
    {
        'title': 'Configurer Spanning Tree (STP) et le Root Bridge',
        'summary': 'Configuration de STP PVST+ pour elire le Root Bridge optimal, eviter les boucles L2 et optimiser les chemins de commutation.',
        'objective': 'Forcer l\'election du Root Bridge STP sur le switch de distribution et configurer les parametres de temporisation pour une convergence optimale.',
        'use_cases': (
            '- Controle de l\'election du Root Bridge dans un reseau commute\n'
            '- Optimisation des chemins STP (eviter un switch d\'acces comme Root)\n'
            '- Reduction du temps de convergence STP\n'
            '- Prevention des boucles L2 en presence de liens redondants'
        ),
        'prerequisites': (
            '- Liens trunk configures entre les switches\n'
            '- VLANs crees sur les switches\n'
            '- STP active (actif par defaut sur Cisco)\n'
            '- Topologie physique documentee'
        ),
        'expected_outcome': (
            'Le switch configure est elu Root Bridge pour les VLANs specifiques. '
            '"show spanning-tree" affiche "This bridge is the root". '
            'Aucune boucle L2 active — les ports redondants sont en etat BLK ou ALT.'
        ),
        'best_practices': (
            '- Toujours forcer le Root Bridge sur le switch de distribution (pas d\'election aleatoire)\n'
            '- Utiliser "spanning-tree vlan X root primary" plutot que de modifier la priorite manuellement\n'
            '- Activer PortFast uniquement sur les ports d\'acces (jamais sur les trunks)\n'
            '- Activer BPDU Guard sur les ports PortFast pour prevenir les attaques STP\n'
            '- Preferer RSTP (Rapid PVST+) a STP classique pour une convergence plus rapide'
        ),
        'common_pitfalls': (
            '- Laisser l\'election STP aleatoire (le switch avec le plus petit MAC devient Root)\n'
            '- Activer PortFast sur un port trunk (boucle possible)\n'
            '- Modifier les timers STP sans comprendre l\'impact (diameter du reseau)\n'
            '- Oublier que STP est par VLAN avec PVST+ (chaque VLAN a son propre Root)\n'
            '- Ne pas configurer de Root secondaire (pas de redondance si le primaire tombe)'
        ),
        'notes': 'PVST+ (Per-VLAN Spanning Tree Plus) est le mode STP par defaut sur Cisco. Rapid PVST+ (802.1w) est recommande pour une convergence en moins de 2 secondes au lieu de 30-50s.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'intermediate',
        'criticality': 'high',
        'estimated_duration': 20,
        'status': 'published',
        'category': 'vlan-switching',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'vlan_range',       'label': 'VLANs concernes',         'field_type': 'text',      'placeholder': '10,20,30',           'order': 1},
            {'name': 'portfast_iface',   'label': 'Interface PortFast',      'field_type': 'interface', 'placeholder': 'FastEthernet0/1',    'order': 2},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Activer Rapid PVST+ et forcer le Root Bridge',
                'explanation': 'Passer en mode Rapid PVST+ et elire ce switch comme Root Bridge primaire pour les VLANs specifies.',
                'command_template': (
                    'configure terminal\n'
                    'spanning-tree mode rapid-pvst\n'
                    'spanning-tree vlan {{ vlan_range }} root primary'
                ),
                'expected_result': 'Switch elu Root Bridge pour VLANs {{ vlan_range }} avec priorite 24576 (ou inferieure a la priorite actuelle).',
                'warning': '',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Activer PortFast et BPDU Guard sur les ports d\'acces',
                'explanation': 'PortFast fait passer le port directement en Forwarding (bypass Listening/Learning). BPDU Guard desactive le port si un BPDU est recu (protection contre switches non autorises).',
                'command_template': (
                    'interface {{ portfast_iface }}\n'
                    ' spanning-tree portfast\n'
                    ' spanning-tree bpduguard enable\n'
                    'end'
                ),
                'expected_result': 'Port {{ portfast_iface }} en Forwarding immediat. Err-disabled si BPDU recu.',
                'warning': 'Ne jamais activer PortFast sur un port connecte a un autre switch ou un port trunk.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration STP.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier le Root Bridge actuel',        'command': 'show spanning-tree vlan {{ vlan_range }}',     'expected_output': 'Root ID Priority et Bridge ID — noter avant changement',                 'order': 1},
            {'check_type': 'post',      'title': 'Confirmer le Root Bridge',              'command': 'show spanning-tree vlan {{ vlan_range }}',     'expected_output': 'This bridge is the root — Priority 24576',                              'order': 1},
            {'check_type': 'post',      'title': 'Verifier les ports STP',               'command': 'show spanning-tree vlan {{ vlan_range }} detail','expected_output': 'Ports en FWD (Forwarding) ou BLK (Blocking) selon la topologie',       'order': 2},
            {'check_type': 'post',      'title': 'Verifier PortFast et BPDU Guard',      'command': 'show spanning-tree interface {{ portfast_iface }} detail', 'expected_output': 'PortFast enabled, BPDU Guard enabled',                    'order': 3},
            {'check_type': 'validation','title': 'Verifier absence de boucles',          'command': 'show spanning-tree summary',                   'expected_output': 'Aucun port en etat LOOP — topology changes recentes = 0',               'order': 1},
        ],
        'rollback': {
            'conditions': 'Changement du Root Bridge cause une reconfiguration STP non souhaitee ou une coupure.',
            'rollback_commands': (
                'configure terminal\n'
                'no spanning-tree vlan {{ vlan_range }} root primary\n'
                'spanning-tree vlan {{ vlan_range }} priority 32768\n'
                'interface {{ portfast_iface }}\n'
                ' no spanning-tree portfast\n'
                ' no spanning-tree bpduguard enable\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Reinitialiser la priorite a 32768 (valeur par defaut) relance une election STP normale.',
        },
    },

    # ── 13. OSPFv3 Configuration ───────────────────────────────────────────────
    {
        'title': 'Configurer OSPFv3 pour IPv6 sur routeur Cisco',
        'summary': 'Mise en place d\'OSPFv3 pour le routage dynamique IPv6, avec activation par interface et verification des adjacences.',
        'objective': 'Activer OSPFv3 sur les interfaces IPv6 d\'un routeur Cisco pour etablir des adjacences et propager les routes IPv6 dynamiquement.',
        'use_cases': (
            '- Routage IPv6 dynamique dans un reseau d\'entreprise\n'
            '- Migration IPv4 OSPF vers dual-stack OSPFv3\n'
            '- Remplacement des routes statiques IPv6 par un protocole dynamique\n'
            '- Labos CCNP IPv6 / OSPFv3'
        ),
        'prerequisites': (
            '- IPv6 unicast-routing active\n'
            '- Interfaces IPv6 configurees et up\n'
            '- Connectivite IPv6 entre les routeurs (link-local fonctionne)\n'
            '- Meme area OSPFv3 sur les interfaces connectees'
        ),
        'expected_outcome': (
            'Les adjacences OSPFv3 sont etablies (etat FULL). '
            '"show ipv6 route ospf" affiche des routes "O" apprises. '
            'La connectivite IPv6 entre tous les routeurs est fonctionnelle.'
        ),
        'best_practices': (
            '- Configurer un Router-ID explicite (adresse IPv4 loopback ou statique)\n'
            '- Activer OSPFv3 directement sur les interfaces (pas de commande "network")\n'
            '- Utiliser des interfaces passive sur les segments LAN\n'
            '- Verifier que les link-local sont joignables entre voisins\n'
            '- Documenter le process ID et le Router-ID de chaque routeur'
        ),
        'common_pitfalls': (
            '- Oublier "ipv6 unicast-routing" (routage IPv6 inactif)\n'
            '- Pas de Router-ID configure et aucune adresse IPv4 sur le routeur (OSPFv3 ne demarre pas)\n'
            '- Area differente entre deux routeurs voisins (adjacence impossible)\n'
            '- Utiliser la syntaxe OSPFv2 (network command) qui ne fonctionne pas pour OSPFv3\n'
            '- Confondre le process ID OSPFv3 avec l\'AS number'
        ),
        'notes': 'OSPFv3 utilise les adresses link-local pour les adjacences et les paquets Hello (pas les adresses globales). Le Router-ID reste une adresse au format IPv4 meme en OSPFv3.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'intermediate',
        'criticality': 'high',
        'estimated_duration': 25,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'process_id',      'label': 'Process ID OSPFv3',          'field_type': 'text',      'placeholder': '1',                 'order': 1},
            {'name': 'router_id',       'label': 'Router-ID (format IPv4)',    'field_type': 'ip',        'placeholder': '1.1.1.1',           'order': 2},
            {'name': 'interface_wan',   'label': 'Interface vers voisin OSPF', 'field_type': 'interface', 'placeholder': 'GigabitEthernet0/0','order': 3},
            {'name': 'area_id',         'label': 'Numero d\'area',             'field_type': 'text',      'placeholder': '0',                 'order': 4},
            {'name': 'passive_iface',   'label': 'Interface passive (LAN)',    'field_type': 'interface', 'placeholder': 'GigabitEthernet0/1','order': 5},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Creer le processus OSPFv3 et definir le Router-ID',
                'explanation': 'Demarrer le processus OSPFv3 et assigner un Router-ID stable au format IPv4.',
                'command_template': (
                    'configure terminal\n'
                    'ipv6 router ospf {{ process_id }}\n'
                    ' router-id {{ router_id }}'
                ),
                'expected_result': 'Processus OSPFv3 {{ process_id }} actif avec Router-ID {{ router_id }}.',
                'warning': 'Sans Router-ID et sans adresse IPv4 sur le routeur, OSPFv3 ne demarre pas.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Activer OSPFv3 sur les interfaces',
                'explanation': 'Contrairement a OSPFv2, OSPFv3 s\'active directement sur les interfaces (pas de commande "network").',
                'command_template': (
                    'interface {{ interface_wan }}\n'
                    ' ipv6 ospf {{ process_id }} area {{ area_id }}\n'
                    'interface {{ passive_iface }}\n'
                    ' ipv6 ospf {{ process_id }} area {{ area_id }}'
                ),
                'expected_result': 'OSPFv3 actif sur les deux interfaces. Hellos envoyes sur {{ interface_wan }}.',
                'warning': '',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer l\'interface passive et sauvegarder',
                'explanation': 'Empecher l\'envoi de Hellos OSPFv3 sur l\'interface LAN (inutile et non securise).',
                'command_template': (
                    'ipv6 router ospf {{ process_id }}\n'
                    ' passive-interface {{ passive_iface }}\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Aucun Hello OSPFv3 sur {{ passive_iface }}. Configuration sauvegardee.',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier IPv6 unicast-routing',        'command': 'show running-config | include ipv6 unicast',  'expected_output': 'ipv6 unicast-routing',                                              'order': 1},
            {'check_type': 'pre',       'title': 'Verifier les adresses IPv6',           'command': 'show ipv6 interface brief',                   'expected_output': 'Interfaces up avec adresses IPv6 (globale + link-local)',           'order': 2},
            {'check_type': 'post',      'title': 'Verifier les voisins OSPFv3',          'command': 'show ipv6 ospf neighbor',                     'expected_output': 'Voisins en etat FULL/DR ou FULL/BDR',                              'order': 1},
            {'check_type': 'post',      'title': 'Verifier les routes OSPFv3',           'command': 'show ipv6 route ospf',                        'expected_output': 'Routes "O" apprises depuis les voisins OSPFv3',                    'order': 2},
            {'check_type': 'validation','title': 'Ping IPv6 vers reseau distant',        'command': 'ping ipv6 <adresse_ipv6_destination>',        'expected_output': 'Success rate is 100 percent (5/5)',                                'order': 1},
        ],
        'rollback': {
            'conditions': 'OSPFv3 cause des problemes de routage IPv6 ou des adjacences incorrectes.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ interface_wan }}\n'
                ' no ipv6 ospf {{ process_id }} area {{ area_id }}\n'
                'interface {{ passive_iface }}\n'
                ' no ipv6 ospf {{ process_id }} area {{ area_id }}\n'
                'no ipv6 router ospf {{ process_id }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'La suppression du processus OSPFv3 retire toutes les routes apprises via ce protocole.',
        },
    },

    # ── 14. eBGP Configuration ────────────────────────────────────────────────
    {
        'title': 'Configurer eBGP entre deux AS Cisco',
        'summary': 'Mise en place d\'une session eBGP (External BGP) entre deux routeurs Cisco appartenant a des AS differents pour l\'echange de routes inter-domaine.',
        'objective': 'Etablir une peering eBGP entre deux routeurs, annoncer un reseau et verifier la table BGP et la propagation des routes.',
        'use_cases': (
            '- Connexion a un FAI via BGP\n'
            '- Interconnexion de deux entreprises avec leurs propres AS\n'
            '- Multi-homing (connexion a plusieurs FAI)\n'
            '- Labos CCNP BGP preparation'
        ),
        'prerequisites': (
            '- Connectivite IP directe entre les deux routeurs (meme subnet)\n'
            '- Numeros d\'AS publics ou prives assignes (AS prives : 64512-65535)\n'
            '- Interfaces configurees et up\n'
            '- Accord sur les prefixes a echanger'
        ),
        'expected_outcome': (
            'La session BGP est etablie (etat Established). '
            '"show ip bgp summary" affiche l\'etat Up/Down avec prefixes recus (PfxRcd > 0). '
            'Les routes BGP apparaissent dans la table de routage avec le tag "B".'
        ),
        'best_practices': (
            '- Utiliser des adresses de loopback pour les sessions iBGP (pas pour eBGP direct)\n'
            '- Activer l\'authentification MD5 BGP entre les pairs\n'
            '- Appliquer des prefix-lists pour filtrer les routes annoncees/recues\n'
            '- Ne jamais annoncer des routes par defaut sans verification\n'
            '- Documenter les politiques de routage (communities, prepend, local-pref)'
        ),
        'common_pitfalls': (
            '- Mauvais AS number du voisin (session refuse)\n'
            '- Adresse du neighbor incorrecte ou non joignable\n'
            '- Pas de route reseau annoncee (BGP n\'annonce rien sans "network" ou redistribution)\n'
            '- Oublier que eBGP TTL = 1 par defaut (voisins directement connectes uniquement)\n'
            '- Synchronisation BGP activee (IOS anciens) bloquant les routes BGP'
        ),
        'notes': 'BGP est le protocole de routage d\'Internet (EGP). La commande "network" en BGP n\'active pas BGP sur une interface — elle annonce un prefixe specifique qui doit exister dans la table de routage.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'advanced',
        'criticality': 'critical',
        'estimated_duration': 30,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'local_as',        'label': 'AS local',                  'field_type': 'text', 'placeholder': '65001',         'order': 1},
            {'name': 'neighbor_ip',     'label': 'IP du voisin eBGP',         'field_type': 'ip',   'placeholder': '203.0.113.2',   'order': 2},
            {'name': 'remote_as',       'label': 'AS du voisin (remote AS)',  'field_type': 'text', 'placeholder': '65002',         'order': 3},
            {'name': 'network_prefix',  'label': 'Prefixe a annoncer',        'field_type': 'ip',   'placeholder': '192.168.1.0',   'order': 4},
            {'name': 'network_mask',    'label': 'Masque du prefixe',         'field_type': 'text', 'placeholder': '255.255.255.0', 'order': 5},
            {'name': 'bgp_password',    'label': 'Mot de passe MD5 BGP',      'field_type': 'text', 'placeholder': 'BGP$ecret!',    'order': 6},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer le processus BGP et le voisin eBGP',
                'explanation': 'Creer le processus BGP avec l\'AS local et declarer le voisin eBGP avec son AS et l\'authentification MD5.',
                'command_template': (
                    'configure terminal\n'
                    'router bgp {{ local_as }}\n'
                    ' bgp router-id {{ neighbor_ip }}\n'
                    ' no bgp synchronization\n'
                    ' neighbor {{ neighbor_ip }} remote-as {{ remote_as }}\n'
                    ' neighbor {{ neighbor_ip }} password {{ bgp_password }}\n'
                    ' neighbor {{ neighbor_ip }} description eBGP-PEER-AS{{ remote_as }}'
                ),
                'expected_result': 'Session BGP initiee vers {{ neighbor_ip }}. Etat Active ou Connect en attente du voisin.',
                'warning': 'Les deux cotes doivent etre configures pour que la session passe en Established.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Annoncer le prefixe dans BGP',
                'explanation': 'Declarer le reseau a propager au voisin eBGP. Le prefixe doit exister dans la table de routage locale.',
                'command_template': (
                    ' network {{ network_prefix }} mask {{ network_mask }}\n'
                    'end'
                ),
                'expected_result': 'Prefixe {{ network_prefix }}/{{ network_mask }} annonce au voisin {{ neighbor_ip }}.',
                'warning': 'Si la route n\'existe pas dans la table de routage, elle ne sera pas annoncee.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration BGP.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier connectivite vers le voisin', 'command': 'ping {{ neighbor_ip }}',               'expected_output': 'Success rate is 100 percent',                                              'order': 1},
            {'check_type': 'post',      'title': 'Verifier la session BGP',              'command': 'show ip bgp summary',                  'expected_output': '{{ neighbor_ip }} AS{{ remote_as }} — Etat: Established, PfxRcd > 0',      'order': 1},
            {'check_type': 'post',      'title': 'Verifier la table BGP',                'command': 'show ip bgp',                          'expected_output': 'Prefixe {{ network_prefix }} avec next-hop {{ neighbor_ip }}, status >',    'order': 2},
            {'check_type': 'post',      'title': 'Verifier les routes BGP dans la RIB',  'command': 'show ip route bgp',                    'expected_output': 'Routes "B" apprises via {{ neighbor_ip }}',                               'order': 3},
            {'check_type': 'validation','title': 'Ping destination via route BGP',       'command': 'ping {{ network_prefix }}',            'expected_output': 'Success rate is 100 percent (5/5)',                                        'order': 1},
            {'check_type': 'troubleshooting','title': 'Debugger session BGP',            'command': 'debug ip bgp {{ neighbor_ip }} events', 'expected_output': 'Messages d\'etablissement — desactiver avec undebug all apres usage',    'order': 1},
        ],
        'rollback': {
            'conditions': 'La session BGP cause des annonces de routes incorrectes ou une perte de connectivite.',
            'rollback_commands': (
                'configure terminal\n'
                'router bgp {{ local_as }}\n'
                ' no neighbor {{ neighbor_ip }} remote-as {{ remote_as }}\n'
                ' no network {{ network_prefix }} mask {{ network_mask }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Supprimer le neighbor ferme immediatement la session BGP. Les routes apprises sont retirees de la table de routage.',
        },
    },

    # ── 15. NTP Configuration ─────────────────────────────────────────────────
    {
        'title': 'Configurer NTP sur equipement Cisco',
        'summary': 'Synchronisation de l\'horloge des equipements Cisco avec un serveur NTP pour assurer la coherence des logs et l\'authentification Kerberos/PKI.',
        'objective': 'Configurer un ou plusieurs serveurs NTP sur un equipement Cisco, verifier la synchronisation et configurer le fuseau horaire.',
        'use_cases': (
            '- Coherence des timestamps dans les logs Syslog\n'
            '- Prerequis pour les protocoles d\'authentification (Kerberos, certificats PKI)\n'
            '- Correlation d\'evenements entre equipements lors d\'incidents\n'
            '- Conformite aux audits de securite (ANSSI, PCI-DSS, ISO 27001)'
        ),
        'prerequisites': (
            '- Connectivite IP vers le(s) serveur(s) NTP\n'
            '- Port UDP/123 ouvert entre l\'equipement et le serveur NTP\n'
            '- Droits privilege 15\n'
            '- Serveur NTP disponible (interne ou public : pool.ntp.org)'
        ),
        'expected_outcome': (
            '"show ntp status" affiche "Clock is synchronized" avec la stratum du serveur. '
            '"show clock" affiche l\'heure correcte avec le fuseau horaire configure. '
            'L\'heure se synchronise en moins de 5 minutes apres configuration.'
        ),
        'best_practices': (
            '- Utiliser un serveur NTP interne plutot que des serveurs publics\n'
            '- Configurer au moins deux serveurs NTP pour la redondance\n'
            '- Activer l\'authentification NTP avec une cle MD5\n'
            '- Utiliser "ntp server prefer" pour indiquer le serveur principal\n'
            '- Configurer le fuseau horaire et l\'heure d\'ete (clock timezone / clock summer-time)'
        ),
        'common_pitfalls': (
            '- Port UDP 123 bloque par une ACL (NTP ne se synchronise pas sans log d\'erreur apparent)\n'
            '- Serveur NTP injoignable (verifier la route et le ping)\n'
            '- Fuseau horaire non configure (logs en UTC par defaut)\n'
            '- L\'equipement est lui-meme source NTP non desiree (ajouter "ntp master" seulement si necessaire)\n'
            '- Delai de synchronisation non attendu (jusqu\'a 5-15 min pour la premiere sync)'
        ),
        'notes': 'NTP utilise une hierarchie de "stratum". Un serveur de stratum 1 est connecte directement a une horloge atomique. Les routeurs Cisco bien synchronises sont en stratum 2-4.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'beginner',
        'criticality': 'medium',
        'estimated_duration': 15,
        'status': 'published',
        'category': 'supervision',
        'is_featured': False,
        'requires_maintenance_window': False,
        'save_config_required': True,
        'variables': [
            {'name': 'ntp_server1',   'label': 'Serveur NTP primaire',     'field_type': 'ip',   'placeholder': '192.168.1.100',  'order': 1},
            {'name': 'ntp_server2',   'label': 'Serveur NTP secondaire',   'field_type': 'ip',   'placeholder': '192.168.1.101',  'order': 2},
            {'name': 'timezone',      'label': 'Fuseau horaire (nom)',      'field_type': 'text', 'placeholder': 'CET',            'order': 3},
            {'name': 'tz_offset',     'label': 'Decalage UTC (heures)',     'field_type': 'text', 'placeholder': '1',              'order': 4},
            {'name': 'ntp_key_id',    'label': 'ID de cle NTP',            'field_type': 'text', 'placeholder': '1',              'order': 5},
            {'name': 'ntp_key_value', 'label': 'Valeur de la cle NTP',     'field_type': 'text', 'placeholder': 'NTP$ecretKey',   'order': 6},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer le fuseau horaire',
                'explanation': 'Definir le fuseau horaire local pour que les logs affichent l\'heure locale et non UTC.',
                'command_template': (
                    'configure terminal\n'
                    'clock timezone {{ timezone }} {{ tz_offset }}\n'
                    'clock summer-time {{ timezone }}DT recurring'
                ),
                'expected_result': 'Fuseau horaire {{ timezone }} UTC+{{ tz_offset }} configure avec heure d\'ete automatique.',
                'warning': '',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Configurer l\'authentification NTP',
                'explanation': 'Activer l\'authentification NTP avec une cle MD5 pour securiser la synchronisation.',
                'command_template': (
                    'ntp authenticate\n'
                    'ntp authentication-key {{ ntp_key_id }} md5 {{ ntp_key_value }}\n'
                    'ntp trusted-key {{ ntp_key_id }}'
                ),
                'expected_result': 'Authentification NTP activee avec la cle {{ ntp_key_id }}.',
                'warning': 'Le serveur NTP doit aussi etre configure avec la meme cle pour que l\'authentification fonctionne.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer les serveurs NTP',
                'explanation': 'Pointer l\'equipement vers les serveurs NTP avec le serveur primaire en "prefer".',
                'command_template': (
                    'ntp server {{ ntp_server1 }} key {{ ntp_key_id }} prefer\n'
                    'ntp server {{ ntp_server2 }} key {{ ntp_key_id }}\n'
                    'end'
                ),
                'expected_result': 'Equipement en cours de synchronisation vers {{ ntp_server1 }} (prefer) et {{ ntp_server2 }} (backup).',
                'warning': 'La synchronisation peut prendre jusqu\'a 5-15 minutes apres la premiere configuration.',
                'order': 3,
            },
            {
                'step_number': 4,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration NTP.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier connectivite vers serveur NTP', 'command': 'ping {{ ntp_server1 }}',      'expected_output': 'Success rate is 100 percent',                                           'order': 1},
            {'check_type': 'post',      'title': 'Verifier l\'etat NTP',                  'command': 'show ntp status',             'expected_output': 'Clock is synchronized, stratum X, reference is {{ ntp_server1 }}',     'order': 1},
            {'check_type': 'post',      'title': 'Verifier les associations NTP',         'command': 'show ntp associations',       'expected_output': '* indique le serveur de reference actif ({{ ntp_server1 }})',           'order': 2},
            {'check_type': 'post',      'title': 'Verifier l\'heure correcte',            'command': 'show clock detail',           'expected_output': 'Heure correcte avec fuseau {{ timezone }} — Time source is NTP',       'order': 3},
            {'check_type': 'validation','title': 'Verifier les logs avec timestamp',      'command': 'show logging | head',         'expected_output': 'Logs avec timestamps dans le bon fuseau horaire',                       'order': 1},
        ],
        'rollback': {
            'conditions': 'Mauvaise synchronisation NTP ou serveur NTP cause des problemes d\'horloge.',
            'rollback_commands': (
                'configure terminal\n'
                'no ntp server {{ ntp_server1 }}\n'
                'no ntp server {{ ntp_server2 }}\n'
                'no ntp authenticate\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Apres suppression NTP, l\'horloge conserve l\'heure actuelle mais ne se synchronise plus. Utiliser "clock set" pour ajustement manuel.',
        },
    },

    # ── 16. Advanced EIGRP ────────────────────────────────────────────────────
    {
        'title': 'Configurer EIGRP avance : summarisation et authentification',
        'summary': 'Configuration avancee d\'EIGRP avec summarisation manuelle des routes et authentification MD5 pour securiser les echanges entre routeurs.',
        'objective': 'Reduire la table de routage via la summarisation EIGRP et securiser les echanges de routes avec l\'authentification MD5 sur les interfaces.',
        'use_cases': (
            '- Reduction de la table de routage dans les grands reseaux\n'
            '- Securisation des echanges EIGRP contre les injections de routes\n'
            '- Optimisation de la convergence EIGRP\n'
            '- Environnements multi-sites avec hierarchie d\'adressage'
        ),
        'prerequisites': (
            '- EIGRP de base deja configure et fonctionnel\n'
            '- Plan d\'adressage hierarchique permettant la summarisation\n'
            '- Meme cle d\'authentification disponible sur tous les routeurs voisins\n'
            '- Droits privilege 15'
        ),
        'expected_outcome': (
            'La route resumes apparait dans "show ip route" des voisins. '
            '"show ip eigrp neighbors" indique toujours les voisins actifs. '
            '"show key chain" confirme la cle configuree.'
        ),
        'best_practices': (
            '- Toujours planifier la summarisation avant le deploiement (adressage hierarchique)\n'
            '- Configurer la summarisation des deux cotes pour symetrie\n'
            '- Utiliser des key-chains avec rotation de cles pour plus de securite\n'
            '- Tester la summarisation en lab avant production\n'
            '- Documenter les supernets annonces et leur portee'
        ),
        'common_pitfalls': (
            '- Summarisation cree une route vers Null0 (discard) sur le routeur local\n'
            '- Mauvais calcul du prefixe de summarisation (routes perdues)\n'
            '- Cle d\'authentification differente entre voisins (adjacence perdue)\n'
            '- Oublier que "no auto-summary" est necessaire avec summarisation manuelle\n'
            '- Key-chain avec mauvaise heure (time-based key rotation)'
        ),
        'notes': 'La summarisation EIGRP installe automatiquement une route vers Null0 pour le prefixe resume — comportement normal pour prevenir les boucles de routage.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'advanced',
        'criticality': 'high',
        'estimated_duration': 30,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'as_number',      'label': 'Numero AS EIGRP',           'field_type': 'text',      'placeholder': '100',               'order': 1},
            {'name': 'interface_name', 'label': 'Interface vers voisin',     'field_type': 'interface', 'placeholder': 'GigabitEthernet0/0','order': 2},
            {'name': 'summary_prefix', 'label': 'Prefixe resumes',           'field_type': 'ip',        'placeholder': '192.168.0.0',       'order': 3},
            {'name': 'summary_mask',   'label': 'Masque de summarisation',   'field_type': 'text',      'placeholder': '255.255.252.0',     'order': 4},
            {'name': 'keychain_name',  'label': 'Nom du key-chain',          'field_type': 'text',      'placeholder': 'EIGRP-AUTH',        'order': 5},
            {'name': 'key_id',         'label': 'ID de la cle',              'field_type': 'text',      'placeholder': '1',                 'order': 6},
            {'name': 'key_string',     'label': 'Valeur de la cle',          'field_type': 'text',      'placeholder': 'E1GRP$ecret',       'order': 7},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer le key-chain pour l\'authentification',
                'explanation': 'Creer un key-chain avec une cle MD5 qui sera utilisee pour authentifier les echanges EIGRP.',
                'command_template': (
                    'configure terminal\n'
                    'key chain {{ keychain_name }}\n'
                    ' key {{ key_id }}\n'
                    '  key-string {{ key_string }}'
                ),
                'expected_result': 'Key-chain {{ keychain_name }} cree avec la cle {{ key_id }}.',
                'warning': 'La valeur de cle doit etre identique sur tous les routeurs voisins EIGRP.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Appliquer l\'authentification et la summarisation sur l\'interface',
                'explanation': 'Activer l\'authentification MD5 EIGRP et configurer la summarisation manuelle sur l\'interface vers le voisin.',
                'command_template': (
                    'interface {{ interface_name }}\n'
                    ' ip authentication mode eigrp {{ as_number }} md5\n'
                    ' ip authentication key-chain eigrp {{ as_number }} {{ keychain_name }}\n'
                    ' ip summary-address eigrp {{ as_number }} {{ summary_prefix }} {{ summary_mask }}\n'
                    'end'
                ),
                'expected_result': 'Authentification MD5 active. Route resumes {{ summary_prefix }}/{{ summary_mask }} annoncee au voisin.',
                'warning': 'L\'activation de l\'authentification peut brievement interrompre l\'adjacence EIGRP le temps que le voisin soit aussi configure.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Sauvegarder',
                'explanation': 'Persister la configuration.',
                'command_template': 'copy running-config startup-config',
                'expected_result': 'Configuration sauvegardee [OK].',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier adjacence EIGRP existante',  'command': 'show ip eigrp neighbors',                      'expected_output': 'Voisins en etat Up avant modification',                       'order': 1},
            {'check_type': 'post',      'title': 'Verifier le key-chain',               'command': 'show key chain',                               'expected_output': 'Key-chain {{ keychain_name }}, key {{ key_id }} present',    'order': 1},
            {'check_type': 'post',      'title': 'Verifier l\'authentification EIGRP',  'command': 'show ip eigrp interfaces detail {{ interface_name }}', 'expected_output': 'Authentication mode is md5, key-chain {{ keychain_name }}','order': 2},
            {'check_type': 'post',      'title': 'Verifier la route resumes chez voisin','command': 'show ip route eigrp',                         'expected_output': 'Route D {{ summary_prefix }}/xx apprise via le voisin',       'order': 3},
            {'check_type': 'validation','title': 'Verifier l\'adjacence maintenue',     'command': 'show ip eigrp neighbors',                      'expected_output': 'Voisins toujours en etat Up apres activation auth',           'order': 1},
        ],
        'rollback': {
            'conditions': 'L\'authentification coupe l\'adjacence EIGRP ou la summarisation cause des problemes de routage.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ interface_name }}\n'
                ' no ip authentication mode eigrp {{ as_number }} md5\n'
                ' no ip authentication key-chain eigrp {{ as_number }} {{ keychain_name }}\n'
                ' no ip summary-address eigrp {{ as_number }} {{ summary_prefix }} {{ summary_mask }}\n'
                'no key chain {{ keychain_name }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Supprimer l\'authentification en premier pour retablir l\'adjacence, puis supprimer la summarisation.',
        },
    },

    # ── 17. Advanced OSPF ─────────────────────────────────────────────────────
    {
        'title': 'Configurer OSPF avance : areas, cost et authentification',
        'summary': 'Configuration avancee d\'OSPF avec zones multiples (area 0 + stub area), ajustement du cost et authentification MD5 des echanges.',
        'objective': 'Optimiser OSPF avec plusieurs areas pour reduire la charge LSA, ajuster les couts d\'interface et securiser les adjacences par authentification.',
        'use_cases': (
            '- Segmentation OSPF en areas pour reduire la LSDB\n'
            '- Optimisation du chemin de routage via le cost\n'
            '- Securisation des echanges OSPF en production\n'
            '- Reduction du trafic LSA dans les grandes topologies'
        ),
        'prerequisites': (
            '- OSPF de base (area 0) deja configure et fonctionnel\n'
            '- Topologie multi-routeurs avec plan d\'areas defini\n'
            '- Liens entre areas via l\'ABR (Area Border Router)\n'
            '- Droits privilege 15'
        ),
        'expected_outcome': (
            '"show ip ospf" affiche les areas configurees. '
            '"show ip ospf neighbor" montre les adjacences FULL dans toutes les areas. '
            '"show ip ospf interface" confirme l\'authentification et le cost configures.'
        ),
        'best_practices': (
            '- L\'area 0 (backbone) doit etre contigue — toutes les autres areas y sont attachees\n'
            '- Utiliser les Stub Areas pour limiter les LSA externes dans les areas de periphere\n'
            '- Ajuster le cost de reference (auto-cost reference-bandwidth) pour les liens Gig/10G\n'
            '- Authentifier OSPF sur toutes les interfaces en production\n'
            '- Documenter le Router-ID et l\'area de chaque interface'
        ),
        'common_pitfalls': (
            '- Mettre une interface dans la mauvaise area (adjacence impossible avec le voisin)\n'
            '- Cost de reference non ajuste : liens 100Mbps et 1Gbps ont le meme cout (1)\n'
            '- Mot de passe d\'authentification different entre voisins (adjacence perdue)\n'
            '- ABR non connecte a l\'area 0 (routes inter-area non propagees)\n'
            '- Stub area configuree d\'un seul cote de l\'adjacence (incompatibilite)'
        ),
        'notes': 'La commande "auto-cost reference-bandwidth" doit etre configuree sur TOUS les routeurs OSPF du domaine avec la meme valeur, sinon les couts sont incoherents.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'advanced',
        'criticality': 'high',
        'estimated_duration': 35,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'process_id',     'label': 'Process ID OSPF',           'field_type': 'text',      'placeholder': '1',                 'order': 1},
            {'name': 'area_id',        'label': 'Area additionnelle',        'field_type': 'text',      'placeholder': '1',                 'order': 2},
            {'name': 'network_area',   'label': 'Reseau dans la nouvelle area','field_type': 'ip',      'placeholder': '10.1.1.0',          'order': 3},
            {'name': 'wildcard_area',  'label': 'Wildcard',                  'field_type': 'text',      'placeholder': '0.0.0.255',         'order': 4},
            {'name': 'iface_cost',     'label': 'Interface a ajuster (cost)','field_type': 'interface', 'placeholder': 'GigabitEthernet0/1','order': 5},
            {'name': 'cost_value',     'label': 'Valeur du cost',            'field_type': 'text',      'placeholder': '10',                'order': 6},
            {'name': 'auth_iface',     'label': 'Interface a authentifier',  'field_type': 'interface', 'placeholder': 'GigabitEthernet0/0','order': 7},
            {'name': 'auth_password',  'label': 'Mot de passe OSPF MD5',     'field_type': 'text',      'placeholder': 'OSPF$ecret',        'order': 8},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Ajuster le cout de reference OSPF',
                'explanation': 'Definir une bande passante de reference coherente avec les liens Gigabit du reseau (defaut : 100 Mbps).',
                'command_template': (
                    'configure terminal\n'
                    'router ospf {{ process_id }}\n'
                    ' auto-cost reference-bandwidth 10000\n'
                    ' area {{ area_id }} stub'
                ),
                'expected_result': 'Reference bandwidth 10 Gbps. Area {{ area_id }} configuree en stub.',
                'warning': 'Configurer la meme reference-bandwidth sur TOUS les routeurs OSPF du domaine.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Annoncer le reseau dans la nouvelle area',
                'explanation': 'Inclure le reseau de la nouvelle area dans le processus OSPF.',
                'command_template': (
                    ' network {{ network_area }} {{ wildcard_area }} area {{ area_id }}\n'
                    'end'
                ),
                'expected_result': 'Reseau {{ network_area }} annonce dans l\'area {{ area_id }}.',
                'warning': '',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Ajuster le cost sur une interface et activer l\'authentification',
                'explanation': 'Forcer un chemin prefere via le cost et securiser les adjacences OSPF avec MD5.',
                'command_template': (
                    'interface {{ iface_cost }}\n'
                    ' ip ospf cost {{ cost_value }}\n'
                    'interface {{ auth_iface }}\n'
                    ' ip ospf authentication message-digest\n'
                    ' ip ospf message-digest-key 1 md5 {{ auth_password }}\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Cost {{ cost_value }} sur {{ iface_cost }}. Authentification MD5 sur {{ auth_iface }}.',
                'warning': 'L\'authentification interrompt brievement l\'adjacence. Configurer le voisin en parallele.',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier adjacences OSPF actuelles',  'command': 'show ip ospf neighbor',                         'expected_output': 'Adjacences FULL avant modification',                             'order': 1},
            {'check_type': 'post',      'title': 'Verifier les areas OSPF',             'command': 'show ip ospf',                                  'expected_output': 'Area {{ area_id }} stub, area 0 backbone',                       'order': 1},
            {'check_type': 'post',      'title': 'Verifier le cost de l\'interface',    'command': 'show ip ospf interface {{ iface_cost }}',        'expected_output': 'Cost: {{ cost_value }}',                                         'order': 2},
            {'check_type': 'post',      'title': 'Verifier l\'authentification OSPF',   'command': 'show ip ospf interface {{ auth_iface }}',        'expected_output': 'Message digest authentication enabled — key id 1',              'order': 3},
            {'check_type': 'validation','title': 'Verifier routes inter-area',          'command': 'show ip route ospf',                            'expected_output': 'Routes "O IA" (inter-area) visibles dans la table de routage',   'order': 1},
        ],
        'rollback': {
            'conditions': 'L\'authentification OSPF coupe les adjacences ou le cost modifie cause un mauvais chemin.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ auth_iface }}\n'
                ' no ip ospf authentication message-digest\n'
                ' no ip ospf message-digest-key 1 md5 {{ auth_password }}\n'
                'interface {{ iface_cost }}\n'
                ' no ip ospf cost\n'
                'router ospf {{ process_id }}\n'
                ' no auto-cost reference-bandwidth\n'
                ' no area {{ area_id }} stub\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Supprimer l\'authentification en premier pour retablir les adjacences avant de toucher aux autres parametres.',
        },
    },

    # ── 18. Basic Redistribution ───────────────────────────────────────────────
    {
        'title': 'Configurer la redistribution de routes entre protocoles',
        'summary': 'Redistribution bidirectionnelle de routes entre deux protocoles de routage (OSPF et EIGRP) via un routeur frontiere.',
        'objective': 'Permettre l\'echange de routes entre deux domaines de routage differents (OSPF <-> EIGRP) en configurant la redistribution sur le routeur frontiere.',
        'use_cases': (
            '- Migration progressive d\'un protocole vers un autre\n'
            '- Interconnexion de domaines de routage heterogenes\n'
            '- Fusion de reseaux d\'entreprises avec des protocoles differents\n'
            '- Architecture ou coexistent OSPF (WAN) et EIGRP (LAN)'
        ),
        'prerequisites': (
            '- Les deux protocoles de routage configures et fonctionnels\n'
            '- Routeur frontiere avec acces aux deux domaines\n'
            '- Comprehension des metriques des deux protocoles\n'
            '- Plan de filtrage pour eviter les boucles de redistribution'
        ),
        'expected_outcome': (
            'Les routes OSPF apparaissent dans la table EIGRP avec le tag "D EX" (externe). '
            'Les routes EIGRP apparaissent dans la table OSPF avec le tag "O E2" (externe type 2). '
            'La connectivite entre les deux domaines est etablie.'
        ),
        'best_practices': (
            '- Toujours utiliser des route-maps avec tag pour identifier les routes redistribuees\n'
            '- Filtrer les routes redistribuees pour eviter les boucles (deny les routes taggees)\n'
            '- Definir des metriques explicites lors de la redistribution\n'
            '- Tester la redistribution dans un lab avant la production\n'
            '- Documenter clairement les politiques de redistribution'
        ),
        'common_pitfalls': (
            '- Boucles de redistribution (routes redistribuees dans les deux sens sans filtre)\n'
            '- Metrique incorrecte pour EIGRP (5 parametres requis : bw, delay, reliability, load, mtu)\n'
            '- Routes sous-optimales dues aux metriques arbitraires de redistribution\n'
            '- Redistribution de la route par defaut accidentellement\n'
            '- Oublier "subnets" pour OSPF (sinon seules les routes classful sont redistribuees)'
        ),
        'notes': 'La commande "subnets" est obligatoire lors de la redistribution vers OSPF pour inclure les routes sans classe (VLSM). Sans "subnets", seules les routes de classe A/B/C sont redistribuees.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'advanced',
        'criticality': 'critical',
        'estimated_duration': 35,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'ospf_pid',      'label': 'Process ID OSPF',              'field_type': 'text', 'placeholder': '1',    'order': 1},
            {'name': 'eigrp_as',      'label': 'AS EIGRP',                     'field_type': 'text', 'placeholder': '100',  'order': 2},
            {'name': 'ospf_metric',   'label': 'Metrique OSPF externe (seed)', 'field_type': 'text', 'placeholder': '100',  'order': 3},
            {'name': 'eigrp_bw',      'label': 'Bande passante EIGRP (kbps)',  'field_type': 'text', 'placeholder': '1000', 'order': 4},
            {'name': 'eigrp_delay',   'label': 'Delai EIGRP (10us)',           'field_type': 'text', 'placeholder': '100',  'order': 5},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Redistribuer EIGRP dans OSPF',
                'explanation': 'Injecter les routes EIGRP dans le domaine OSPF. "subnets" est obligatoire pour inclure toutes les routes VLSM.',
                'command_template': (
                    'configure terminal\n'
                    'router ospf {{ ospf_pid }}\n'
                    ' redistribute eigrp {{ eigrp_as }} metric {{ ospf_metric }} metric-type 2 subnets\n'
                    ' redistribute eigrp {{ eigrp_as }} tag 100'
                ),
                'expected_result': 'Routes EIGRP injectees dans OSPF avec metrique {{ ospf_metric }} (type E2).',
                'warning': 'Ne pas oublier "subnets" sinon seules les routes classful (A/B/C) sont redistribuees.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Redistribuer OSPF dans EIGRP',
                'explanation': 'Injecter les routes OSPF dans le domaine EIGRP avec une metrique EIGRP explicite (5 parametres).',
                'command_template': (
                    'router eigrp {{ eigrp_as }}\n'
                    ' redistribute ospf {{ ospf_pid }} metric {{ eigrp_bw }} {{ eigrp_delay }} 255 1 1500\n'
                    ' redistribute ospf {{ ospf_pid }} route-map DENY-OSPF-TAG\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Routes OSPF injectees dans EIGRP avec la metrique fournie.',
                'warning': 'Les 5 parametres de metrique EIGRP sont obligatoires : bandwidth, delay, reliability, load, MTU.',
                'order': 2,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier les deux tables de routage', 'command': 'show ip route',             'expected_output': 'Routes OSPF et EIGRP presentes mais limitees a leurs domaines respectifs',  'order': 1},
            {'check_type': 'post',      'title': 'Verifier routes EIGRP dans OSPF',    'command': 'show ip route ospf',        'expected_output': 'Routes "O E2" correspondant aux reseaux EIGRP',                           'order': 1},
            {'check_type': 'post',      'title': 'Verifier routes OSPF dans EIGRP',    'command': 'show ip route eigrp',       'expected_output': 'Routes "D EX" correspondant aux reseaux OSPF',                           'order': 2},
            {'check_type': 'validation','title': 'Connectivite cross-domaine',          'command': 'ping <ip_reseau_distant>',  'expected_output': 'Success rate is 100 percent (5/5)',                                       'order': 1},
        ],
        'rollback': {
            'conditions': 'La redistribution cause des boucles ou des routes sous-optimales.',
            'rollback_commands': (
                'configure terminal\n'
                'router ospf {{ ospf_pid }}\n'
                ' no redistribute eigrp {{ eigrp_as }}\n'
                'router eigrp {{ eigrp_as }}\n'
                ' no redistribute ospf {{ ospf_pid }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Supprimer la redistribution des deux cotes simultanement pour eviter des routes transitoires indesirables.',
        },
    },

    # ── 19. Policy Based Routing ───────────────────────────────────────────────
    {
        'title': 'Configurer le Policy Based Routing (PBR)',
        'summary': 'Mise en place du routage base sur des politiques pour forcer certains flux vers un next-hop specifique, independamment de la table de routage.',
        'objective': 'Creer une route-map PBR pour rediriger un trafic specifique (source, application) vers un next-hop different de celui calcule par le protocole de routage.',
        'use_cases': (
            '- Forcer le trafic HTTP/HTTPS vers un proxy ou un FAI specifique\n'
            '- Routage de trafic voix vers un lien MPLS dedie\n'
            '- Load balancing entre deux FAI selon la source\n'
            '- Contournement d\'equipements specifiques pour certains flux'
        ),
        'prerequisites': (
            '- Interfaces configurees avec adresses IP et up\n'
            '- Next-hop(s) joignables\n'
            '- ACL definissant le trafic a router via PBR\n'
            '- Droits privilege 15'
        ),
        'expected_outcome': (
            '"show ip policy" affiche la route-map appliquee sur l\'interface. '
            '"debug ip policy" confirme que le trafic correspondant suit le next-hop PBR. '
            'Le trafic non matche suit la table de routage normale.'
        ),
        'best_practices': (
            '- Toujours terminer la route-map par un "permit" sans set (trafic non matche passe en routing normal)\n'
            '- Tester avec "debug ip policy" en lab avant production\n'
            '- Utiliser des ACL nommees pour plus de lisibilite\n'
            '- Configurer un second next-hop de secours avec "set ip next-hop verify-reachability"\n'
            '- Documenter clairement quels flux sont affectes par le PBR'
        ),
        'common_pitfalls': (
            '- PBR s\'applique au trafic TRANSIT (entrant sur l\'interface) pas au trafic LOCAL du routeur\n'
            '- Next-hop PBR injoignable : trafic drope si verify-reachability est active\n'
            '- Oublier le dernier "permit" dans la route-map (tout le trafic non matche est drope)\n'
            '- ACL incorrecte matchant plus de trafic que prevu\n'
            '- Appliquer PBR sur la mauvaise interface (sortante au lieu d\'entrante)'
        ),
        'notes': 'PBR s\'applique sur l\'interface ENTRANT le trafic (ingress). Le routeur examine d\'abord la route-map PBR, puis la table de routage si aucun match.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'advanced',
        'criticality': 'high',
        'estimated_duration': 30,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'acl_name',       'label': 'Nom de l\'ACL de match',     'field_type': 'text',      'placeholder': 'ACL-PBR-HTTP',      'order': 1},
            {'name': 'src_network',    'label': 'Reseau source a router',     'field_type': 'ip',        'placeholder': '192.168.10.0',      'order': 2},
            {'name': 'src_wildcard',   'label': 'Wildcard source',            'field_type': 'text',      'placeholder': '0.0.0.255',         'order': 3},
            {'name': 'pbr_nexthop',    'label': 'Next-hop PBR',              'field_type': 'ip',        'placeholder': '10.0.0.2',          'order': 4},
            {'name': 'routemap_name',  'label': 'Nom de la route-map',       'field_type': 'text',      'placeholder': 'PBR-POLICY',        'order': 5},
            {'name': 'apply_iface',    'label': 'Interface d\'application',  'field_type': 'interface', 'placeholder': 'GigabitEthernet0/1','order': 6},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Creer l\'ACL definissant le trafic a intercepter',
                'explanation': 'Definir le trafic qui sera soumis au PBR (source, destination ou protocole).',
                'command_template': (
                    'configure terminal\n'
                    'ip access-list extended {{ acl_name }}\n'
                    ' permit ip {{ src_network }} {{ src_wildcard }} any\n'
                    ' deny ip any any'
                ),
                'expected_result': 'ACL {{ acl_name }} creee — matche le trafic du reseau {{ src_network }}.',
                'warning': '',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Creer la route-map PBR',
                'explanation': 'Definir la route-map qui force le next-hop pour le trafic matche, avec un permit final pour laisser passer le reste.',
                'command_template': (
                    'route-map {{ routemap_name }} permit 10\n'
                    ' match ip address {{ acl_name }}\n'
                    ' set ip next-hop verify-reachability {{ pbr_nexthop }}\n'
                    'route-map {{ routemap_name }} permit 20'
                ),
                'expected_result': 'Route-map {{ routemap_name }} creee : seq 10 redirige vers {{ pbr_nexthop }}, seq 20 laisse passer le reste.',
                'warning': 'La clause "permit 20" sans action est indispensable pour ne pas dropper le trafic non matche.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Appliquer la route-map sur l\'interface',
                'explanation': 'Lier la route-map PBR a l\'interface sur laquelle arrive le trafic a rediriger.',
                'command_template': (
                    'interface {{ apply_iface }}\n'
                    ' ip policy route-map {{ routemap_name }}\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'PBR actif sur {{ apply_iface }}. Trafic {{ src_network }} redirige vers {{ pbr_nexthop }}.',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier joignabilite du next-hop PBR','command': 'ping {{ pbr_nexthop }}',                       'expected_output': 'Success rate is 100 percent',                                    'order': 1},
            {'check_type': 'post',      'title': 'Verifier la policy sur l\'interface',  'command': 'show ip policy',                               'expected_output': '{{ apply_iface }}: route-map {{ routemap_name }}',               'order': 1},
            {'check_type': 'post',      'title': 'Verifier la route-map',                'command': 'show route-map {{ routemap_name }}',            'expected_output': 'Match: ip address {{ acl_name }}, Set: ip next-hop {{ pbr_nexthop }}','order': 2},
            {'check_type': 'validation','title': 'Tracer le chemin du trafic PBR',       'command': 'debug ip policy',                              'expected_output': 'Trafic source {{ src_network }} route via {{ pbr_nexthop }} (PBR match)', 'order': 1},
        ],
        'rollback': {
            'conditions': 'Le PBR cause des problemes de connectivite ou le next-hop PBR est injoignable.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ apply_iface }}\n'
                ' no ip policy route-map {{ routemap_name }}\n'
                'no route-map {{ routemap_name }}\n'
                'no ip access-list extended {{ acl_name }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Supprimer d\'abord l\'application sur l\'interface, puis la route-map et l\'ACL.',
        },
    },

    # ── 20. DHCP Snooping ─────────────────────────────────────────────────────
    {
        'title': 'Configurer DHCP Snooping sur switch Cisco',
        'summary': 'Activation du DHCP Snooping pour proteger le reseau contre les serveurs DHCP frauduleux et les attaques DHCP starvation.',
        'objective': 'Activer DHCP Snooping sur les VLANs critiques, definir les ports de confiance (trusted) et bloquer les DHCP Offer non autorises sur les ports non fiables.',
        'use_cases': (
            '- Protection contre les serveurs DHCP rogue (pirates)\n'
            '- Prevention des attaques DHCP starvation\n'
            '- Base pour Dynamic ARP Inspection (DAI) et IP Source Guard\n'
            '- Conformite securite reseau (PCI-DSS, ISO 27001)'
        ),
        'prerequisites': (
            '- VLANs concernes deja configures sur le switch\n'
            '- Port vers le vrai serveur DHCP identifie (sera trusted)\n'
            '- Acces privilege 15\n'
            '- Topologie documentee (ports uplink vs ports acces)'
        ),
        'expected_outcome': (
            '"show ip dhcp snooping" affiche DHCP Snooping enabled sur les VLANs configures. '
            'Les ports trusted laissent passer les Offer DHCP. '
            'Les ports untrusted droppent silencieusement les Offer DHCP frauduleux.'
        ),
        'best_practices': (
            '- Marquer trusted uniquement les ports uplink et ports vers le serveur DHCP\n'
            '- Activer le rate-limiting sur les ports untrusted (protection starvation)\n'
            '- Activer l\'option 82 uniquement si le serveur DHCP le supporte\n'
            '- Combiner avec Dynamic ARP Inspection (DAI) pour une protection complete\n'
            '- Sauvegarder la base DHCP Snooping sur flash pour persistence apres reboot'
        ),
        'common_pitfalls': (
            '- Marquer tous les ports en trusted (annule la protection)\n'
            '- Oublier de marquer l\'uplink vers le switch distribution en trusted (DHCP bloque)\n'
            '- Option 82 activee mais serveur DHCP ne la supporte pas (requetes droppees)\n'
            '- Ne pas sauvegarder la base snooping (perte des baux apres reboot)\n'
            '- Rate-limiting trop restrictif perturbant le renouvellement des baux'
        ),
        'notes': 'DHCP Snooping construit une table de correspondance MAC-IP-VLAN-Port utilisee ensuite par Dynamic ARP Inspection (DAI) et IP Source Guard pour une protection L2 complete.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'intermediate',
        'criticality': 'high',
        'estimated_duration': 20,
        'status': 'published',
        'category': 'securite-acl',
        'is_featured': False,
        'requires_maintenance_window': False,
        'save_config_required': True,
        'variables': [
            {'name': 'vlan_range',     'label': 'VLANs a proteger',          'field_type': 'text',      'placeholder': '10,20,30',           'order': 1},
            {'name': 'trusted_port',   'label': 'Port trusted (uplink/DHCP)','field_type': 'interface', 'placeholder': 'GigabitEthernet0/24','order': 2},
            {'name': 'untrusted_port', 'label': 'Port untrusted (acces)',    'field_type': 'interface', 'placeholder': 'FastEthernet0/1',    'order': 3},
            {'name': 'rate_limit',     'label': 'Rate-limit paquets/s',      'field_type': 'text',      'placeholder': '15',                 'order': 4},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Activer DHCP Snooping globalement et sur les VLANs',
                'explanation': 'Activer le service DHCP Snooping et le restreindre aux VLANs a proteger.',
                'command_template': (
                    'configure terminal\n'
                    'ip dhcp snooping\n'
                    'ip dhcp snooping vlan {{ vlan_range }}\n'
                    'no ip dhcp snooping information option'
                ),
                'expected_result': 'DHCP Snooping actif sur VLANs {{ vlan_range }}. Option 82 desactivee (compatibilite).',
                'warning': 'Sans "no ip dhcp snooping information option", certains serveurs DHCP rejettent les requetes avec Option 82.',
                'order': 1,
                'real_world_example': 'Exemple : un etudiant branche son Raspberry Pi sur le reseau de l\'entreprise et lance un faux serveur DHCP dessus. Sans DHCP Snooping, les autres PCs pourraient obtenir une fausse passerelle de cet etudiant et tout leur trafic passerait par son Pi (attaque Man-in-the-Middle). Avec DHCP Snooping actif, le switch bloque automatiquement les reponses DHCP venant de ports non autorises.',
            },
            {
                'step_number': 2,
                'title': 'Configurer le port trusted et le rate-limiting',
                'explanation': 'Marquer le port uplink/DHCP en trusted et limiter le debit DHCP sur le port acces.',
                'command_template': (
                    'interface {{ trusted_port }}\n'
                    ' ip dhcp snooping trust\n'
                    'interface {{ untrusted_port }}\n'
                    ' ip dhcp snooping limit rate {{ rate_limit }}\n'
                    'end'
                ),
                'expected_result': '{{ trusted_port }} accepte les Offer DHCP. {{ untrusted_port }} limite a {{ rate_limit }} paquets/s.',
                'warning': 'Oublier "trust" sur le port uplink coupe le DHCP pour tous les hotes du VLAN.',
                'order': 2,
                'real_world_example': 'Exemple : Gi0/1 est le port qui monte vers le switch de distribution (et donc vers le vrai serveur DHCP) — c\'est lui qui doit etre "trust". Fa0/5 est le port d\'un PC employe — il reste "untrusted". Si l\'employe essaie d\'envoyer une reponse DHCP depuis son PC, le switch la bloque. Le rate-limit a 15 paquets/s empeche aussi une attaque DHCP starvation (flooding de requetes pour epuiser le pool d\'adresses).',
            },
            {
                'step_number': 3,
                'title': 'Persister la base DHCP Snooping et sauvegarder',
                'explanation': 'Ecrire la base de baux snooping sur la flash pour survie apres reboot.',
                'command_template': (
                    'ip dhcp snooping database flash:dhcp-snooping.db\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Base DHCP Snooping persistee sur flash. Configuration sauvegardee [OK].',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier le port DHCP serveur',        'command': 'show cdp neighbors {{ trusted_port }} detail',  'expected_output': 'Confirmer que le voisin est bien le switch/routeur DHCP',       'order': 1},
            {'check_type': 'post',      'title': 'Verifier DHCP Snooping global',        'command': 'show ip dhcp snooping',                         'expected_output': 'DHCP Snooping is enabled, VLANs: {{ vlan_range }}, {{ trusted_port }} trusted', 'order': 1},
            {'check_type': 'post',      'title': 'Verifier la table de binding',         'command': 'show ip dhcp snooping binding',                 'expected_output': 'Baux MAC-IP-VLAN-Port presentes apres connexion de clients',    'order': 2},
            {'check_type': 'post',      'title': 'Verifier les statistiques',            'command': 'show ip dhcp snooping statistics',              'expected_output': 'Forwarded/Dropped counters — Dropped devrait etre 0 si pas d\'attaque', 'order': 3},
            {'check_type': 'validation','title': 'Test client DHCP normal',              'command': 'show ip dhcp snooping binding',                 'expected_output': 'Client recoit une IP et apparait dans la table de binding',     'order': 1},
        ],
        'rollback': {
            'conditions': 'DHCP Snooping bloque les requetes DHCP legitimes ou cause des problemes de connectivite.',
            'rollback_commands': (
                'configure terminal\n'
                'no ip dhcp snooping vlan {{ vlan_range }}\n'
                'no ip dhcp snooping\n'
                'interface {{ untrusted_port }}\n'
                ' no ip dhcp snooping limit rate\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Desactiver d\'abord sur les VLANs, puis globalement. Verifier la connectivite DHCP apres desactivation.',
        },
    },

    # ── 21. BGP Attributes ────────────────────────────────────────────────────
    {
        'title': 'Configurer les attributs BGP : Local Preference et AS-Path Prepend',
        'summary': 'Manipulation des attributs BGP pour influencer la selection des chemins entrants (Local Preference) et sortants (AS-Path Prepend) dans un environnement multi-homed.',
        'objective': 'Utiliser Local Preference pour privilegier un chemin sortant et AS-Path Prepend pour influencer les routes entrantes depuis les AS voisins.',
        'use_cases': (
            '- Gestion du trafic sortant dans un reseau multi-homed\n'
            '- Influence des routes entrantes annoncees aux FAI\n'
            '- Optimisation du routage BGP en production\n'
            '- Scenarios CCNP ENARSI / preparation BGP avance'
        ),
        'prerequisites': (
            '- Sessions eBGP etablies avec au moins deux voisins\n'
            '- Prefixes annonces et recus fonctionnels\n'
            '- Comprehension du processus de selection BGP (weight > local-pref > AS-path > MED)\n'
            '- Droits privilege 15'
        ),
        'expected_outcome': (
            '"show ip bgp" affiche les routes avec les attributs modifies. '
            'Le chemin prefere change conformement aux Local Preference configurees. '
            '"show ip bgp regexp" confirme les AS-Path avec prepend.'
        ),
        'best_practices': (
            '- Local Preference > 100 (defaut) = chemin prefere en sortie\n'
            '- AS-Path Prepend : ajouter son propre AS pour allonger le chemin et le rendre moins attractif\n'
            '- Utiliser des route-maps avec des noms descriptifs\n'
            '- Tester les changements d\'attributs dans un lab avant la production\n'
            '- Documenter la politique de routage BGP dans un plan de routage'
        ),
        'common_pitfalls': (
            '- Confondre Local Preference (sortant) et MED (entrant)\n'
            '- AS-Path Prepend trop agressif rendant un chemin completement inattractif\n'
            '- Route-map appliquee dans la mauvaise direction (in vs out)\n'
            '- Oublier que Local Preference est un attribut iBGP (pas propage en eBGP)\n'
            '- Modifier des attributs BGP en production sans coordination avec le FAI'
        ),
        'notes': 'Local Preference est un attribut iBGP local a un AS. AS-Path Prepend est visible par tous les AS voisins. Weight est un attribut Cisco-proprietaire, local au routeur uniquement.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'advanced',
        'criticality': 'critical',
        'estimated_duration': 35,
        'status': 'published',
        'category': 'routage',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'local_as',        'label': 'AS local',                      'field_type': 'text', 'placeholder': '65001',       'order': 1},
            {'name': 'neighbor_primary','label': 'Voisin BGP primaire (prefere)', 'field_type': 'ip',   'placeholder': '203.0.113.1', 'order': 2},
            {'name': 'neighbor_backup', 'label': 'Voisin BGP backup',             'field_type': 'ip',   'placeholder': '203.0.113.5', 'order': 3},
            {'name': 'local_pref_high', 'label': 'Local Pref chemin primaire',    'field_type': 'text', 'placeholder': '200',         'order': 4},
            {'name': 'local_pref_low',  'label': 'Local Pref chemin backup',      'field_type': 'text', 'placeholder': '100',         'order': 5},
            {'name': 'prepend_count',   'label': 'Nombre de prepends (backup)',   'field_type': 'text', 'placeholder': '3',           'order': 6},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Creer les route-maps pour Local Preference',
                'explanation': 'Definir deux route-maps pour fixer la Local Preference sur les routes recues de chaque voisin — chemin primaire preferred, backup normal.',
                'command_template': (
                    'configure terminal\n'
                    'route-map SET-LOCPREF-HIGH permit 10\n'
                    ' set local-preference {{ local_pref_high }}\n'
                    'route-map SET-LOCPREF-LOW permit 10\n'
                    ' set local-preference {{ local_pref_low }}'
                ),
                'expected_result': 'Deux route-maps creees pour les Local Preferences {{ local_pref_high }} et {{ local_pref_low }}.',
                'warning': '',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Appliquer Local Preference sur les voisins BGP',
                'explanation': 'Lier les route-maps aux voisins BGP en direction "in" pour modifier la Local Preference des routes recues.',
                'command_template': (
                    'router bgp {{ local_as }}\n'
                    ' neighbor {{ neighbor_primary }} route-map SET-LOCPREF-HIGH in\n'
                    ' neighbor {{ neighbor_backup }} route-map SET-LOCPREF-LOW in'
                ),
                'expected_result': 'Routes recues de {{ neighbor_primary }} ont local-pref {{ local_pref_high }} (prefere en sortie).',
                'warning': 'Apres modification, faire "clear ip bgp {{ neighbor_primary }} soft in" pour appliquer sans couper la session.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer AS-Path Prepend sur le voisin backup',
                'explanation': 'Allonger l\'AS-Path annonce au voisin backup pour le rendre moins attractif en entree.',
                'command_template': (
                    'route-map PREPEND-BACKUP permit 10\n'
                    ' set as-path prepend {{ local_as }} {{ local_as }} {{ local_as }}\n'
                    'router bgp {{ local_as }}\n'
                    ' neighbor {{ neighbor_backup }} route-map PREPEND-BACKUP out\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'L\'AS-Path annonce a {{ neighbor_backup }} contient {{ prepend_count }} fois l\'AS {{ local_as }} supplementaire.',
                'warning': 'Appliquer le prepend "out" vers le voisin dont on veut reduire le trafic entrant.',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier sessions BGP etablies',      'command': 'show ip bgp summary',                     'expected_output': 'Etat Established pour {{ neighbor_primary }} et {{ neighbor_backup }}', 'order': 1},
            {'check_type': 'post',      'title': 'Verifier Local Preference dans BGP',  'command': 'show ip bgp',                             'expected_output': 'Routes via {{ neighbor_primary }} avec LocPrf {{ local_pref_high }}',   'order': 1},
            {'check_type': 'post',      'title': 'Verifier AS-Path Prepend',            'command': 'show ip bgp regexp _{{ local_as }}_',     'expected_output': 'Routes annoncees a {{ neighbor_backup }} avec AS-Path allonge',        'order': 2},
            {'check_type': 'validation','title': 'Verifier chemin prefere selectionne', 'command': 'show ip bgp <prefixe_recu>',              'expected_output': '> marque la route via {{ neighbor_primary }} comme best path',         'order': 1},
        ],
        'rollback': {
            'conditions': 'Les changements d\'attributs BGP causent une selection de chemin incorrecte ou une perte de connectivite.',
            'rollback_commands': (
                'configure terminal\n'
                'router bgp {{ local_as }}\n'
                ' no neighbor {{ neighbor_primary }} route-map SET-LOCPREF-HIGH in\n'
                ' no neighbor {{ neighbor_backup }} route-map SET-LOCPREF-LOW in\n'
                ' no neighbor {{ neighbor_backup }} route-map PREPEND-BACKUP out\n'
                'no route-map SET-LOCPREF-HIGH\n'
                'no route-map SET-LOCPREF-LOW\n'
                'no route-map PREPEND-BACKUP\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Faire "clear ip bgp * soft" apres suppression des route-maps pour forcer le recalcul des chemins BGP.',
        },
    },

    # ── 22. Multi-Layer Switching ──────────────────────────────────────────────
    {
        'title': 'Configurer le routage inter-VLAN sur switch multicouche (MLS)',
        'summary': 'Activation du routage IP sur un switch Catalyst multicouche (L3) avec SVIs pour chaque VLAN et une route par defaut vers le routeur edge.',
        'objective': 'Transformer un switch Catalyst en switch L3 avec routage inter-VLAN natif via les SVIs, eliminer la dependance au Router-on-a-Stick.',
        'use_cases': (
            '- Routage inter-VLAN haute performance sans routeur dedie\n'
            '- Architecture de distribution dans les campus reseaux\n'
            '- Remplacement du Router-on-a-Stick par une solution L3 native\n'
            '- Switches Catalyst 3560, 3750, 3850, 9300 en distribution'
        ),
        'prerequisites': (
            '- Switch Catalyst avec licence IP Services (ou IP Base pour OSPF)\n'
            '- VLANs crees et ports assignes\n'
            '- Plan d\'adressage avec une IP de passerelle par VLAN\n'
            '- Route par defaut ou protocole de routage vers le routeur edge'
        ),
        'expected_outcome': (
            '"show ip route" affiche les routes C connectees pour chaque SVI. '
            'Le ping inter-VLAN fonctionne sans passer par un routeur externe. '
            '"show interfaces vlan X" affiche toutes les SVIs en up/up.'
        ),
        'best_practices': (
            '- Activer "ip routing" avant de configurer les SVIs\n'
            '- Utiliser "no switchport" sur les ports routed (L3) vers les routeurs\n'
            '- Configurer une route par defaut vers le routeur edge pour Internet\n'
            '- Desactiver les SVIs des VLANs inactifs (shutdown)\n'
            '- Combiner avec OSPF ou EIGRP pour le routage dynamique vers le WAN'
        ),
        'common_pitfalls': (
            '- Oublier "ip routing" : les SVIs ont des IP mais le switch ne route pas\n'
            '- SVI en down si le VLAN n\'a aucun port actif dans cet etat\n'
            '- Pas de route par defaut : le trafic vers Internet est drope\n'
            '- Confondre "interface vlan X" (SVI) et "interface GiX/X.X" (subinterface routeur)\n'
            '- Licence insuffisante sur certains Catalyst (IP Base vs IP Services)'
        ),
        'notes': 'Sur les Catalyst, la SVI (Switch Virtual Interface) est l\'equivalent d\'une interface L3 pour un VLAN. Un seul switch peut router entre tous ses VLANs sans aucun equipement externe.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'intermediate',
        'criticality': 'high',
        'estimated_duration': 25,
        'status': 'published',
        'category': 'vlan-switching',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'vlan1_id',      'label': 'VLAN 1 ID',                  'field_type': 'vlan',      'placeholder': '10',              'order': 1},
            {'name': 'vlan1_ip',      'label': 'IP SVI VLAN 1',              'field_type': 'ip',        'placeholder': '192.168.10.1',    'order': 2},
            {'name': 'vlan1_mask',    'label': 'Masque VLAN 1',              'field_type': 'text',      'placeholder': '255.255.255.0',   'order': 3},
            {'name': 'vlan2_id',      'label': 'VLAN 2 ID',                  'field_type': 'vlan',      'placeholder': '20',              'order': 4},
            {'name': 'vlan2_ip',      'label': 'IP SVI VLAN 2',              'field_type': 'ip',        'placeholder': '192.168.20.1',    'order': 5},
            {'name': 'vlan2_mask',    'label': 'Masque VLAN 2',              'field_type': 'text',      'placeholder': '255.255.255.0',   'order': 6},
            {'name': 'uplink_iface',  'label': 'Interface uplink vers routeur','field_type': 'interface','placeholder': 'GigabitEthernet0/1','order': 7},
            {'name': 'uplink_ip',     'label': 'IP uplink (routed port)',    'field_type': 'ip',        'placeholder': '10.0.0.2',        'order': 8},
            {'name': 'uplink_mask',   'label': 'Masque uplink',              'field_type': 'text',      'placeholder': '255.255.255.252', 'order': 9},
            {'name': 'default_gw',    'label': 'Passerelle par defaut',      'field_type': 'ip',        'placeholder': '10.0.0.1',        'order': 10},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Activer le routage IP sur le switch',
                'explanation': 'Activer la fonction de routage L3 du switch multicouche.',
                'command_template': (
                    'configure terminal\n'
                    'ip routing'
                ),
                'expected_result': 'Le switch est maintenant capable de router des paquets IP entre VLANs.',
                'warning': 'Sans "ip routing", les SVIs ont des IP mais le switch se comporte comme un switch L2.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Creer les SVIs pour chaque VLAN',
                'explanation': 'Configurer une interface virtuelle L3 pour chaque VLAN — c\'est la passerelle des hotes de ce VLAN.',
                'command_template': (
                    'interface vlan {{ vlan1_id }}\n'
                    ' ip address {{ vlan1_ip }} {{ vlan1_mask }}\n'
                    ' no shutdown\n'
                    'interface vlan {{ vlan2_id }}\n'
                    ' ip address {{ vlan2_ip }} {{ vlan2_mask }}\n'
                    ' no shutdown'
                ),
                'expected_result': 'SVIs Vlan{{ vlan1_id }} et Vlan{{ vlan2_id }} up/up avec leurs adresses IP.',
                'warning': 'La SVI ne passe up que si le VLAN existe et a au moins un port actif (up/up) dans ce VLAN.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer le port routed vers le routeur edge',
                'explanation': 'Transformer l\'interface uplink en port L3 (no switchport) et configurer la route par defaut.',
                'command_template': (
                    'interface {{ uplink_iface }}\n'
                    ' no switchport\n'
                    ' ip address {{ uplink_ip }} {{ uplink_mask }}\n'
                    ' no shutdown\n'
                    'ip route 0.0.0.0 0.0.0.0 {{ default_gw }}\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Port routed vers le routeur. Route par defaut via {{ default_gw }} installee.',
                'warning': '"no switchport" est irreversible sur certains Catalyst sans reboot. Verifier avant application.',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier la licence IP routing',       'command': 'show license feature | include ipservices',   'expected_output': 'IP Services ou IP Base active selon le modele',                 'order': 1},
            {'check_type': 'post',      'title': 'Verifier ip routing actif',            'command': 'show running-config | include ^ip routing',   'expected_output': 'ip routing',                                                    'order': 1},
            {'check_type': 'post',      'title': 'Verifier les SVIs',                   'command': 'show interfaces vlan {{ vlan1_id }}',          'expected_output': 'Vlan{{ vlan1_id }} is up, line protocol is up',                 'order': 2},
            {'check_type': 'post',      'title': 'Verifier la table de routage',        'command': 'show ip route',                               'expected_output': 'Routes C pour {{ vlan1_ip }} et {{ vlan2_ip }}, S* 0.0.0.0/0', 'order': 3},
            {'check_type': 'validation','title': 'Ping inter-VLAN depuis le switch',    'command': 'ping {{ vlan2_ip }} source vlan {{ vlan1_id }}','expected_output': 'Success rate is 100 percent (5/5)',                            'order': 1},
        ],
        'rollback': {
            'conditions': 'Le routage MLS cause des problemes ou doit etre desactive.',
            'rollback_commands': (
                'configure terminal\n'
                'no ip route 0.0.0.0 0.0.0.0 {{ default_gw }}\n'
                'interface vlan {{ vlan1_id }}\n'
                ' shutdown\n'
                'interface vlan {{ vlan2_id }}\n'
                ' shutdown\n'
                'no ip routing\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Desactiver "ip routing" repasse le switch en mode L2 pur. Les SVIs restent configurees mais inactives.',
        },
    },

    # ── 23. STP Advanced ──────────────────────────────────────────────────────
    {
        'title': 'Configurer STP avance : RSTP, Root Guard et Loop Guard',
        'summary': 'Renforcement de la topologie Spanning Tree avec Root Guard pour proteger le Root Bridge et Loop Guard pour detecter les pannes unidirectionnelles.',
        'objective': 'Deployer les mecanismes de protection STP avances pour prevenir les elections indesirables de Root Bridge et les boucles dues aux pannes de liaisons unidirectionnelles.',
        'use_cases': (
            '- Protection du Root Bridge contre les switches non autorises\n'
            '- Prevention des boucles L2 en cas de panne unidirectionnelle\n'
            '- Renforcement de la securite de la topologie commutee\n'
            '- Preparation aux certifications CCNP ENCOR'
        ),
        'prerequisites': (
            '- Rapid PVST+ configure sur tous les switches\n'
            '- Root Bridge actuel identifie et protege\n'
            '- Topologie STP documentee (ports designated, root, alternate)\n'
            '- Droits privilege 15'
        ),
        'expected_outcome': (
            'Root Guard bloque tout port recevant des BPDU superieurs (err-disabled). '
            'Loop Guard detecte les pannes unidirectionnelles et met le port en loop-inconsistent. '
            '"show spanning-tree inconsistentports" = vide en fonctionnement normal.'
        ),
        'best_practices': (
            '- Root Guard : appliquer sur tous les ports designated non-root (vers les switches acces)\n'
            '- Loop Guard : appliquer sur les ports root et alternate (non-designated)\n'
            '- Ne jamais activer Root Guard et Loop Guard sur le meme port\n'
            '- Combiner avec BPDU Guard sur les ports PortFast\n'
            '- Activer "spanning-tree loopguard default" globalement puis desactiver sur les exceptions'
        ),
        'common_pitfalls': (
            '- Root Guard sur le port root du switch (se bloque lui-meme)\n'
            '- Loop Guard sur les ports PortFast (incompatible)\n'
            '- Confondre Root Guard (protection Root Bridge) et BPDU Guard (protection PortFast)\n'
            '- Port en root-inconsistent bloque tout le trafic du VLAN (perte de connectivite)\n'
            '- Oublier que Root Guard est specifique a PVST+ (par VLAN)'
        ),
        'notes': 'Root Guard et Loop Guard sont mutuellement exclusifs sur un meme port. Root Guard s\'applique sur les ports "designated" (vers les switches en aval). Loop Guard s\'applique sur les ports "non-designated" (root/alternate).',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'advanced',
        'criticality': 'high',
        'estimated_duration': 25,
        'status': 'published',
        'category': 'vlan-switching',
        'is_featured': False,
        'requires_maintenance_window': False,
        'save_config_required': True,
        'variables': [
            {'name': 'vlan_range',      'label': 'VLANs a proteger',          'field_type': 'text',      'placeholder': '10,20,30',          'order': 1},
            {'name': 'root_guard_port', 'label': 'Port Root Guard (vers acces)','field_type': 'interface','placeholder': 'GigabitEthernet0/2','order': 2},
            {'name': 'loop_guard_port', 'label': 'Port Loop Guard (root/alt)', 'field_type': 'interface','placeholder': 'GigabitEthernet0/1','order': 3},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Activer Loop Guard globalement',
                'explanation': 'Activer Loop Guard par defaut sur tous les ports non-designated du switch pour detecter les pannes unidirectionnelles.',
                'command_template': (
                    'configure terminal\n'
                    'spanning-tree loopguard default'
                ),
                'expected_result': 'Loop Guard actif par defaut sur tous les ports root et alternate du switch.',
                'warning': 'Loop Guard est automatiquement desactive sur les ports PortFast (incompatibilite geree par IOS).',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Configurer Root Guard sur le port vers un switch acces',
                'explanation': 'Empecher qu\'un switch en aval devienne Root Bridge en bloquant les BPDU superieurs sur ce port.',
                'command_template': (
                    'interface {{ root_guard_port }}\n'
                    ' spanning-tree guard root'
                ),
                'expected_result': 'Root Guard actif sur {{ root_guard_port }}. Tout BPDU superieur recu mettra le port en root-inconsistent.',
                'warning': 'N\'appliquer Root Guard QUE sur les ports designated vers les switches acces, jamais sur les uplinks.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Configurer Loop Guard specifique sur un port et sauvegarder',
                'explanation': 'Confirmer Loop Guard sur le port root/alternate specifique si le defaut global est insuffisant.',
                'command_template': (
                    'interface {{ loop_guard_port }}\n'
                    ' spanning-tree guard loop\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Loop Guard confirme sur {{ loop_guard_port }}. Configuration sauvegardee.',
                'warning': '',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier le role des ports STP',       'command': 'show spanning-tree vlan {{ vlan_range }}',              'expected_output': 'Roles des ports : Root, Desg, Altn — identifier avant application',    'order': 1},
            {'check_type': 'post',      'title': 'Verifier Root Guard',                  'command': 'show spanning-tree interface {{ root_guard_port }} detail','expected_output': 'Root guard is enabled on the port',                                 'order': 1},
            {'check_type': 'post',      'title': 'Verifier Loop Guard',                  'command': 'show spanning-tree interface {{ loop_guard_port }} detail','expected_output': 'Loop guard is enabled on the port',                                 'order': 2},
            {'check_type': 'post',      'title': 'Verifier absence de ports inconsistants','command': 'show spanning-tree inconsistentports',               'expected_output': 'Name: vide (aucun port bloque par Root/Loop Guard)',                    'order': 3},
            {'check_type': 'validation','title': 'Verifier la topologie STP stable',     'command': 'show spanning-tree summary',                            'expected_output': '0 topology changes recentes — topologie stable',                      'order': 1},
        ],
        'rollback': {
            'conditions': 'Root Guard ou Loop Guard bloque des ports legitimes causant une perte de connectivite.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ root_guard_port }}\n'
                ' no spanning-tree guard root\n'
                'interface {{ loop_guard_port }}\n'
                ' no spanning-tree guard loop\n'
                'no spanning-tree loopguard default\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Si un port est en root-inconsistent, supprimer Root Guard et faire "shutdown / no shutdown" pour le reinitialiser.',
        },
    },

    # ── 24. Layer 3 EtherChannel ───────────────────────────────────────────────
    {
        'title': 'Configurer un EtherChannel L3 (routed port-channel)',
        'summary': 'Creation d\'un EtherChannel L3 entre deux switches multicouches pour un lien inter-switch route, sans STP, avec bande passante aggregee.',
        'objective': 'Agreger plusieurs liens physiques en un Port-Channel L3 avec une adresse IP, eliminer STP sur ce lien et assurer la redondance avec LACP.',
        'use_cases': (
            '- Lien inter-switch L3 entre la distribution et le core\n'
            '- Alternative au trunk L2 EtherChannel avec routage natif\n'
            '- Elimination de STP sur les liens critiques entre switches L3\n'
            '- Connexion haute disponibilite entre switches de distribution'
        ),
        'prerequisites': (
            '- Switches multicouches (Catalyst 3560/3750/3850/9300 ou equivalent)\n'
            '- "ip routing" active sur les deux switches\n'
            '- Interfaces membres non assignees a d\'autres port-channels\n'
            '- Plan d\'adressage /30 pour le lien inter-switch'
        ),
        'expected_outcome': (
            '"show etherchannel summary" affiche le Port-Channel en etat "RU" (Layer3, in use). '
            'Le Port-Channel a une adresse IP et apparait dans "show ip route" comme route connectee. '
            'STP n\'est pas actif sur ce lien.'
        ),
        'best_practices': (
            '- Utiliser un /30 ou /31 pour le lien inter-switch L3\n'
            '- Configurer les interfaces membres avant le Port-Channel (sequence L3)\n'
            '- Verifier que toutes les interfaces membres ont le meme type (copper/fiber)\n'
            '- Activer LACP des deux cotes (active/active ou active/passive)\n'
            '- Documenter le Port-Channel ID et le sous-reseau utilise'
        ),
        'common_pitfalls': (
            '- Oublier "no switchport" sur les interfaces membres (restent en mode L2)\n'
            '- Assigner une IP directement sur les membres physiques au lieu du Port-Channel\n'
            '- Interfaces membres de vitesses differentes (LACP refuse de les bundler)\n'
            '- Port-Channel cree en mode L2 (sans "no switchport") par defaut sur certains switches\n'
            '- Oublier "ip routing" : le Port-Channel a une IP mais ne route pas'
        ),
        'notes': 'Un EtherChannel L3 n\'est pas soumis au Spanning Tree (pas de BPDU). STP ne voit pas les liens membres individuellement, seulement le Port-Channel logique comme un seul lien L3.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'advanced',
        'criticality': 'high',
        'estimated_duration': 30,
        'status': 'published',
        'category': 'vlan-switching',
        'is_featured': False,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'pc_number',      'label': 'Numero du Port-Channel',    'field_type': 'text',      'placeholder': '1',                  'order': 1},
            {'name': 'member_iface1',  'label': 'Interface membre 1',        'field_type': 'interface', 'placeholder': 'GigabitEthernet1/0/1','order': 2},
            {'name': 'member_iface2',  'label': 'Interface membre 2',        'field_type': 'interface', 'placeholder': 'GigabitEthernet1/0/2','order': 3},
            {'name': 'pc_ip',          'label': 'IP du Port-Channel',        'field_type': 'ip',        'placeholder': '10.0.0.1',            'order': 4},
            {'name': 'pc_mask',        'label': 'Masque',                    'field_type': 'text',      'placeholder': '255.255.255.252',     'order': 5},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer les interfaces membres en mode L3 et les ajouter au Port-Channel',
                'explanation': 'Supprimer le mode switchport (L2) des interfaces membres et les associer au Port-Channel avec LACP.',
                'command_template': (
                    'configure terminal\n'
                    'interface {{ member_iface1 }}\n'
                    ' no switchport\n'
                    ' no ip address\n'
                    ' channel-group {{ pc_number }} mode active\n'
                    'interface {{ member_iface2 }}\n'
                    ' no switchport\n'
                    ' no ip address\n'
                    ' channel-group {{ pc_number }} mode active'
                ),
                'expected_result': 'Interfaces {{ member_iface1 }} et {{ member_iface2 }} ajoutees au Port-Channel {{ pc_number }} en mode L3.',
                'warning': '"no switchport" est necessaire pour que les membres soient en mode L3. Sans cette commande, le Port-Channel reste en mode L2.',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Configurer l\'adresse IP sur le Port-Channel',
                'explanation': 'Assigner l\'adresse IP sur l\'interface logique Port-Channel (pas sur les membres physiques).',
                'command_template': (
                    'interface port-channel {{ pc_number }}\n'
                    ' no switchport\n'
                    ' ip address {{ pc_ip }} {{ pc_mask }}\n'
                    ' no shutdown\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Port-Channel {{ pc_number }} avec IP {{ pc_ip }}/{{ pc_mask }}, en etat up/up.',
                'warning': '',
                'order': 2,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier ip routing actif',            'command': 'show running-config | include ^ip routing',      'expected_output': 'ip routing',                                                        'order': 1},
            {'check_type': 'post',      'title': 'Verifier l\'etat EtherChannel L3',    'command': 'show etherchannel summary',                      'expected_output': 'Po{{ pc_number }} (RU) — R=Layer3, U=in use — membres (P)',          'order': 1},
            {'check_type': 'post',      'title': 'Verifier l\'IP du Port-Channel',      'command': 'show interfaces port-channel {{ pc_number }}',   'expected_output': 'Port-channel{{ pc_number }} is up — Internet address is {{ pc_ip }}', 'order': 2},
            {'check_type': 'post',      'title': 'Verifier la route connectee',         'command': 'show ip route connected',                        'expected_output': 'Route C pour le reseau {{ pc_ip }} via Port-channel{{ pc_number }}',  'order': 3},
            {'check_type': 'validation','title': 'Ping vers l\'IP distante du lien',    'command': 'ping <ip_distante_port_channel>',                'expected_output': 'Success rate is 100 percent (5/5)',                                   'order': 1},
        ],
        'rollback': {
            'conditions': 'Le Port-Channel L3 ne monte pas ou cause des problemes de routage.',
            'rollback_commands': (
                'configure terminal\n'
                'interface port-channel {{ pc_number }}\n'
                ' no ip address\n'
                ' shutdown\n'
                'interface {{ member_iface1 }}\n'
                ' no channel-group {{ pc_number }}\n'
                ' switchport\n'
                'interface {{ member_iface2 }}\n'
                ' no channel-group {{ pc_number }}\n'
                ' switchport\n'
                'no interface port-channel {{ pc_number }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Remettre "switchport" sur les membres pour les repasser en mode L2 si necessaire.',
        },
    },

    # ── 25. Security + STP Hardening ──────────────────────────────────────────
    {
        'title': 'Durcissement securite L2 : BPDU Guard, Storm Control et DAI',
        'summary': 'Application d\'un ensemble de protections L2 contre les attaques reseau : BPDU Guard (STP), Storm Control (broadcast/multicast) et Dynamic ARP Inspection (ARP poisoning).',
        'objective': 'Renforcer la securite L2 du switch avec trois mecanismes complementaires : protection STP, limitation des tempetes de broadcast, et validation des echanges ARP.',
        'use_cases': (
            '- Durcissement securite d\'un switch en production\n'
            '- Protection contre ARP poisoning / Man-in-the-Middle\n'
            '- Prevention des tempetes de broadcast et boucles accidentelles\n'
            '- Conformite securite (PCI-DSS, ISO 27001, ANSSI BP28)'
        ),
        'prerequisites': (
            '- DHCP Snooping configure et fonctionnel (requis pour DAI)\n'
            '- VLANs et ports configures\n'
            '- PortFast active sur les ports d\'acces (prerequis BPDU Guard)\n'
            '- Droits privilege 15'
        ),
        'expected_outcome': (
            'BPDU Guard place en err-disabled tout port acces recevant un BPDU. '
            'Storm Control limite le trafic broadcast/multicast. '
            'DAI valide les paquets ARP contre la table DHCP Snooping — ARP spoofing bloque.'
        ),
        'best_practices': (
            '- Activer BPDU Guard globalement sur tous les ports PortFast\n'
            '- Configurer err-disable recovery pour BPDU Guard (evite intervention manuelle)\n'
            '- Storm Control : seuil 20% rising / 10% falling pour la plupart des environnements\n'
            '- DAI : appliquer sur tous les VLANs utilisateur, pas sur les VLANs de gestion\n'
            '- Loguer les violations DAI pour detection d\'incidents'
        ),
        'common_pitfalls': (
            '- BPDU Guard sans PortFast : ne s\'active pas correctement\n'
            '- DAI sans DHCP Snooping : aucune table de reference (tout ARP est bloque ou accepte)\n'
            '- Storm Control trop restrictif perturbant le trafic VoIP/multicast legitime\n'
            '- Oublier le port "trusted" DAI pour le port vers le routeur (ARP bloque)\n'
            '- err-disable recovery non configure : ports restes bloques indefiniment'
        ),
        'notes': 'Dynamic ARP Inspection (DAI) utilise la table DHCP Snooping pour valider les echanges ARP. Les hotes avec IP statique doivent etre ajoutes manuellement via "ip arp inspection filter".',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'switch',
        'difficulty': 'advanced',
        'criticality': 'high',
        'estimated_duration': 30,
        'status': 'published',
        'category': 'securite-acl',
        'is_featured': False,
        'requires_maintenance_window': False,
        'save_config_required': True,
        'variables': [
            {'name': 'vlan_range',      'label': 'VLANs a proteger',            'field_type': 'text',      'placeholder': '10,20,30',           'order': 1},
            {'name': 'access_port',     'label': 'Port acces utilisateur',       'field_type': 'interface', 'placeholder': 'FastEthernet0/1',    'order': 2},
            {'name': 'trusted_port',    'label': 'Port trusted DAI (uplink)',    'field_type': 'interface', 'placeholder': 'GigabitEthernet0/24','order': 3},
            {'name': 'storm_rising',    'label': 'Seuil Storm Control montant (%)', 'field_type': 'text',   'placeholder': '20',                 'order': 4},
            {'name': 'storm_falling',   'label': 'Seuil Storm Control descendant (%)', 'field_type': 'text','placeholder': '10',                 'order': 5},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Activer BPDU Guard globalement et configurer err-disable recovery',
                'explanation': 'Activer BPDU Guard sur tous les ports PortFast et configurer la recuperation automatique des ports err-disabled.',
                'command_template': (
                    'configure terminal\n'
                    'spanning-tree portfast bpduguard default\n'
                    'errdisable recovery cause bpduguard\n'
                    'errdisable recovery interval 300'
                ),
                'expected_result': 'BPDU Guard actif sur tous les ports PortFast. Ports err-disabled recuperes apres 300s.',
                'warning': '',
                'order': 1,
            },
            {
                'step_number': 2,
                'title': 'Configurer Storm Control sur le port acces',
                'explanation': 'Limiter le trafic broadcast et multicast pour prevenir les tempetes de diffusion.',
                'command_template': (
                    'interface {{ access_port }}\n'
                    ' storm-control broadcast level {{ storm_rising }} {{ storm_falling }}\n'
                    ' storm-control multicast level {{ storm_rising }} {{ storm_falling }}\n'
                    ' storm-control action shutdown'
                ),
                'expected_result': 'Storm Control actif : broadcast/multicast limites a {{ storm_rising }}%. Port shutdown si depasse.',
                'warning': 'Le mode "shutdown" coupe le port en cas de tempete. Utiliser "trap" pour seulement alerter si trop restrictif.',
                'order': 2,
            },
            {
                'step_number': 3,
                'title': 'Activer Dynamic ARP Inspection (DAI)',
                'explanation': 'Activer DAI sur les VLANs utilisateur et marquer le port uplink en trusted pour laisser passer l\'ARP legitime.',
                'command_template': (
                    'ip arp inspection vlan {{ vlan_range }}\n'
                    'ip arp inspection validate src-mac dst-mac ip\n'
                    'interface {{ trusted_port }}\n'
                    ' ip arp inspection trust\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'DAI actif sur VLANs {{ vlan_range }}. ARP non conforme a la table DHCP Snooping est drope.',
                'warning': 'Sans "trust" sur le port uplink, l\'ARP du routeur est bloque et tout le trafic routed est coupe.',
                'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier DHCP Snooping actif',         'command': 'show ip dhcp snooping',                           'expected_output': 'DHCP Snooping enabled (prerequis pour DAI)',                           'order': 1},
            {'check_type': 'post',      'title': 'Verifier BPDU Guard global',           'command': 'show spanning-tree summary',                      'expected_output': 'Portfast BPDU Guard Default is enabled',                              'order': 1},
            {'check_type': 'post',      'title': 'Verifier Storm Control',               'command': 'show storm-control {{ access_port }} broadcast',  'expected_output': 'Rising threshold {{ storm_rising }}%, Action: Shutdown Port',         'order': 2},
            {'check_type': 'post',      'title': 'Verifier DAI',                         'command': 'show ip arp inspection vlan {{ vlan_range }}',    'expected_output': 'VLAN {{ vlan_range }}: Enabled, {{ trusted_port }} trusted',          'order': 3},
            {'check_type': 'post',      'title': 'Verifier les statistiques DAI',        'command': 'show ip arp inspection statistics vlan {{ vlan_range }}', 'expected_output': 'Forwarded > 0, Dropped = 0 en fonctionnement normal',         'order': 4},
            {'check_type': 'validation','title': 'Test connectivite post-hardening',     'command': 'ping <ip_passerelle_vlan>',                       'expected_output': 'Success rate is 100 percent (5/5) depuis un hote du VLAN',            'order': 1},
        ],
        'rollback': {
            'conditions': 'Une des protections L2 bloque du trafic legitime ou cause des problemes de connectivite.',
            'rollback_commands': (
                'configure terminal\n'
                'no ip arp inspection vlan {{ vlan_range }}\n'
                'interface {{ access_port }}\n'
                ' no storm-control broadcast level\n'
                ' no storm-control multicast level\n'
                ' no storm-control action shutdown\n'
                'no spanning-tree portfast bpduguard default\n'
                'no errdisable recovery cause bpduguard\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Desactiver DAI en premier si la connectivite est coupee, puis Storm Control et BPDU Guard. Verifier les ports err-disabled avec "show interfaces status err-disabled".',
        },
    },

    # ── 5. HSRP Configuration ─────────────────────────────────────────────────
    {
        'title': 'Configurer HSRP pour la haute disponibilite',
        'summary': 'Mise en place de HSRP (Hot Standby Router Protocol) entre deux routeurs/switches L3 pour assurer la redondance de passerelle.',
        'objective': 'Configurer un groupe HSRP avec un routeur actif et un routeur standby partageant une adresse IP virtuelle de passerelle.',
        'use_cases': (
            '- Redondance de passerelle par defaut pour les postes clients\n'
            '- Elimination du SPOF (Single Point of Failure) sur la passerelle\n'
            '- Basculement automatique en cas de panne du routeur actif\n'
            '- Architecture avec deux routeurs/switches L3 en bord de distribution'
        ),
        'prerequisites': (
            '- Deux routeurs ou switches L3 avec connectivite entre eux\n'
            '- Interfaces L3 configurees avec des IP du meme sous-reseau\n'
            '- IP virtuelle HSRP disponible dans le sous-reseau\n'
            '- IOS supportant HSRP (standard sur IOS 12.x+)'
        ),
        'expected_outcome': (
            'Le routeur actif gere le trafic via l\'IP virtuelle. '
            '"show standby brief" affiche un routeur en etat Active et l\'autre en Standby. '
            'En cas de panne du routeur actif, le standby prend la main en moins de 10 secondes.'
        ),
        'best_practices': (
            '- Utiliser HSRP v2 (supporte IPv6 et groupes 0-4095)\n'
            '- Definir des priorites explicites (100 = defaut, augmenter pour l\'actif prefere)\n'
            '- Activer "preempt" pour que le routeur prefere reprenne le role actif apres reprise\n'
            '- Configurer le tracking d\'interface pour baisser la priorite si l\'uplink tombe\n'
            '- Utiliser une authentification MD5 pour securiser les echanges HSRP'
        ),
        'common_pitfalls': (
            '- IP virtuelle identique a une IP reelle d\'interface (conflit)\n'
            '- Oublier "preempt" : le routeur prefere ne reprend pas le role actif apres reboot\n'
            '- Numero de groupe HSRP different entre les deux routeurs (pas d\'election)\n'
            '- Meme priorite sur les deux routeurs sans preempt (election aleatoire)\n'
            '- VIP HSRP hors du sous-reseau de l\'interface'
        ),
        'notes': 'HSRP est proprietaire Cisco. Pour un environnement multi-vendeur, utiliser VRRP (standard IEEE). GLBP offre en plus le load balancing entre les passerelles.',
        'vendor': 'cisco',
        'platform': 'ios',
        'device_type': 'router',
        'difficulty': 'intermediate',
        'criticality': 'critical',
        'estimated_duration': 30,
        'status': 'published',
        'category': 'haute-disponibilite',
        'is_featured': True,
        'requires_maintenance_window': True,
        'save_config_required': True,
        'variables': [
            {'name': 'interface_name',  'label': 'Interface HSRP',              'field_type': 'interface', 'placeholder': 'GigabitEthernet0/1', 'order': 1},
            {'name': 'hsrp_group',      'label': 'Numero de groupe HSRP',       'field_type': 'text',      'placeholder': '1',                  'order': 2},
            {'name': 'virtual_ip',      'label': 'IP virtuelle (VIP)',           'field_type': 'ip',        'placeholder': '192.168.1.254',      'order': 3},
            {'name': 'priority',        'label': 'Priorite HSRP (actif > 100)', 'field_type': 'text',      'placeholder': '110',                'order': 4},
            {'name': 'track_interface', 'label': 'Interface a surveiller',      'field_type': 'interface', 'placeholder': 'GigabitEthernet0/0', 'order': 5},
        ],
        'steps': [
            {
                'step_number': 1,
                'title': 'Configurer HSRP sur le routeur ACTIF',
                'explanation': 'Activer HSRP v2 sur l\'interface, definir l\'IP virtuelle, la priorite elevee et le preempt.',
                'command_template': (
                    'configure terminal\n'
                    'interface {{ interface_name }}\n'
                    ' standby version 2\n'
                    ' standby {{ hsrp_group }} ip {{ virtual_ip }}\n'
                    ' standby {{ hsrp_group }} priority {{ priority }}\n'
                    ' standby {{ hsrp_group }} preempt\n'
                    ' standby {{ hsrp_group }} preempt delay minimum 30'
                ),
                'expected_result': 'Routeur actif : etat HSRP passe a Active apres election.',
                'warning': 'Ces commandes sont a saisir sur le routeur ACTIF (priorite > 100). Sur le standby, utiliser la priorite par defaut (100) sans "priority".',
                'order': 1,
                'real_world_example': 'Exemple : tous les PCs du bureau utilisent 192.168.1.254 comme passerelle. Avec HSRP, cette IP n\'appartient a aucun routeur physique — c\'est une IP virtuelle partagee. Le routeur R1 (priorite 110) est actif et repond pour cette IP. Les PCs ne savent pas qu\'il y a deux routeurs derriere. Ils font juste confiance a l\'adresse 192.168.1.254.',
            },
            {
                'step_number': 2,
                'title': 'Configurer le tracking d\'interface',
                'explanation': 'Surveiller l\'interface uplink : si elle tombe, baisser la priorite HSRP pour declencher un basculement.',
                'command_template': (
                    ' standby {{ hsrp_group }} track {{ track_interface }} decrement 20\n'
                    'end'
                ),
                'expected_result': 'Si {{ track_interface }} tombe, priorite passe a {{ priority }}-20. Le standby (100) prend le role actif.',
                'warning': 'Le decrement doit etre suffisant pour passer sous la priorite du standby (ex: 110 - 20 = 90 < 100).',
                'order': 2,
                'real_world_example': 'Exemple : R1 (priorite 110) est actif mais sa connexion Internet (Gi0/0) tombe. Sans tracking, R1 resterait quand meme le routeur actif HSRP meme s\'il ne peut plus acceder a Internet — inutile ! Avec le tracking, quand Gi0/0 tombe, la priorite de R1 baisse a 90 (110-20). R2 avec sa priorite de 100 devient actif et prend le relais. Le basculement est automatique en moins de 10 secondes.',
            },
            {
                'step_number': 3,
                'title': 'Configurer le routeur STANDBY',
                'explanation': 'Sur le second routeur, configurer HSRP avec le meme groupe et la meme VIP, mais sans augmenter la priorite.',
                'command_template': (
                    'configure terminal\n'
                    'interface {{ interface_name }}\n'
                    ' standby version 2\n'
                    ' standby {{ hsrp_group }} ip {{ virtual_ip }}\n'
                    ' standby {{ hsrp_group }} preempt\n'
                    'end\n'
                    'copy running-config startup-config'
                ),
                'expected_result': 'Second routeur en etat Standby. Election HSRP terminee.',
                'warning': '',
                'order': 3,
                'real_world_example': 'Exemple : sur R2 (le routeur de secours), tu configures le meme groupe HSRP et la meme VIP 192.168.1.254, mais SANS augmenter la priorite (elle reste a 100 par defaut). R2 sait alors qu\'il doit laisser R1 etre actif. Il surveille en silence et est pret a prendre le relais en quelques secondes si R1 disparait. Le "preempt" sur R2 lui permet de reprendre le role standby si R1 revient en ligne apres une panne.',
            },
        ],
        'checks': [
            {'check_type': 'pre',       'title': 'Verifier connectivite entre routeurs',  'command': 'ping <ip_routeur_standby>',                   'expected_output': 'Success rate is 100 percent',                                              'order': 1},
            {'check_type': 'pre',       'title': 'Verifier que la VIP est libre',         'command': 'ping {{ virtual_ip }}',                       'expected_output': 'Echec (host unreachable) — confirme que la VIP est disponible',             'order': 2},
            {'check_type': 'post',      'title': 'Verifier etat HSRP actif',              'command': 'show standby brief',                          'expected_output': '{{ interface_name }} Grp {{ hsrp_group }} P Active local {{ virtual_ip }}', 'order': 1},
            {'check_type': 'post',      'title': 'Verifier details HSRP',                 'command': 'show standby {{ interface_name }} {{ hsrp_group }}', 'expected_output': 'Active router is local, priority {{ priority }}, preemption enabled', 'order': 2},
            {'check_type': 'validation','title': 'Ping VIP depuis un host LAN',           'command': 'ping {{ virtual_ip }}',                       'expected_output': 'Success rate is 100 percent — passerelle virtuelle joignable',              'order': 1},
            {'check_type': 'validation','title': 'Test basculement (shutdown actif)',      'command': 'show standby brief',                          'expected_output': 'Apres shutdown de l\'actif : le standby passe en Active < 10s',            'order': 2},
        ],
        'rollback': {
            'conditions': 'HSRP cause un conflit d\'adressage ou des problemes de connectivite apres activation.',
            'rollback_commands': (
                'configure terminal\n'
                'interface {{ interface_name }}\n'
                ' no standby {{ hsrp_group }}\n'
                'end\n'
                'copy running-config startup-config'
            ),
            'notes': 'Supprimer HSRP des deux routeurs. Les clients devront pointer vers une passerelle physique manuelle.',
        },
    },
]


class Command(BaseCommand):
    help = 'Ajoute 5 nouvelles procedures Cisco (seed additionnel - ne touche pas aux donnees existantes)'

    def handle(self, *args, **options):
        self.stdout.write('=== seed_extra : ajout de nouvelles procedures ===')

        # Creer les nouvelles categories si absentes
        for cat_data in NEW_CATEGORIES:
            cat, created = ProcedureCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name':        cat_data['name'],
                    'icon':        cat_data['icon'],
                    'description': cat_data['description'],
                },
            )
            status = 'creee' if created else 'existante'
            self.stdout.write(f'  Categorie [{status}] : {cat.name}')

        # Charger les categories existantes dans un dict slug -> objet
        categories = {c.slug: c for c in ProcedureCategory.objects.all()}

        created_count = 0
        skipped_count = 0

        for data in PROCEDURES_DATA:
            slug = slugify(data['title'])

            if Procedure.objects.filter(slug=slug).exists():
                self.stdout.write(f'  [SKIP] deja present : {data["title"]}')
                skipped_count += 1
                continue

            cat_slug = data['category']
            if cat_slug not in categories:
                self.stdout.write(f'  [ERREUR] categorie introuvable : {cat_slug} -- procedure ignoree : {data["title"]}')
                skipped_count += 1
                continue

            # Creer la procedure
            proc = Procedure.objects.create(
                title=data['title'],
                slug=slug,
                summary=data['summary'],
                objective=data.get('objective', ''),
                use_cases=data.get('use_cases', ''),
                prerequisites=data.get('prerequisites', ''),
                expected_outcome=data.get('expected_outcome', ''),
                best_practices=data.get('best_practices', ''),
                common_pitfalls=data.get('common_pitfalls', ''),
                notes=data.get('notes', ''),
                vendor=data.get('vendor', 'cisco'),
                platform=data.get('platform', 'ios'),
                device_type=data.get('device_type', 'router'),
                difficulty=data.get('difficulty', 'intermediate'),
                criticality=data.get('criticality', 'medium'),
                estimated_duration=data.get('estimated_duration', 30),
                status=data.get('status', 'published'),
                category=categories[cat_slug],
                is_featured=data.get('is_featured', False),
                requires_maintenance_window=data.get('requires_maintenance_window', False),
                save_config_required=data.get('save_config_required', True),
            )

            # Variables
            for v in data.get('variables', []):
                ProcedureVariable.objects.create(
                    procedure=proc,
                    name=v['name'],
                    label=v.get('label', v['name']),
                    field_type=v.get('field_type', 'text'),
                    placeholder=v.get('placeholder', ''),
                    help_text=v.get('help_text', ''),
                    required=v.get('required', True),
                    order=v.get('order', 1),
                    select_options=v.get('select_options', ''),
                )

            # Steps
            for s in data.get('steps', []):
                ProcedureStep.objects.create(
                    procedure=proc,
                    step_number=s['step_number'],
                    title=s['title'],
                    explanation=s.get('explanation', ''),
                    command_template=s.get('command_template', ''),
                    expected_result=s.get('expected_result', ''),
                    warning=s.get('warning', ''),
                    order=s.get('order', s['step_number']),
                )

            # Checks
            for c in data.get('checks', []):
                ProcedureCheck.objects.create(
                    procedure=proc,
                    check_type=c['check_type'],
                    title=c['title'],
                    command=c.get('command', ''),
                    expected_output=c.get('expected_output', ''),
                    order=c.get('order', 1),
                )

            # Rollback
            rb = data.get('rollback')
            if rb:
                ProcedureRollback.objects.create(
                    procedure=proc,
                    conditions=rb.get('conditions', ''),
                    rollback_commands=rb.get('rollback_commands', ''),
                    notes=rb.get('notes', ''),
                )

            self.stdout.write(f'  [OK] {proc.title}')
            created_count += 1

        self.stdout.write('')
        self.stdout.write(f'=== Termine : {created_count} creees, {skipped_count} ignorees ===')
