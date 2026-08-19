"""
Commande de seed : python manage.py seed_data
Recrée les catégories et les procédures de démonstration complètes.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from procedures.models import (
    ProcedureCategory, Procedure, ProcedureVariable,
    ProcedureStep, ProcedureCheck, ProcedureRollback,
)

CATEGORIES = [
    {'name': 'VLAN & Switching',  'slug': 'vlan-switching',  'icon': 'bi-hdd-network',    'description': 'Création et gestion des VLANs, trunks, ports access'},
    {'name': 'Routage',           'slug': 'routage',          'icon': 'bi-arrow-left-right','description': 'Routes statiques, OSPF, inter-VLAN, router-on-a-stick'},
    {'name': 'Sécurité & ACL',    'slug': 'securite-acl',     'icon': 'bi-shield-lock',    'description': 'ACL standard/extended, NAT, filtrage de trafic'},
    {'name': 'Supervision',       'slug': 'supervision',      'icon': 'bi-graph-up',       'description': 'SNMP, Syslog, NTP, monitoring réseau'},
    {'name': 'Troubleshooting',   'slug': 'troubleshooting',  'icon': 'bi-bug',            'description': 'Diagnostic et résolution d\'incidents réseau Cisco'},
]

PROCEDURES_DATA = [

    # ── 1. Créer un VLAN ─────────────────────────────────────────────────────
    {
        'title': 'Créer un VLAN sur switch Cisco',
        'summary': 'Création, nommage et assignation d\'un VLAN sur un switch Cisco Catalyst.',
        'objective': 'Créer un VLAN avec son ID et son nom sur un switch Cisco, puis assigner un ou plusieurs ports en mode access.',
        'use_cases': '- Segmentation réseau (VLAN IT, VoIP, Guest, Serveurs)\n- Isolation de trafic entre services\n- Déploiement d\'un nouveau périmètre réseau',
        'prerequisites': '- Accès SSH ou console au switch\n- Droits enable / privilege 15\n- Plan d\'adressage VLAN validé\n- ID VLAN disponible (non utilisé)',
        'expected_outcome': 'Le VLAN est visible dans show vlan brief avec le statut "active". Les ports assignés aparaissent dans la colonne Ports du VLAN.',
        'best_practices': '- Vérifier l\'existence du VLAN avant création (éviter les doublons)\n- Nommer les VLANs de manière explicite (VLAN_PROD, VLAN_VOIP)\n- Éviter le VLAN 1 pour le trafic utilisateur\n- Documenter l\'assignation dans le plan d\'adressage\n- Vérifier l\'impact STP après création',
        'common_pitfalls': '- Oublier de créer le VLAN sur tous les switches du domaine de broadcast\n- Utiliser des IDs VLAN déjà réservés (1002-1005)\n- Ne pas vérifier si le trunk autorise le nouveau VLAN\n- Oublier "no shutdown" sur l\'interface',
        'notes': 'Le VLAN 1 est le VLAN natif Cisco par défaut — à éviter pour le trafic utilisateur. Les VLANs 1002-1005 sont réservés.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'switch',
        'difficulty': 'beginner', 'criticality': 'medium',
        'estimated_duration': 10, 'status': 'published',
        'category': 'vlan-switching', 'is_featured': True,
        'requires_maintenance_window': False, 'save_config_required': True,
        'variables': [
            {'name': 'vlan_id',        'label': 'ID du VLAN',        'field_type': 'vlan',      'placeholder': '10',               'order': 1},
            {'name': 'vlan_name',      'label': 'Nom du VLAN',       'field_type': 'text',      'placeholder': 'VLAN_IT',          'order': 2},
            {'name': 'interface_name', 'label': 'Interface access',  'field_type': 'interface', 'placeholder': 'GigabitEthernet0/1','order': 3},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Passer en mode configuration globale',
                'explanation': 'Accéder au mode privilegié puis au mode configuration pour modifier le switch.',
                'command_template': 'enable\nconfigure terminal',
                'expected_result': 'Prompt Switch(config)# affiché.',
                'warning': '', 'order': 1,
            },
            {
                'step_number': 2, 'title': 'Créer le VLAN et lui attribuer un nom',
                'explanation': 'Créer le VLAN dans la base de données VLAN du switch et lui donner un nom descriptif.',
                'command_template': 'vlan {{ vlan_id }}\n name {{ vlan_name }}',
                'expected_result': 'VLAN créé et visible dans show vlan brief avec statut active.',
                'warning': '', 'order': 2,
                'real_world_example': 'Exemple : tu crées le VLAN 20 pour tous les PCs du service Comptabilite. Tu le nommes VLAN_COMPTA pour que tout le monde comprenne a quoi il correspond. Sans ce VLAN, les PCs de Compta seraient melanges avec les autres services sur le meme reseau.',
            },
            {
                'step_number': 3, 'title': 'Configurer le port en mode access',
                'explanation': 'Assigner l\'interface au VLAN en mode access. Le port ne transportera qu\'un seul VLAN non tagué.',
                'command_template': 'interface {{ interface_name }}\n switchport mode access\n switchport access vlan {{ vlan_id }}\n no shutdown',
                'expected_result': 'Port en mode access sur le VLAN {{ vlan_id }}, état up/up.',
                'warning': 'Vérifier que le port n\'est pas actuellement en mode trunk avant modification.',
                'order': 3,
                'real_world_example': 'Exemple : Marie travaille en Comptabilite et son PC est branche sur le port Gi0/5 du switch. En mettant ce port dans le VLAN 20 (VLAN_COMPTA), le PC de Marie rejoint automatiquement le reseau Comptabilite. Elle peut acceder aux serveurs de Compta, mais pas au reseau IT ni au reseau RH.',
            },
            {
                'step_number': 4, 'title': 'Sauvegarder la configuration',
                'explanation': 'Enregistrer la configuration en NVRAM pour persistence après redémarrage.',
                'command_template': 'end\ncopy running-config startup-config',
                'expected_result': 'Destination filename [startup-config]? — Appuyer sur Entrée. [OK]',
                'warning': '', 'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre', 'title': 'Vérifier les VLANs existants', 'command': 'show vlan brief', 'expected_output': 'Liste des VLANs actifs — confirmer que le VLAN {{ vlan_id }} n\'existe pas.', 'order': 1},
            {'check_type': 'pre', 'title': 'Vérifier le mode de l\'interface', 'command': 'show interfaces {{ interface_name }} switchport', 'expected_output': 'Administrative Mode: dynamic auto (ou access)', 'order': 2},
            {'check_type': 'post', 'title': 'Confirmer la création du VLAN', 'command': 'show vlan id {{ vlan_id }}', 'expected_output': 'VLAN {{ vlan_id }}  {{ vlan_name }}  active  {{ interface_name }}', 'order': 1},
            {'check_type': 'post', 'title': 'Vérifier l\'assignation du port', 'command': 'show interfaces {{ interface_name }} switchport', 'expected_output': 'Access Mode VLAN: {{ vlan_id }} ({{ vlan_name }})', 'order': 2},
            {'check_type': 'validation', 'title': 'Vérifier l\'apprentissage MAC', 'command': 'show mac address-table vlan {{ vlan_id }}', 'expected_output': 'Adresses MAC apprises sur le VLAN {{ vlan_id }}.', 'order': 1},
        ],
        'rollback': {
            'conditions': 'Le VLAN cause des problèmes de connectivité ou n\'est plus nécessaire.',
            'rollback_commands': 'configure terminal\nno vlan {{ vlan_id }}\ninterface {{ interface_name }}\n no switchport access vlan\n switchport access vlan 1\nend\ncopy running-config startup-config',
            'notes': 'Attention : supprimer un VLAN actif coupe immédiatement le trafic de tous les ports assignés.',
        },
    },

    # ── 2. Configurer un trunk ────────────────────────────────────────────────
    {
        'title': 'Configurer un lien trunk 802.1Q',
        'summary': 'Mise en place d\'un lien trunk 802.1Q entre deux équipements Cisco pour transporter plusieurs VLANs.',
        'objective': 'Configurer une interface en mode trunk statique pour transporter des VLANs tagués entre deux équipements réseau.',
        'use_cases': '- Liaison switch-switch (uplink)\n- Liaison switch-routeur (router-on-a-stick)\n- Liaison switch-serveur hyperviseur (VMware, Hyper-V)\n- Liaison vers un WLC',
        'prerequisites': '- Liaison physique opérationnelle entre les équipements\n- VLANs déjà créés sur les deux switches\n- Droits de configuration sur les deux équipements',
        'expected_outcome': 'L\'interface apparaît dans "show interfaces trunk" avec les VLANs autorisés et le VLAN natif correct des deux côtés.',
        'best_practices': '- Désactiver DTP (switchport nonegotiate) pour forcer le mode trunk statique\n- Restreindre les VLANs autorisés (ne pas laisser "all")\n- Utiliser un VLAN natif dédié différent du VLAN 1\n- Configurer des deux côtés avant d\'activer le port\n- Vérifier la cohérence STP après activation',
        'common_pitfalls': '- VLAN natif différent des deux côtés (CDP warning native VLAN mismatch)\n- Oublier la commande d\'encapsulation dot1q sur IOS classique\n- Autoriser tous les VLANs sur le trunk (risque de boucle STP)\n- DTP actif sur l\'un des côtés empêchant la négociation',
        'notes': 'Sur certains Catalyst (IOS-XE récent), la commande "switchport trunk encapsulation dot1q" n\'est pas nécessaire.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'switch',
        'difficulty': 'intermediate', 'criticality': 'high',
        'estimated_duration': 15, 'status': 'published',
        'category': 'vlan-switching', 'is_featured': True,
        'requires_maintenance_window': True, 'save_config_required': True,
        'variables': [
            {'name': 'trunk_interface', 'label': 'Interface trunk',     'field_type': 'interface', 'placeholder': 'GigabitEthernet0/24', 'order': 1},
            {'name': 'allowed_vlans',   'label': 'VLANs autorisés',    'field_type': 'text',      'placeholder': '10,20,30,99',         'help_text': 'Liste séparée par des virgules', 'order': 2},
            {'name': 'native_vlan',     'label': 'VLAN natif',         'field_type': 'vlan',      'placeholder': '99',                  'order': 3},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Accéder à l\'interface et configurer le trunk',
                'explanation': 'Forcer l\'encapsulation 802.1Q, activer le mode trunk statique et désactiver DTP.',
                'command_template': 'configure terminal\ninterface {{ trunk_interface }}\n switchport trunk encapsulation dot1q\n switchport mode trunk\n switchport nonegotiate',
                'expected_result': 'Interface configurée en trunk statique, DTP désactivé.',
                'warning': 'Certains IOS-XE n\'ont pas la commande d\'encapsulation — ignorer l\'erreur le cas échéant.',
                'order': 1,
                'real_world_example': 'Exemple : tu relies le switch de l\'etage 1 au switch de la salle reseau via le port Gi0/24. Ce lien trunk fait passer tous les VLANs (IT, Compta, VoIP) en meme temps sur un seul cable. Sans trunk, il faudrait un cable dedie par VLAN — beaucoup moins pratique.',
            },
            {
                'step_number': 2, 'title': 'Définir les VLANs autorisés et le VLAN natif',
                'explanation': 'Restreindre le trunk aux VLANs nécessaires et configurer un VLAN natif non-défaut.',
                'command_template': ' switchport trunk allowed vlan {{ allowed_vlans }}\n switchport trunk native vlan {{ native_vlan }}',
                'expected_result': 'Seuls les VLANs listés sont transportés. VLAN natif = {{ native_vlan }}.',
                'warning': 'Le VLAN natif DOIT être identique des deux côtés du lien sous peine de fuite inter-VLAN.',
                'order': 2,
                'real_world_example': 'Exemple : tu autorises uniquement les VLANs 10, 20 et 30 sur ce trunk. Si quelqu\'un cree un VLAN 99 par accident, il ne passera pas automatiquement sur ce lien — c\'est une bonne pratique de securite. Le VLAN 99 est choisi comme VLAN natif car il est dedie au management et non utilise par les utilisateurs.',
            },
            {
                'step_number': 3, 'title': 'Sauvegarder',
                'explanation': 'Valider et persister la configuration.',
                'command_template': 'end\ncopy running-config startup-config',
                'expected_result': '[OK]', 'warning': '', 'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre', 'title': 'Vérifier l\'état physique du port', 'command': 'show interfaces {{ trunk_interface }} status', 'expected_output': 'connected', 'order': 1},
            {'check_type': 'pre', 'title': 'Vérifier les VLANs existants', 'command': 'show vlan brief', 'expected_output': 'VLANs {{ allowed_vlans }} présents avec statut active', 'order': 2},
            {'check_type': 'post', 'title': 'Vérifier le trunk actif', 'command': 'show interfaces trunk', 'expected_output': '{{ trunk_interface }} listed, mode "on", encapsulation "802.1q"', 'order': 1},
            {'check_type': 'post', 'title': 'Vérifier les VLANs autorisés', 'command': 'show interfaces {{ trunk_interface }} trunk', 'expected_output': 'VLANs allowed: {{ allowed_vlans }} — VLANs in STP forwarding', 'order': 2},
            {'check_type': 'validation', 'title': 'Vérifier l\'absence de native VLAN mismatch', 'command': 'show cdp neighbors {{ trunk_interface }} detail', 'expected_output': 'Aucune alerte "native VLAN mismatch" dans la sortie.', 'order': 1},
        ],
        'rollback': {
            'conditions': 'Perte de connectivité ou mauvaise configuration trunk détectée.',
            'rollback_commands': 'configure terminal\ninterface {{ trunk_interface }}\n no switchport trunk allowed vlan\n no switchport trunk native vlan\n switchport mode access\nend\ncopy running-config startup-config',
            'notes': 'Le rollback coupe TOUT le trafic inter-VLAN passant par ce lien. Anticiper l\'impact.',
        },
    },

    # ── 3. Inter-VLAN L3 ─────────────────────────────────────────────────────
    {
        'title': 'Configurer l\'inter-VLAN sur switch L3 (SVI)',
        'summary': 'Routage inter-VLAN via interfaces SVI sur un switch Cisco de couche 3.',
        'objective': 'Permettre la communication entre VLANs en configurant des interfaces SVI avec adresses IP passerelles sur un switch L3 Cisco.',
        'use_cases': '- Communication VLAN IT ↔ VLAN Serveurs\n- Routage local sans routeur dédié (Catalyst 3560/3750/9300)\n- Architecture campus avec distribution L3',
        'prerequisites': '- Switch Cisco L3 (Catalyst 3560, 3750, 9300, etc.)\n- VLANs créés et actifs dans la base VLAN\n- Plan d\'adressage IP des sous-réseaux défini\n- Licence IP Base ou IP Services selon la plateforme',
        'expected_outcome': 'La commande "show ip route" affiche les routes connectées pour chaque SVI. Un ping entre deux hôtes de VLANs différents aboutit.',
        'best_practices': '- Activer "ip routing" avant toute configuration SVI\n- Vérifier que le VLAN est "active" dans show vlan brief avant de créer la SVI\n- Documenter les adresses passerelles dans le plan d\'adressage\n- Configurer les hôtes avec la SVI comme gateway par défaut',
        'common_pitfalls': '- Oublier la commande "ip routing" (erreur la plus fréquente)\n- Créer la SVI avant que le VLAN n\'existe — la SVI reste down/down\n- Masque de sous-réseau incorrect → routes mal installées\n- Ne pas avoir de port actif dans le VLAN → SVI reste down',
        'notes': 'La SVI monte uniquement si : (1) le VLAN existe, (2) au moins un port actif est membre du VLAN.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'switch',
        'difficulty': 'intermediate', 'criticality': 'high',
        'estimated_duration': 20, 'status': 'published',
        'category': 'routage', 'is_featured': True,
        'requires_maintenance_window': True, 'save_config_required': True,
        'variables': [
            {'name': 'vlan_id',     'label': 'ID du VLAN',           'field_type': 'vlan',   'placeholder': '10',            'order': 1},
            {'name': 'svi_ip',      'label': 'IP passerelle (SVI)',   'field_type': 'ip',     'placeholder': '192.168.10.1',  'order': 2},
            {'name': 'subnet_mask', 'label': 'Masque de sous-réseau', 'field_type': 'subnet', 'placeholder': '255.255.255.0', 'order': 3},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Activer le routage IP',
                'explanation': 'Activer la fonctionnalité de routage Layer 3 au niveau global du switch.',
                'command_template': 'configure terminal\nip routing',
                'expected_result': 'Routing activé — le switch peut router entre sous-réseaux.',
                'warning': 'Commande globale : elle active le routage sur l\'ensemble de l\'équipement.',
                'order': 1,
                'real_world_example': 'Exemple : sans cette commande, le switch 3750 sait deplacer les trames entre ses ports (commutation), mais il ne sait pas faire circuler des paquets entre le VLAN 10 (192.168.10.0/24) et le VLAN 20 (192.168.20.0/24). C\'est comme activer le moteur d\'une voiture avant de pouvoir conduire.',
            },
            {
                'step_number': 2, 'title': 'Créer la SVI et assigner l\'adresse IP',
                'explanation': 'Créer l\'interface VLAN virtuelle (SVI) et lui attribuer l\'adresse IP qui servira de passerelle aux hôtes du VLAN.',
                'command_template': 'interface vlan {{ vlan_id }}\n ip address {{ svi_ip }} {{ subnet_mask }}\n no shutdown',
                'expected_result': 'SVI {{ vlan_id }} en état up/up avec IP {{ svi_ip }}/{{ subnet_mask }}.',
                'warning': 'Si la SVI reste down/down, vérifier que le VLAN existe et qu\'un port actif lui est assigné.',
                'order': 2,
                'real_world_example': 'Exemple : tu crees la SVI du VLAN 10 avec l\'IP 192.168.10.1. Tous les PCs du VLAN 10 doivent configurer 192.168.10.1 comme passerelle par defaut. Quand un PC du VLAN 10 veut parler a un PC du VLAN 20, il envoie le paquet a cette IP, et c\'est le switch L3 qui se charge de l\'acheminer vers le bon VLAN.',
            },
            {
                'step_number': 3, 'title': 'Vérifier la table de routage et sauvegarder',
                'explanation': 'Confirmer que la route connectée est installée dans la RIB puis persister la config.',
                'command_template': 'end\nshow ip route\ncopy running-config startup-config',
                'expected_result': 'Route "C" (connected) visible pour le réseau {{ svi_ip }}/24.',
                'warning': '', 'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre', 'title': 'Vérifier que le VLAN est actif', 'command': 'show vlan id {{ vlan_id }}', 'expected_output': 'VLAN {{ vlan_id }}  active', 'order': 1},
            {'check_type': 'pre', 'title': 'Vérifier que ip routing est absent', 'command': 'show running-config | include ip routing', 'expected_output': 'Ligne vide si ip routing n\'est pas encore activé.', 'order': 2},
            {'check_type': 'post', 'title': 'Vérifier l\'état de la SVI', 'command': 'show interfaces vlan {{ vlan_id }}', 'expected_output': 'Vlan{{ vlan_id }} is up, line protocol is up', 'order': 1},
            {'check_type': 'post', 'title': 'Vérifier la route connectée', 'command': 'show ip route connected', 'expected_output': 'C  192.168.x.0/24 is directly connected, Vlan{{ vlan_id }}', 'order': 2},
            {'check_type': 'validation', 'title': 'Ping depuis la SVI', 'command': 'ping {{ svi_ip }} source vlan {{ vlan_id }}', 'expected_output': 'Success rate is 100 percent (5/5)', 'order': 1},
        ],
        'rollback': {
            'conditions': 'Problèmes de routage constatés ou adressage incorrect après déploiement.',
            'rollback_commands': 'configure terminal\nno interface vlan {{ vlan_id }}\nend\ncopy running-config startup-config',
            'notes': 'Supprimer la SVI isole tous les hôtes du VLAN {{ vlan_id }} — impact immédiat sur la connectivité.',
        },
    },

    # ── 4. Route statique ─────────────────────────────────────────────────────
    {
        'title': 'Configurer une route statique Cisco',
        'summary': 'Ajout d\'une route statique ou route par défaut sur un routeur ou switch L3 Cisco.',
        'objective': 'Configurer une route statique pointant vers un prochain saut ou une interface de sortie pour atteindre un réseau distant.',
        'use_cases': '- Route par défaut vers Internet (default route)\n- Route vers un réseau distant via VPN ou WAN\n- Route de secours (floating static route)\n- Stub network sans protocole de routage dynamique',
        'prerequisites': '- Accès configure terminal\n- Prochain saut (next-hop) ou interface de sortie connu\n- ip routing activé sur switch L3',
        'expected_outcome': 'La route apparaît dans "show ip route" avec le code "S" (Static). Les pings vers la destination aboutissent.',
        'best_practices': '- Toujours spécifier un next-hop IP plutôt qu\'une interface seule (sauf PPP)\n- Utiliser une distance administrative > 1 pour une floating route\n- Documenter la justification de chaque route statique\n- Vérifier la récursivité : le next-hop doit être atteignable',
        'common_pitfalls': '- Next-hop inaccessible → route absente de la RIB\n- Masque incorrect (confusion /24 vs 255.255.255.0)\n- Route statique en conflit avec route dynamique (priorité distance admin)\n- Oubli de la route retour du côté distant (black hole)',
        'notes': 'La distance administrative par défaut d\'une route statique est 1. Une route dynamique (OSPF=110, EIGRP=90) la supplantera si la distance est plus faible.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'router',
        'difficulty': 'beginner', 'criticality': 'medium',
        'estimated_duration': 10, 'status': 'published',
        'category': 'routage', 'is_featured': False,
        'requires_maintenance_window': False, 'save_config_required': True,
        'variables': [
            {'name': 'dest_network',  'label': 'Réseau destination',  'field_type': 'ip',     'placeholder': '10.0.0.0',      'order': 1},
            {'name': 'dest_mask',     'label': 'Masque destination',  'field_type': 'subnet', 'placeholder': '255.255.255.0', 'order': 2},
            {'name': 'next_hop',      'label': 'Prochain saut (IP)',  'field_type': 'ip',     'placeholder': '192.168.1.254', 'order': 3},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Ajouter la route statique',
                'explanation': 'Configurer la route statique avec le réseau cible et le prochain saut.',
                'command_template': 'configure terminal\nip route {{ dest_network }} {{ dest_mask }} {{ next_hop }}',
                'expected_result': 'Route visible dans show ip route avec code S.',
                'warning': '', 'order': 1,
                'real_world_example': 'Exemple : ton routeur de bureau ne connait pas le reseau du siege (10.10.0.0/24). Tu lui indiques manuellement : "Pour atteindre 10.10.0.0/24, envoie les paquets vers 192.168.1.254" (le routeur WAN). C\'est comme donner une adresse a un livreur qui ne connait pas le chemin — tu lui dis exactement par ou passer.',
            },
            {
                'step_number': 2, 'title': 'Vérifier et sauvegarder',
                'explanation': 'Confirmer l\'installation de la route dans la RIB et persister.',
                'command_template': 'end\nshow ip route {{ dest_network }}\ncopy running-config startup-config',
                'expected_result': 'S  {{ dest_network }}/xx [1/0] via {{ next_hop }}', 'warning': '', 'order': 2,
            },
        ],
        'checks': [
            {'check_type': 'pre', 'title': 'Vérifier la table de routage existante', 'command': 'show ip route', 'expected_output': 'Confirmer qu\'aucune route conflictuelle n\'existe pour {{ dest_network }}.', 'order': 1},
            {'check_type': 'pre', 'title': 'Vérifier la joignabilité du next-hop', 'command': 'ping {{ next_hop }}', 'expected_output': 'Success rate is 100 percent', 'order': 2},
            {'check_type': 'post', 'title': 'Confirmer l\'installation de la route', 'command': 'show ip route {{ dest_network }}', 'expected_output': 'S  {{ dest_network }} [1/0] via {{ next_hop }}', 'order': 1},
            {'check_type': 'validation', 'title': 'Ping vers le réseau destination', 'command': 'ping {{ dest_network }}', 'expected_output': 'Success rate > 0 percent', 'order': 1},
        ],
        'rollback': {
            'conditions': 'Problème de routage causé par la route statique ou route devenue obsolète.',
            'rollback_commands': 'configure terminal\nno ip route {{ dest_network }} {{ dest_mask }} {{ next_hop }}\nend\ncopy running-config startup-config',
            'notes': 'La suppression de la route peut créer un black hole si aucune route alternative n\'existe.',
        },
    },

    # ── 5. ACL Standard ──────────────────────────────────────────────────────
    {
        'title': 'Créer une ACL standard Cisco',
        'summary': 'Création et application d\'une liste de contrôle d\'accès standard (filtrage sur IP source uniquement).',
        'objective': 'Créer une ACL standard numérotée ou nommée pour filtrer le trafic basé sur l\'adresse IP source, puis l\'appliquer sur une interface.',
        'use_cases': '- Bloquer un sous-réseau entier en entrée d\'une interface\n- Restreindre l\'accès VTY (SSH/Telnet) à certains hôtes\n- Filtrer les mises à jour de routage (distribute-list)\n- Contrôle d\'accès basique sur un lien WAN',
        'prerequisites': '- Topologie réseau connue (source des flux à filtrer)\n- Interface cible identifiée\n- Règle de sécurité validée par l\'équipe réseau',
        'expected_outcome': 'L\'ACL apparaît dans "show access-lists". Le trafic correspondant est filtré selon les règles configurées.',
        'best_practices': '- Placer une ACL standard AU PLUS PRÈS de la DESTINATION\n- Toujours finir par un "deny any" explicite avec log\n- Tester avec "show access-lists" et vérifier les hitcounts\n- Préférer les ACL nommées aux ACL numérotées (plus lisibles)\n- Commenter chaque règle avec "remark"',
        'common_pitfalls': '- Appliquer l\'ACL dans le mauvais sens (in vs out)\n- Oublier le "deny any any" implicite à la fin (trafic légitime bloqué)\n- Appliquer l\'ACL standard trop près de la source (filtre trop large)\n- Wildcard incorrecte (confusion avec masque de sous-réseau)',
        'notes': 'Les ACL standards (1-99, 1300-1999) filtrent uniquement sur l\'IP source. Pour filtrer source+destination+port, utiliser une ACL extended.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'router',
        'difficulty': 'intermediate', 'criticality': 'high',
        'estimated_duration': 15, 'status': 'published',
        'category': 'securite-acl', 'is_featured': True,
        'requires_maintenance_window': True, 'save_config_required': True,
        'variables': [
            {'name': 'acl_name',      'label': 'Nom/numéro ACL',      'field_type': 'text',      'placeholder': 'BLOCK_GUEST',       'order': 1},
            {'name': 'source_net',    'label': 'Réseau source',        'field_type': 'ip',        'placeholder': '192.168.100.0',     'order': 2},
            {'name': 'wildcard',      'label': 'Wildcard mask',        'field_type': 'subnet',    'placeholder': '0.0.0.255',         'order': 3},
            {'name': 'interface_acl', 'label': 'Interface cible',      'field_type': 'interface', 'placeholder': 'GigabitEthernet0/1','order': 4},
            {'name': 'direction',     'label': 'Direction (in/out)',   'field_type': 'select',    'placeholder': 'in',                'select_options': 'in,out', 'order': 5},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Créer l\'ACL standard',
                'explanation': 'Définir les règles de l\'ACL avec un deny sur le réseau source et un permit any pour le reste.',
                'command_template': 'configure terminal\nip access-list standard {{ acl_name }}\n remark Genere par NetOps Pro Hub\n deny {{ source_net }} {{ wildcard }} log\n permit any\n exit',
                'expected_result': 'ACL créée, visible dans show access-lists.',
                'warning': 'Le "permit any" final est indispensable sinon tout le trafic sera bloqué (deny implicite).',
                'order': 1,
                'real_world_example': 'Exemple : tu veux empecher le reseau des stagiaires (192.168.100.0/24) d\'acceder au reseau des serveurs. Tu crees l\'ACL BLOCK_STAGIAIRES avec une regle "deny 192.168.100.0 0.0.0.255". Le "permit any" en dessous permet au reste du trafic de passer normalement. Sans ce "permit any", personne ne pourrait plus rien faire.',
            },
            {
                'step_number': 2, 'title': 'Appliquer l\'ACL sur l\'interface',
                'explanation': 'Lier l\'ACL à l\'interface dans la direction choisie.',
                'command_template': 'interface {{ interface_acl }}\n ip access-group {{ acl_name }} {{ direction }}\n exit',
                'expected_result': 'ACL appliquée sur {{ interface_acl }} en {{ direction }}.',
                'warning': 'L\'ACL est active immédiatement après cette commande. Vérifier l\'impact avant.',
                'order': 2,
                'real_world_example': 'Exemple : tu appliques l\'ACL BLOCK_STAGIAIRES en "in" sur l\'interface Gi0/1 (le port connecte au switch des stagiaires). Ainsi, tout trafic venant du reseau stagiaires et entrant sur Gi0/1 est filtre des son arrivee sur le routeur — avant meme d\'aller plus loin dans le reseau.',
            },
            {
                'step_number': 3, 'title': 'Sauvegarder',
                'explanation': 'Persister la configuration.',
                'command_template': 'end\ncopy running-config startup-config',
                'expected_result': '[OK]', 'warning': '', 'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'pre', 'title': 'Vérifier les ACL existantes sur l\'interface', 'command': 'show ip interface {{ interface_acl }}', 'expected_output': 'Inbound/Outbound access list is not set (ou ACL différente)', 'order': 1},
            {'check_type': 'post', 'title': 'Vérifier la création de l\'ACL', 'command': 'show access-lists {{ acl_name }}', 'expected_output': 'Standard IP access list {{ acl_name }} — règles listées', 'order': 1},
            {'check_type': 'post', 'title': 'Vérifier l\'application sur l\'interface', 'command': 'show ip interface {{ interface_acl }}', 'expected_output': 'Inbound/Outbound access list is {{ acl_name }}', 'order': 2},
            {'check_type': 'validation', 'title': 'Vérifier les hitcounts', 'command': 'show access-lists {{ acl_name }}', 'expected_output': 'Les compteurs (matches) s\'incrémentent sur la règle deny.', 'order': 1},
        ],
        'rollback': {
            'conditions': 'L\'ACL bloque du trafic légitime ou doit être retirée.',
            'rollback_commands': 'configure terminal\ninterface {{ interface_acl }}\n no ip access-group {{ acl_name }} {{ direction }}\n exit\nno ip access-list standard {{ acl_name }}\nend\ncopy running-config startup-config',
            'notes': 'Retirer l\'ACL de l\'interface AVANT de la supprimer pour éviter les erreurs de référence.',
        },
    },

    # ── 6. NAT Overload (PAT) ─────────────────────────────────────────────────
    {
        'title': 'Configurer NAT overload (PAT) Cisco',
        'summary': 'Configuration du NAT dynamique avec surcharge (PAT) pour partager une IP publique entre plusieurs hôtes privés.',
        'objective': 'Permettre à un ou plusieurs réseaux privés d\'accéder à Internet via une seule adresse IP publique en utilisant la translation de port (PAT).',
        'use_cases': '- Accès Internet d\'un LAN via une seule IP publique\n- Connexion de plusieurs sites via un seul lien WAN\n- Architecture SOHO / PME',
        'prerequisites': '- Interface WAN avec IP publique configurée\n- Interface LAN avec IP privée configurée\n- ip routing activé',
        'expected_outcome': '"show ip nat translations" affiche les translations actives. Les hôtes internes peuvent joindre Internet.',
        'best_practices': '- Toujours définir des ACL précises pour le NAT (ne pas natifier tout le trafic)\n- Utiliser une ACL nommée pour les sources NAT\n- Vérifier "show ip nat statistics" pour diagnostiquer\n- Documenter les plages d\'adresses privées natifiées',
        'common_pitfalls': '- ACL NAT incorrecte → trafic non natifié ou trafic incorrect natifié\n- Interface WAN/LAN inversées (ip nat inside/outside)\n- Oublier "ip nat inside" ou "ip nat outside" sur les interfaces\n- Translations NAT en cache causant des problèmes après changement',
        'notes': 'NAT overload = PAT (Port Address Translation). La surcharge utilise les numéros de port TCP/UDP pour différencier les sessions.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'router',
        'difficulty': 'intermediate', 'criticality': 'critical',
        'estimated_duration': 20, 'status': 'published',
        'category': 'securite-acl', 'is_featured': True,
        'requires_maintenance_window': True, 'save_config_required': True,
        'variables': [
            {'name': 'inside_network',    'label': 'Réseau interne (source)', 'field_type': 'ip',        'placeholder': '192.168.1.0',       'order': 1},
            {'name': 'inside_wildcard',   'label': 'Wildcard réseau interne', 'field_type': 'subnet',    'placeholder': '0.0.0.255',         'order': 2},
            {'name': 'inside_interface',  'label': 'Interface inside (LAN)',  'field_type': 'interface', 'placeholder': 'GigabitEthernet0/1','order': 3},
            {'name': 'outside_interface', 'label': 'Interface outside (WAN)', 'field_type': 'interface', 'placeholder': 'GigabitEthernet0/0','order': 4},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Créer l\'ACL définissant les sources NAT',
                'explanation': 'Définir les adresses internes autorisées à être natifiées via une ACL.',
                'command_template': 'configure terminal\nip access-list standard NAT_INSIDE_SOURCES\n permit {{ inside_network }} {{ inside_wildcard }}\n exit',
                'expected_result': 'ACL créée pour identifier les sources NAT.',
                'warning': '', 'order': 1,
                'real_world_example': 'Exemple : dans une PME, le reseau interne est 192.168.1.0/24. Cette ACL dit au routeur : "Tous les PCs de ce reseau ont le droit d\'aller sur Internet via NAT." Si tu ne mets pas un PC dans cette ACL, il ne pourra pas sortir sur Internet, meme s\'il est correctement configure.',
            },
            {
                'step_number': 2, 'title': 'Configurer le NAT overload',
                'explanation': 'Lier l\'ACL source au NAT overload sur l\'interface outside.',
                'command_template': 'ip nat inside source list NAT_INSIDE_SOURCES interface {{ outside_interface }} overload',
                'expected_result': 'Règle NAT créée. Trafic des sources listées sera natifié.',
                'warning': '', 'order': 2,
                'real_world_example': 'Exemple : 50 PCs dans le bureau partagent une seule IP publique (ex: 90.200.1.10 fournie par le FAI). Quand le PC de Paul (192.168.1.5) ouvre YouTube, le routeur traduit : "192.168.1.5:50234 devient 90.200.1.10:50234". Quand la reponse revient, le routeur sait la renvoyer a Paul grace au numero de port. C\'est ca le NAT overload.',
            },
            {
                'step_number': 3, 'title': 'Configurer les interfaces inside et outside',
                'explanation': 'Désigner les interfaces LAN (inside) et WAN (outside) pour le NAT.',
                'command_template': 'interface {{ inside_interface }}\n ip nat inside\n exit\ninterface {{ outside_interface }}\n ip nat outside\n exit',
                'expected_result': 'Interfaces désignées. NAT actif sur les flux traversant ces interfaces.',
                'warning': 'Une seule interface inside et une seule outside suffisent pour PAT simple.',
                'order': 3,
                'real_world_example': 'Exemple : Gi0/1 est branche au switch LAN (reseau interne) -> "ip nat inside". Gi0/0 est branche au modem FAI (Internet) -> "ip nat outside". Si tu inverses les deux, le NAT ne fonctionnera pas — le routeur chercherait a natter le trafic dans le mauvais sens.',
            },
            {
                'step_number': 4, 'title': 'Sauvegarder',
                'explanation': '', 'command_template': 'end\ncopy running-config startup-config',
                'expected_result': '[OK]', 'warning': '', 'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre', 'title': 'Vérifier l\'IP de l\'interface outside', 'command': 'show interfaces {{ outside_interface }}', 'expected_output': 'IP publique configurée et interface up/up', 'order': 1},
            {'check_type': 'post', 'title': 'Vérifier les translations actives', 'command': 'show ip nat translations', 'expected_output': 'Entrées TCP/UDP avec Inside Local → Inside Global', 'order': 1},
            {'check_type': 'post', 'title': 'Vérifier les statistiques NAT', 'command': 'show ip nat statistics', 'expected_output': 'Total active translations > 0, hits > 0', 'order': 2},
            {'check_type': 'validation', 'title': 'Test de connectivité Internet', 'command': 'ping 8.8.8.8 source {{ inside_interface }}', 'expected_output': 'Success rate is 100 percent', 'order': 1},
        ],
        'rollback': {
            'conditions': 'NAT causant des problèmes de connectivité ou configuration incorrecte.',
            'rollback_commands': 'configure terminal\nno ip nat inside source list NAT_INSIDE_SOURCES interface {{ outside_interface }} overload\ninterface {{ inside_interface }}\n no ip nat inside\n exit\ninterface {{ outside_interface }}\n no ip nat outside\n exit\nno ip access-list standard NAT_INSIDE_SOURCES\nend\nclear ip nat translation *\ncopy running-config startup-config',
            'notes': 'clear ip nat translation * efface toutes les translations actives — impact immédiat sur les sessions en cours.',
        },
    },

    # ── 7. OSPF basique ───────────────────────────────────────────────────────
    {
        'title': 'Configurer OSPF area 0 sur routeur Cisco',
        'summary': 'Activation d\'OSPF sur un routeur Cisco et annonce de réseaux dans l\'area backbone.',
        'objective': 'Déployer OSPF (Open Shortest Path First) pour assurer le routage dynamique entre routeurs dans l\'area 0 (backbone).',
        'use_cases': '- Routage dynamique dans un réseau d\'entreprise\n- Remplacement de routes statiques complexes\n- Convergence automatique après une panne\n- Multi-area pour architectures hiérarchiques',
        'prerequisites': '- Interfaces avec adresses IP configurées\n- Connectivité L2 entre les routeurs voisins\n- Process ID OSPF défini (local à l\'équipement)\n- Router-ID unique pour chaque routeur',
        'expected_outcome': '"show ip ospf neighbor" affiche les voisins en état FULL. Les routes OSPF apparaissent dans "show ip route" avec le code "O".',
        'best_practices': '- Configurer un Router-ID explicite (plus stable qu\'une IP dynamique)\n- Utiliser des interfaces loopback pour le Router-ID\n- Configurer "passive-interface" sur les interfaces non-OSPF (sécurité)\n- Authentification OSPF MD5 en production\n- Documenter les areas et les network statements',
        'common_pitfalls': '- Wildcard incorrect dans le "network" statement\n- Area mismatch entre voisins (neighbor reste en INIT)\n- MTU mismatch empêchant la formation de l\'adjacency (state EXSTART)\n- Timer mismatch (hello/dead) entre voisins\n- Oubli de "passive-interface" sur les interfaces LAN',
        'notes': 'Le Process ID OSPF est local à l\'équipement et n\'a pas besoin de correspondre entre routeurs. Le Router-ID doit être unique dans le domaine OSPF.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'router',
        'difficulty': 'advanced', 'criticality': 'critical',
        'estimated_duration': 30, 'status': 'published',
        'category': 'routage', 'is_featured': True,
        'requires_maintenance_window': True, 'save_config_required': True,
        'variables': [
            {'name': 'process_id',   'label': 'Process ID OSPF',      'field_type': 'number',    'placeholder': '1',               'order': 1},
            {'name': 'router_id',    'label': 'Router-ID',             'field_type': 'ip',        'placeholder': '1.1.1.1',         'order': 2},
            {'name': 'network',      'label': 'Réseau à annoncer',     'field_type': 'ip',        'placeholder': '192.168.1.0',     'order': 3},
            {'name': 'wildcard',     'label': 'Wildcard mask',         'field_type': 'subnet',    'placeholder': '0.0.0.255',       'order': 4},
            {'name': 'passive_intf', 'label': 'Interface passive (LAN)','field_type': 'interface', 'placeholder': 'GigabitEthernet0/1','order': 5},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Activer OSPF et configurer le Router-ID',
                'explanation': 'Démarrer le processus OSPF et définir un Router-ID stable.',
                'command_template': 'configure terminal\nrouter ospf {{ process_id }}\n router-id {{ router_id }}\n auto-cost reference-bandwidth 10000',
                'expected_result': 'Processus OSPF {{ process_id }} actif avec Router-ID {{ router_id }}.',
                'warning': 'Changer le router-id nécessite un "clear ip ospf process" pour prendre effet.',
                'order': 1,
                'real_world_example': 'Exemple : tu as 3 routeurs dans ton reseau d\'entreprise. Chacun a un Router-ID unique : R1=1.1.1.1, R2=2.2.2.2, R3=3.3.3.3. Ces IDs sont comme des cartes d\'identite. OSPF les utilise pour savoir qui est qui lors des echanges. Si deux routeurs avaient le meme Router-ID, OSPF serait completement perdu.',
            },
            {
                'step_number': 2, 'title': 'Annoncer le réseau dans l\'area 0',
                'explanation': 'Indiquer quel réseau doit être annoncé dans OSPF et dans quelle area.',
                'command_template': ' network {{ network }} {{ wildcard }} area 0',
                'expected_result': 'Réseau {{ network }} annoncé dans l\'area 0.',
                'warning': 'Le wildcard OSPF est l\'inverse du masque de sous-réseau (0.0.0.255 pour /24).',
                'order': 2,
                'real_world_example': 'Exemple : tu annonces le reseau 192.168.10.0 avec le wildcard 0.0.0.255. Cela signifie : "OSPF, prends en charge toutes les interfaces dont l\'IP est dans 192.168.10.X". Le wildcard 0.0.0.255 est l\'inverse du masque /24 (255.255.255.0). Tous les routeurs OSPF du domaine vont apprendre ce reseau automatiquement.',
            },
            {
                'step_number': 3, 'title': 'Configurer les interfaces passives',
                'explanation': 'Désactiver l\'envoi de hello OSPF sur les interfaces LAN (sécurité).',
                'command_template': ' passive-interface {{ passive_intf }}\n exit',
                'expected_result': 'Aucun paquet hello OSPF envoyé sur {{ passive_intf }}.',
                'warning': '', 'order': 3,
                'real_world_example': 'Exemple : l\'interface Gi0/1 est branchee aux PCs des employes. Ces PCs n\'ont pas besoin de recevoir les messages OSPF (hellos). En mettant Gi0/1 en "passive-interface", le routeur continue d\'annoncer le reseau dans OSPF, mais n\'envoie plus de hellos vers les PCs. C\'est une bonne pratique de securite et ca reduit le trafic inutile.',
            },
            {
                'step_number': 4, 'title': 'Sauvegarder',
                'explanation': '',
                'command_template': 'end\ncopy running-config startup-config',
                'expected_result': '[OK]', 'warning': '', 'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre', 'title': 'Vérifier la connectivité L3 vers le voisin', 'command': 'ping <ip_voisin>', 'expected_output': 'Success rate is 100 percent', 'order': 1},
            {'check_type': 'pre', 'title': 'Vérifier l\'absence d\'OSPF existant', 'command': 'show ip ospf', 'expected_output': 'Pas de processus OSPF actif (ou process ID différent)', 'order': 2},
            {'check_type': 'post', 'title': 'Vérifier la formation des adjacences', 'command': 'show ip ospf neighbor', 'expected_output': 'Voisins OSPF en état FULL/DR ou FULL/BDR', 'order': 1},
            {'check_type': 'post', 'title': 'Vérifier les routes OSPF', 'command': 'show ip route ospf', 'expected_output': 'Routes "O" apprises depuis les voisins OSPF', 'order': 2},
            {'check_type': 'validation', 'title': 'Vérifier la base de données LSDB', 'command': 'show ip ospf database', 'expected_output': 'Router LSAs et Network LSAs présents dans l\'area 0', 'order': 1},
            {'check_type': 'troubleshooting', 'title': 'Diagnostiquer adjacence bloquée', 'command': 'debug ip ospf adj', 'expected_output': 'Messages d\'établissement d\'adjacence — vérifier area et auth', 'order': 1},
        ],
        'rollback': {
            'conditions': 'OSPF cause des problèmes de routage ou des boucles détectées.',
            'rollback_commands': 'configure terminal\nno router ospf {{ process_id }}\nend\ncopy running-config startup-config',
            'notes': 'Supprimer le processus OSPF retire TOUTES les routes apprises dynamiquement — prévoir des routes statiques de secours.',
        },
    },

    # ── 8. SNMP v2c ───────────────────────────────────────────────────────────
    {
        'title': 'Configurer SNMPv2c sur équipement Cisco',
        'summary': 'Activation de SNMP v2c pour supervision réseau avec community string read-only et/ou read-write.',
        'objective': 'Permettre à un NMS (Network Management System) de superviser un équipement Cisco via SNMP v2c.',
        'use_cases': '- Intégration dans un NMS (Zabbix, PRTG, SolarWinds)\n- Supervision des performances et de l\'état des interfaces\n- Collecte de métriques CPU, mémoire, bande passante\n- Alertes sur changements d\'état (SNMP traps)',
        'prerequisites': '- IP de supervision (NMS) connue\n- Community strings définies par la politique de sécurité\n- ACL de restriction d\'accès SNMP préparée',
        'expected_outcome': 'Le NMS peut interroger l\'équipement via SNMP. Les traps sont reçus par le serveur de supervision.',
        'best_practices': '- Utiliser une community string différente de "public" et "private"\n- Restreindre l\'accès SNMP via ACL\n- Préférer SNMPv3 en production (authentification + chiffrement)\n- Configurer uniquement read-only sauf si write est nécessaire\n- Limiter les interfaces d\'écoute SNMP si possible',
        'common_pitfalls': '- Community string en clair dans la config (utiliser "snmp-server community" avec ACL)\n- Pas d\'ACL → accès SNMP ouvert à tous\n- Mauvaise version SNMP côté NMS\n- Traps non reçus car firewall bloque UDP 162',
        'notes': 'SNMPv2c reste en clair sur le réseau. En environnement sensible, migrer vers SNMPv3 avec auth SHA et priv AES.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'generic',
        'difficulty': 'beginner', 'criticality': 'medium',
        'estimated_duration': 10, 'status': 'published',
        'category': 'supervision', 'is_featured': False,
        'requires_maintenance_window': False, 'save_config_required': True,
        'variables': [
            {'name': 'community_ro', 'label': 'Community string Read-Only', 'field_type': 'text', 'placeholder': 'MON_RO_COMMUNITY', 'order': 1},
            {'name': 'nms_ip',       'label': 'IP du serveur NMS',          'field_type': 'ip',   'placeholder': '10.0.0.100',        'order': 2},
            {'name': 'location',     'label': 'Localisation (sysLocation)', 'field_type': 'text', 'placeholder': 'DataCenter-Paris-R1', 'order': 3},
            {'name': 'contact',      'label': 'Contact (sysContact)',       'field_type': 'text', 'placeholder': 'noc@entreprise.fr',  'order': 4},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Créer l\'ACL de restriction SNMP',
                'explanation': 'Limiter l\'accès SNMP au seul serveur NMS autorisé.',
                'command_template': 'configure terminal\nip access-list standard ACL_SNMP_ACCESS\n permit {{ nms_ip }}\n deny any log\n exit',
                'expected_result': 'ACL créée pour restreindre SNMP au NMS {{ nms_ip }}.', 'warning': '', 'order': 1,
            },
            {
                'step_number': 2, 'title': 'Configurer SNMP v2c',
                'explanation': 'Activer SNMP avec community RO, traps et informations système.',
                'command_template': 'snmp-server community {{ community_ro }} RO ACL_SNMP_ACCESS\nsnmp-server location {{ location }}\nsnmp-server contact {{ contact }}\nsnmp-server host {{ nms_ip }} version 2c {{ community_ro }}\nsnmp-server enable traps',
                'expected_result': 'SNMP actif, community {{ community_ro }} restreinte au NMS {{ nms_ip }}.', 'warning': '', 'order': 2,
            },
            {
                'step_number': 3, 'title': 'Sauvegarder',
                'explanation': '',
                'command_template': 'end\ncopy running-config startup-config',
                'expected_result': '[OK]', 'warning': '', 'order': 3,
            },
        ],
        'checks': [
            {'check_type': 'post', 'title': 'Vérifier la configuration SNMP', 'command': 'show snmp', 'expected_output': 'SNMP packets input > 0 après un premier poll depuis le NMS', 'order': 1},
            {'check_type': 'post', 'title': 'Vérifier les community strings', 'command': 'show running-config | section snmp', 'expected_output': 'snmp-server community {{ community_ro }} RO ACL_SNMP_ACCESS', 'order': 2},
            {'check_type': 'validation', 'title': 'Tester depuis le NMS', 'command': 'snmpget -v2c -c {{ community_ro }} <ip_equip> sysDescr.0', 'expected_output': 'Retourne la description système de l\'équipement.', 'order': 1},
        ],
        'rollback': {
            'conditions': 'Problème de sécurité ou SNMP à désactiver.',
            'rollback_commands': 'configure terminal\nno snmp-server community {{ community_ro }}\nno snmp-server host {{ nms_ip }}\nno snmp-server enable traps\nend\ncopy running-config startup-config',
            'notes': 'La désactivation SNMP coupe immédiatement la supervision depuis le NMS.',
        },
    },

    # ── 9. Diagnostiquer un trunk down ────────────────────────────────────────
    {
        'title': 'Diagnostiquer un trunk 802.1Q down ou défaillant',
        'summary': 'Procédure de diagnostic d\'un lien trunk Cisco non fonctionnel — vérification état, encapsulation, VLANs, STP.',
        'objective': 'Identifier la cause d\'un lien trunk non opérationnel ou d\'une perte de connectivité inter-VLAN liée au trunk.',
        'use_cases': '- Trunk qui ne monte pas après configuration\n- Perte soudaine de connectivité sur plusieurs VLANs\n- Alerte NMS sur interface trunk down\n- Problème de traffic inter-switch après changement',
        'prerequisites': '- Accès aux deux équipements aux extrémités du trunk\n- Connaître l\'interface trunk concernée\n- Logs ou symptômes du dysfonctionnement',
        'expected_outcome': 'La cause du problème est identifiée parmi : état physique, mode trunk, encapsulation, VLAN natif mismatch, STP blocking.',
        'best_practices': '- Toujours vérifier la couche physique en premier (câble, SFP, état)\n- Comparer la config des deux côtés du trunk\n- Utiliser CDP pour confirmer l\'identité du voisin\n- Vérifier les logs syslog pour des erreurs récentes',
        'common_pitfalls': '- Diagnostic partiel (vérifier un seul côté du trunk)\n- Ignorer les warnings CDP (native VLAN mismatch)\n- Confondre STP blocking avec un problème de configuration\n- Ne pas vérifier les VLANs autorisés côté distant',
        'notes': 'Utiliser cette procédure comme checklist — ne pas sauter d\'étapes. Un trunk down peut avoir plusieurs causes simultanées.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'switch',
        'difficulty': 'intermediate', 'criticality': 'critical',
        'estimated_duration': 25, 'status': 'published',
        'category': 'troubleshooting', 'is_featured': True,
        'requires_maintenance_window': False, 'save_config_required': False,
        'variables': [
            {'name': 'trunk_interface', 'label': 'Interface trunk concernée', 'field_type': 'interface', 'placeholder': 'GigabitEthernet1/0/24', 'order': 1},
            {'name': 'vlan_test',       'label': 'VLAN à tester',             'field_type': 'vlan',      'placeholder': '10',                     'order': 2},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Vérifier l\'état physique de l\'interface',
                'explanation': 'Confirmer que l\'interface est physiquement up avant tout diagnostic logique.',
                'command_template': 'show interfaces {{ trunk_interface }} status\nshow interfaces {{ trunk_interface }}',
                'expected_result': 'connected / up, line protocol is up. Sinon : câble, SFP, port distant à vérifier.',
                'warning': '', 'order': 1,
            },
            {
                'step_number': 2, 'title': 'Vérifier la configuration trunk',
                'explanation': 'Contrôler le mode, l\'encapsulation et les VLANs autorisés sur cette interface.',
                'command_template': 'show interfaces trunk\nshow interfaces {{ trunk_interface }} trunk\nshow running-config interface {{ trunk_interface }}',
                'expected_result': '{{ trunk_interface }} doit apparaître dans show interfaces trunk avec le mode "on" et les VLANs attendus.',
                'warning': 'Si l\'interface n\'apparaît pas dans "show interfaces trunk", le mode trunk n\'est pas actif.',
                'order': 2,
            },
            {
                'step_number': 3, 'title': 'Vérifier le VLAN natif et les warnings CDP',
                'explanation': 'Un native VLAN mismatch cause des fuites inter-VLAN et peut être signalé par CDP.',
                'command_template': 'show cdp neighbors {{ trunk_interface }} detail\nshow logging | include native',
                'expected_result': 'Aucune alerte "native VLAN mismatch". Même VLAN natif des deux côtés.',
                'warning': 'Un native VLAN mismatch est un risque de sécurité (VLAN hopping).', 'order': 3,
            },
            {
                'step_number': 4, 'title': 'Vérifier l\'état STP sur le VLAN',
                'explanation': 'STP peut bloquer un port trunk pour éviter les boucles — vérifier l\'état STP.',
                'command_template': 'show spanning-tree vlan {{ vlan_test }}\nshow spanning-tree interface {{ trunk_interface }} detail',
                'expected_result': 'Port en état "FWD" (Forwarding). Si "BLK" (Blocking) ou "LIS/LRN" → STP en cours de convergence.',
                'warning': 'Ne jamais désactiver STP sans analyse complète — risque de boucle réseau catastrophique.', 'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'pre', 'title': 'État général des interfaces', 'command': 'show interfaces status', 'expected_output': 'Identifier les ports down ou en erreur', 'order': 1},
            {'check_type': 'troubleshooting', 'title': 'Vérifier les erreurs d\'interface', 'command': 'show interfaces {{ trunk_interface }} counters errors', 'expected_output': 'Compteurs d\'erreurs CRC, input errors, output drops — idéalement à 0', 'order': 1},
            {'check_type': 'troubleshooting', 'title': 'Vérifier les logs système', 'command': 'show logging | include {{ trunk_interface }}', 'expected_output': 'Historique des changements d\'état de l\'interface', 'order': 2},
            {'check_type': 'troubleshooting', 'title': 'Vérifier le VLAN dans la base VLAN', 'command': 'show vlan id {{ vlan_test }}', 'expected_output': 'VLAN {{ vlan_test }} active — s\'il est absent, le trunk ne peut pas le transporter', 'order': 3},
            {'check_type': 'validation', 'title': 'Vérifier la connectivité après correction', 'command': 'show interfaces trunk', 'expected_output': '{{ trunk_interface }} listé avec VLANs en forwarding state', 'order': 1},
        ],
        'rollback': {
            'conditions': 'Les modifications de diagnostic ont aggravé le problème.',
            'rollback_commands': 'configure terminal\ninterface {{ trunk_interface }}\n shutdown\n no shutdown\nend',
            'notes': 'Un bounce de l\'interface peut aider si des compteurs d\'erreurs étaient élevés. Documenter les findings avant toute modification.',
        },
    },

    # ── 10. Diagnostiquer adjacence OSPF absente ──────────────────────────────
    {
        'title': 'Diagnostiquer une adjacence OSPF manquante',
        'summary': 'Checklist de diagnostic pour une adjacence OSPF qui ne se forme pas ou reste bloquée (INIT, EXSTART, 2WAY).',
        'objective': 'Identifier et résoudre la cause d\'une adjacence OSPF qui ne passe pas à l\'état FULL entre deux voisins.',
        'use_cases': '- Voisin OSPF absent de show ip ospf neighbor\n- Adjacence bloquée en état EXSTART ou LOADING\n- Perte de routes OSPF après un changement\n- Incident de production lié au routage dynamique',
        'prerequisites': '- Accès aux deux routeurs voisins\n- Configuration OSPF existante\n- Connectivité L3 de base entre les deux routeurs',
        'expected_outcome': 'La cause est identifiée parmi : area mismatch, auth, MTU, timer, subnet. Après correction, état FULL dans show ip ospf neighbor.',
        'best_practices': '- Vérifier dans l\'ordre : L3 connectivity → area → auth → hello/dead → MTU → subnet\n- Utiliser "debug ip ospf adj" avec précaution (impact CPU)\n- Ne jamais modifier l\'area OSPF sans plan de rollback\n- Documenter les changements dans le ticket d\'incident',
        'common_pitfalls': '- Area différente entre les deux voisins (message "no Hello received")\n- Authentification configurée d\'un seul côté\n- MTU mismatch entre les interfaces (adjacence bloquée en EXSTART)\n- Hello/Dead interval différents (adjacence ne se forme pas)',
        'notes': 'L\'état EXSTART/EXCHANGE bloqué indique souvent un MTU mismatch. L\'état INIT indique que les hellos sont reçus mais l\'ID local est absent.',
        'vendor': 'cisco', 'platform': 'ios', 'device_type': 'router',
        'difficulty': 'advanced', 'criticality': 'critical',
        'estimated_duration': 30, 'status': 'published',
        'category': 'troubleshooting', 'is_featured': True,
        'requires_maintenance_window': False, 'save_config_required': False,
        'variables': [
            {'name': 'ospf_interface', 'label': 'Interface OSPF concernée', 'field_type': 'interface', 'placeholder': 'GigabitEthernet0/0', 'order': 1},
            {'name': 'neighbor_ip',   'label': 'IP du voisin attendu',      'field_type': 'ip',        'placeholder': '10.0.0.2',           'order': 2},
            {'name': 'process_id',    'label': 'Process ID OSPF',           'field_type': 'number',    'placeholder': '1',                  'order': 3},
        ],
        'steps': [
            {
                'step_number': 1, 'title': 'Vérifier l\'état des voisins OSPF',
                'explanation': 'Identifier si le voisin apparaît et dans quel état.',
                'command_template': 'show ip ospf neighbor\nshow ip ospf neighbor {{ neighbor_ip }}',
                'expected_result': 'Voisin {{ neighbor_ip }} en état FULL. Sinon noter l\'état : INIT, 2WAY, EXSTART, EXCHANGE, LOADING.',
                'warning': '', 'order': 1,
            },
            {
                'step_number': 2, 'title': 'Vérifier la connectivité L3 de base',
                'explanation': 'S\'assurer que les deux routeurs se pingent mutuellement.',
                'command_template': 'ping {{ neighbor_ip }} source {{ ospf_interface }}\nshow ip interface {{ ospf_interface }}',
                'expected_result': 'Ping 100%. Interface up/up avec IP dans le bon sous-réseau.',
                'warning': '', 'order': 2,
            },
            {
                'step_number': 3, 'title': 'Vérifier la configuration OSPF sur l\'interface',
                'explanation': 'Contrôler les paramètres OSPF : area, timers, authentification, MTU.',
                'command_template': 'show ip ospf interface {{ ospf_interface }}\nshow running-config interface {{ ospf_interface }}',
                'expected_result': 'Area, hello interval (10s), dead interval (40s) visibles. Comparer avec le voisin.',
                'warning': 'Les timers hello et dead doivent être IDENTIQUES des deux côtés.', 'order': 3,
            },
            {
                'step_number': 4, 'title': 'Vérifier le MTU de l\'interface',
                'explanation': 'Un MTU mismatch bloque l\'adjacence en EXSTART/EXCHANGE.',
                'command_template': 'show interfaces {{ ospf_interface }} | include MTU\nshow ip ospf interface {{ ospf_interface }} | include MTU',
                'expected_result': 'MTU identique des deux côtés (1500 bytes par défaut). Sinon ajouter "ip ospf mtu-ignore".',
                'warning': '"ip ospf mtu-ignore" contourne le problème mais ne le résout pas — corriger le MTU est préférable.',
                'order': 4,
            },
        ],
        'checks': [
            {'check_type': 'troubleshooting', 'title': 'Vérifier les paquets hello reçus/envoyés', 'command': 'show ip ospf interface {{ ospf_interface }}', 'expected_output': 'Hello due in X:XX:XX, Neighbor Count > 0', 'order': 1},
            {'check_type': 'troubleshooting', 'title': 'Vérifier les logs OSPF', 'command': 'show logging | include OSPF', 'expected_output': 'Messages de changement d\'état adjacence — identifier erreurs auth ou area', 'order': 2},
            {'check_type': 'troubleshooting', 'title': 'Vérifier les paramètres OSPF globaux', 'command': 'show ip ospf {{ process_id }}', 'expected_output': 'Process ID, Router ID, Area configurations, SPF schedule', 'order': 3},
            {'check_type': 'validation', 'title': 'Confirmer adjacence FULL', 'command': 'show ip ospf neighbor {{ neighbor_ip }}', 'expected_output': '{{ neighbor_ip }}  FULL/DR (ou FULL/BDR ou FULL/DROTHER)', 'order': 1},
            {'check_type': 'validation', 'title': 'Confirmer routes OSPF reçues', 'command': 'show ip route ospf', 'expected_output': 'Routes "O" et/ou "O IA" présentes dans la table de routage', 'order': 2},
        ],
        'rollback': {
            'conditions': 'Modifications effectuées qui n\'ont pas résolu le problème.',
            'rollback_commands': 'configure terminal\ninterface {{ ospf_interface }}\n no ip ospf {{ process_id }} area 0\n exit\nrouter ospf {{ process_id }}\n no network <network> <wildcard> area 0\nend',
            'notes': 'Retirer l\'interface de l\'OSPF supprime les routes appris via cette adjacence — impact routage immédiat.',
        },
    },
]


class Command(BaseCommand):
    help = 'Charge les données de démonstration NetOps Pro Hub'

    def handle(self, *args, **options):
        self.stdout.write('Nettoyage des donnees existantes...')
        ProcedureRollback.objects.all().delete()
        ProcedureCheck.objects.all().delete()
        ProcedureStep.objects.all().delete()
        ProcedureVariable.objects.all().delete()
        Procedure.objects.all().delete()
        ProcedureCategory.objects.all().delete()

        self.stdout.write('Creation des categories...')
        cat_map = {}
        for cat_data in CATEGORIES:
            cat = ProcedureCategory.objects.create(**cat_data)
            cat_map[cat_data['slug']] = cat
            self.stdout.write(f'  [OK] {cat.name}')

        self.stdout.write('Creation des procedures...')
        for pdata in PROCEDURES_DATA:
            variables = pdata.pop('variables', [])
            steps     = pdata.pop('steps', [])
            checks    = pdata.pop('checks', [])
            rollback  = pdata.pop('rollback', None)

            cat_slug = pdata.pop('category', None)
            pdata['category'] = cat_map.get(cat_slug)
            pdata['slug'] = slugify(pdata['title'])

            proc = Procedure.objects.create(**pdata)

            for v in variables:
                ProcedureVariable.objects.create(procedure=proc, **v)

            for s in steps:
                ProcedureStep.objects.create(procedure=proc, **s)

            for c in checks:
                ProcedureCheck.objects.create(procedure=proc, **c)

            if rollback:
                ProcedureRollback.objects.create(procedure=proc, **rollback)

            self.stdout.write(f'  [OK] {proc.title}')

        total = Procedure.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'\nSeed termine -- {total} procedures creees avec succes.'
        ))
