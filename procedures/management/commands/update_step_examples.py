"""
Commande de mise a jour : python manage.py update_step_examples
Met a jour le champ real_world_example des etapes existantes en base.
N'ecrase pas les exemples deja renseignes (protection idempotente).
"""
from django.core.management.base import BaseCommand
from procedures.models import Procedure, ProcedureStep

# Dictionnaire : { slug_procedure: { step_number: exemple } }
EXAMPLES = {

    # ── 1. Creer un VLAN ──────────────────────────────────────────────────────
    'creer-un-vlan-sur-switch-cisco': {
        2: ('Exemple : tu crees le VLAN 20 pour tous les PCs du service Comptabilite. '
            'Tu le nommes VLAN_COMPTA pour que tout le monde comprenne a quoi il '
            'correspond. Sans ce VLAN, les PCs de Compta seraient melanges avec les '
            'autres services sur le meme reseau.'),
        3: ('Exemple : Marie travaille en Comptabilite et son PC est branche sur le '
            'port Gi0/5 du switch. En mettant ce port dans le VLAN 20 (VLAN_COMPTA), '
            'le PC de Marie rejoint automatiquement le reseau Comptabilite. Elle peut '
            'acceder aux serveurs de Compta, mais pas au reseau IT ni au reseau RH.'),
    },

    # ── 2. Configurer un trunk ────────────────────────────────────────────────
    'configurer-un-lien-trunk-8021q': {
        1: ('Exemple : tu relies le switch de l\'etage 1 au switch de la salle reseau '
            'via le port Gi0/24. Ce lien trunk fait passer tous les VLANs (IT, Compta, '
            'VoIP) en meme temps sur un seul cable. Sans trunk, il faudrait un cable '
            'dedie par VLAN — beaucoup moins pratique.'),
        2: ('Exemple : tu autorises uniquement les VLANs 10, 20 et 30 sur ce trunk. '
            'Si quelqu\'un cree un VLAN 99 par accident, il ne passera pas '
            'automatiquement sur ce lien — c\'est une bonne pratique de securite. '
            'Le VLAN 99 est choisi comme VLAN natif car il est dedie au management '
            'et non utilise par les utilisateurs.'),
    },

    # ── 3. Inter-VLAN L3 (SVI) ───────────────────────────────────────────────
    'configurer-linter-vlan-sur-switch-l3-svi': {
        1: ('Exemple : sans cette commande, le switch 3750 sait deplacer les trames '
            'entre ses ports (commutation), mais il ne sait pas faire circuler des '
            'paquets entre le VLAN 10 (192.168.10.0/24) et le VLAN 20 '
            '(192.168.20.0/24). C\'est comme activer le moteur d\'une voiture avant '
            'de pouvoir conduire.'),
        2: ('Exemple : tu crees la SVI du VLAN 10 avec l\'IP 192.168.10.1. Tous les '
            'PCs du VLAN 10 doivent configurer 192.168.10.1 comme passerelle par '
            'defaut. Quand un PC du VLAN 10 veut parler a un PC du VLAN 20, il envoie '
            'le paquet a cette IP, et c\'est le switch L3 qui se charge de '
            'l\'acheminer vers le bon VLAN.'),
    },

    # ── 4. Route statique ─────────────────────────────────────────────────────
    'configurer-une-route-statique-cisco': {
        1: ('Exemple : ton routeur de bureau ne connait pas le reseau du siege '
            '(10.10.0.0/24). Tu lui indiques manuellement : "Pour atteindre '
            '10.10.0.0/24, envoie les paquets vers 192.168.1.254" (le routeur WAN). '
            'C\'est comme donner une adresse a un livreur qui ne connait pas le '
            'chemin — tu lui dis exactement par ou passer.'),
    },

    # ── 5. ACL Standard ──────────────────────────────────────────────────────
    'creer-une-acl-standard-cisco': {
        1: ('Exemple : tu veux empecher le reseau des stagiaires (192.168.100.0/24) '
            'd\'acceder au reseau des serveurs. Tu crees l\'ACL BLOCK_STAGIAIRES avec '
            'une regle "deny 192.168.100.0 0.0.0.255". Le "permit any" en dessous '
            'permet au reste du trafic de passer normalement. Sans ce "permit any", '
            'personne ne pourrait plus rien faire.'),
        2: ('Exemple : tu appliques l\'ACL BLOCK_STAGIAIRES en "in" sur l\'interface '
            'Gi0/1 (le port connecte au switch des stagiaires). Ainsi, tout trafic '
            'venant du reseau stagiaires et entrant sur Gi0/1 est filtre des son '
            'arrivee sur le routeur — avant meme d\'aller plus loin dans le reseau.'),
    },

    # ── 6. NAT Overload (PAT) ─────────────────────────────────────────────────
    'configurer-nat-overload-pat-cisco': {
        1: ('Exemple : dans une PME, le reseau interne est 192.168.1.0/24. Cette ACL '
            'dit au routeur : "Tous les PCs de ce reseau ont le droit d\'aller sur '
            'Internet via NAT." Si tu ne mets pas un PC dans cette ACL, il ne pourra '
            'pas sortir sur Internet, meme s\'il est correctement configure.'),
        2: ('Exemple : 50 PCs dans le bureau partagent une seule IP publique '
            '(ex: 90.200.1.10 fournie par le FAI). Quand le PC de Paul '
            '(192.168.1.5) ouvre YouTube, le routeur traduit : '
            '"192.168.1.5:50234 devient 90.200.1.10:50234". Quand la reponse revient, '
            'le routeur sait la renvoyer a Paul grace au numero de port. '
            'C\'est ca le NAT overload.'),
        3: ('Exemple : Gi0/1 est branche au switch LAN (reseau interne) -> '
            '"ip nat inside". Gi0/0 est branche au modem FAI (Internet) -> '
            '"ip nat outside". Si tu inverses les deux, le NAT ne fonctionnera pas '
            '— le routeur chercherait a natter le trafic dans le mauvais sens.'),
    },

    # ── 7. OSPF ───────────────────────────────────────────────────────────────
    'configurer-ospf-area-0-sur-routeur-cisco': {
        1: ('Exemple : tu as 3 routeurs dans ton reseau d\'entreprise. Chacun a un '
            'Router-ID unique : R1=1.1.1.1, R2=2.2.2.2, R3=3.3.3.3. Ces IDs sont '
            'comme des cartes d\'identite. OSPF les utilise pour savoir qui est qui '
            'lors des echanges. Si deux routeurs avaient le meme Router-ID, OSPF '
            'serait completement perdu.'),
        2: ('Exemple : tu annonces le reseau 192.168.10.0 avec le wildcard 0.0.0.255. '
            'Cela signifie : "OSPF, prends en charge toutes les interfaces dont l\'IP '
            'est dans 192.168.10.X". Le wildcard 0.0.0.255 est l\'inverse du masque '
            '/24 (255.255.255.0). Tous les routeurs OSPF du domaine vont apprendre '
            'ce reseau automatiquement.'),
        3: ('Exemple : l\'interface Gi0/1 est branchee aux PCs des employes. Ces PCs '
            'n\'ont pas besoin de recevoir les messages OSPF (hellos). En mettant '
            'Gi0/1 en "passive-interface", le routeur continue d\'annoncer le reseau '
            'dans OSPF, mais n\'envoie plus de hellos vers les PCs. C\'est une bonne '
            'pratique de securite et ca reduit le trafic inutile.'),
    },

    # ── 11. Config de base routeur ────────────────────────────────────────────
    'configuration-de-base-dun-routeur-cisco': {
        1: ('Exemple : tu recois un nouveau routeur Cisco 2911 pour la filiale de Lyon. '
            'Des la premiere connexion console, tu tapes "hostname R-LYON" — le prompt '
            'passe immediatement a R-LYON(config)#. Tu ajoutes "enable secret" pour '
            'bloquer l\'acces privilege. "no ip domain-lookup" t\'evite d\'attendre '
            '30 secondes chaque fois que tu tapes une mauvaise commande par accident.'),
        2: ('Exemple : la ligne console est physiquement accessible en salle serveur. '
            'Sans mot de passe, n\'importe quel technicien de passage pourrait entrer '
            'en mode configure. "exec-timeout 10 0" ferme la session apres 10 min '
            'd\'inactivite — si tu oublies de te deconnecter en quittant la salle. '
            'Sur VTY, "transport input ssh telnet" accepte les connexions SSH (chiffrees) '
            'et Telnet (pour les vieux outils de monitoring) depuis le reseau.'),
        3: ('Exemple : Gi0/0 est branche au modem de l\'operateur (lien 10 Mb/s). '
            'Tu lui donnes l\'IP publique 203.0.113.1/30 fournie par le FAI. '
            'Sans "no shutdown", l\'interface reste down et rien ne passe — '
            'c\'est une erreur classique de debutant qui fait appeler le support FAI '
            'alors que le probleme vient juste de la configuration locale.'),
    },

    # ── 12. Config de base switch ─────────────────────────────────────────────
    'configuration-de-base-dun-switch-cisco': {
        1: ('Exemple : tu deploies un Catalyst 2960 dans la salle reseau du batiment B. '
            'Tu le nommes SW-BATB-01 pour le distinguer des autres switches. '
            '"service password-encryption" chiffre le mot de passe dans la config — '
            'si quelqu\'un lit le fichier de config sauvegarde, il ne voit pas le '
            'mot de passe en clair. "no ip domain-lookup" evite les recherches DNS '
            'inutiles qui gelent le terminal.'),
        2: ('Exemple : tu crees le VLAN 99 dedie uniquement a la gestion du switch. '
            'Personne ne branche ses PCs sur ce VLAN — c\'est reserve aux admins. '
            'Tu lui donnes l\'IP 192.168.99.10/24. La "ip default-gateway 192.168.99.1" '
            'permet aux admins depuis un autre batiment de joindre le switch via SSH. '
            'Sans cette commande, le switch est joignable uniquement depuis le VLAN 99 local.'),
        3: ('Exemple : avant ce projet, les techniciens se connectaient au switch via Telnet — '
            'les mots de passe passaient en clair sur le reseau. Un audit de securite l\'a '
            'signale. Tu actives SSH v2 avec une cle RSA 2048 bits : maintenant la session '
            'est chiffree. "transport input ssh" sur les VTY bloque Telnet completement '
            '— plus de risque d\'ecoute passive.'),
    },

    # ── 13. EIGRP ─────────────────────────────────────────────────────────────
    'configurer-eigrp-sur-routeur-cisco': {
        1: ('Exemple : tu as 3 routeurs (R1, R2, R3) dans ton reseau AS 100. '
            'Tu definis Router-ID 1.1.1.1 sur R1 — une IP de loopback stable. '
            'Si tu n\'as pas de loopback et que l\'interface avec la plus haute IP '
            'tombe, EIGRP peut changer de Router-ID en plein fonctionnement et '
            'perturber les adjacences. "no auto-summary" evite qu\'EIGRP agregee '
            'automatiquement les routes en classes (comportement dangereux en IOS < 15).'),
        2: ('Exemple : R1 a deux interfaces — Gi0/0 vers R2 (10.0.0.0/30) et '
            'Gi0/1 vers le reseau LAN (192.168.1.0/24). Tu annonces les deux avec '
            '"network". EIGRP envoie alors des Hellos sur ces deux interfaces. '
            'R2 recoit l\'annonce du reseau 192.168.1.0/24 et peut router vers lui. '
            'Sans cette commande "network", R2 ne saurait pas que ce reseau existe.'),
        3: ('Exemple : Gi0/1 est branchee aux PCs des employes. Ces PCs ne font pas '
            'tourner EIGRP — envoyer des Hellos vers eux est inutile et consomme de '
            'la bande passante. En mettant Gi0/1 en passive-interface, R1 continue '
            'd\'annoncer 192.168.1.0/24 dans EIGRP, mais n\'envoie plus de Hellos. '
            'Un attaquant sur ce reseau ne pourrait pas non plus forger des Hellos '
            'pour injecter de fausses routes.'),
    },

    # ── 14. Port Security ─────────────────────────────────────────────────────
    'configurer-port-security-sur-switch-cisco': {
        1: ('Exemple : Fa0/3 est le port ou est branche le PC de la reception. '
            'Tu actives port-security dessus. "switchport nonegotiate" desactive DTP '
            'pour empecher quelqu\'un de connecter un switch non autorise et de creer '
            'un trunk a la place. Maintenant, le port n\'acceptera que les MACs que '
            'tu autorises — fini le "je branche mon PC perso sur le port de la reception".'),
        2: ('Exemple : tu mets maximum 2 MACs pour le port de la reception — '
            'le PC fixe + un telephone IP. "mac-address sticky" apprend '
            'automatiquement les MACs deja connectees et les ecrit dans la config. '
            'Apres un "copy run start", ces MACs sont sauvegardees. Si quelqu\'un '
            'debranche le PC de reception pour brancher son portable, sa MAC est '
            'differente — violation declenchee.'),
        3: ('Exemple : tu choisis le mode "restrict" plutot que "shutdown". '
            'Pourquoi ? En mode shutdown, le port passe en err-disabled et l\'employe '
            'de la reception n\'a plus de reseau — il appelle le support. '
            'En mode restrict, le trafic de la MAC inconnue est juste droppe '
            'et un log est genere dans Syslog. Tu es alerté sans couper le service. '
            'Le mode shutdown est preferable en zones tres sensibles (salle serveur).'),
    },

    # ── 15. EtherChannel L2 (LACP) ───────────────────────────────────────────
    'configurer-un-etherchannel-l2-lacp': {
        1: ('Exemple : entre le switch de distribution (SW-DIST) et le switch '
            'd\'acces du plateau (SW-ACC), un seul lien de 1 Gb/s saturait aux '
            'heures de pointe. Tu crees Port-Channel 1 en trunk avec les VLANs 10, 20, 30, 99. '
            'L\'ordre est important : configurer le Port-Channel AVANT les membres '
            'physiques. Si tu fais l\'inverse, les membres heritent de parametres '
            'par defaut incompatibles et le channel ne monte pas.'),
        2: ('Exemple : Gi0/1 et Gi0/2 de SW-DIST sont branches a Gi0/1 et Gi0/2 de SW-ACC. '
            '"channel-group 1 mode active" sur les deux interfaces : SW-DIST envoie '
            'des PDUs LACP pour negocier le bundle. SW-ACC repond. Resultat : '
            'Port-Channel 1 monte avec 2 Gb/s de bande passante effective. '
            'Si Gi0/1 tombe, le trafic bascule automatiquement sur Gi0/2 '
            'sans coupure visible pour les utilisateurs.'),
    },

    # ── ACL Etendue ───────────────────────────────────────────────────────────
    'configurer-une-acl-etendue-cisco': {
        1: ('Exemple : tu veux autoriser uniquement le HTTPS (port 443) depuis le '
            'reseau des employes (192.168.1.0/24) vers les serveurs en DMZ '
            '(10.10.10.0/24). Avec une ACL standard, tu ne pourrais filtrer que par '
            'IP source. Avec l\'ACL etendue, tu peux dire exactement : "IP source '
            '192.168.1.X, destination 10.10.10.X, protocole TCP, port 443 seulement" '
            '— tout le reste est bloque.'),
        2: ('Exemple : tu appliques l\'ACL en "in" sur Gi0/0 (l\'interface connectee '
            'au reseau des employes). Cela filtre le trafic DES SON ENTREE sur le '
            'routeur, avant qu\'il aille plus loin. Si tu l\'appliquais en "out" sur '
            'l\'interface vers la DMZ, le routeur traiterait d\'abord le paquet, puis '
            'verifierait s\'il peut sortir. Regle ACL etendue : placer au plus pres '
            'de la source, donc en "in".'),
    },

    # ── 16. Router-on-a-Stick ────────────────────────────────────────────────
    'configurer-le-router-on-a-stick-roas': {
        1: ('Exemple : ton routeur 1841 est relie au switch via un seul cable sur Gi0/0. '
            'Tu laisses Gi0/0 sans adresse IP — les IPs sont sur les sous-interfaces. '
            'C\'est comme une autoroute a plusieurs voies sur un seul tuyau physique : '
            'chaque sous-interface est une voie avec sa propre signalisation (tag VLAN). '
            'Si tu oublies "no shutdown" sur Gi0/0, toutes les sous-interfaces restent down '
            'meme si elles sont bien configurees.'),
        2: ('Exemple : tu crees Gi0/0.10 pour le VLAN 10 (reseau RH, 192.168.10.0/24). '
            '"encapsulation dot1Q 10" dit au routeur : "ce trafic porte le tag VLAN 10". '
            'L\'IP 192.168.10.1 devient la passerelle de tous les PCs RH. '
            'La convention est d\'utiliser le meme numero que le VLAN dans le nom '
            'de la sous-interface (Gi0/0.10 pour VLAN 10) — pas obligatoire '
            'mais indispensable pour s\'y retrouver.'),
        3: ('Exemple : tu crees Gi0/0.20 pour le VLAN 20 (reseau IT, 192.168.20.0/24). '
            'Les PCs IT ont 192.168.20.1 comme passerelle. Quand un PC RH '
            '(192.168.10.x) veut joindre un PC IT (192.168.20.x), le trafic '
            'remonte via le trunk jusqu\'au routeur, qui route de Gi0/0.10 vers '
            'Gi0/0.20, puis redescend au switch vers le PC IT. '
            'Tout ca sur un seul cable physique.'),
    },

    # ── 17. DHCP Server ───────────────────────────────────────────────────────
    'configurer-un-serveur-dhcp-sur-routeur-cisco': {
        1: ('Exemple : ton reseau LAN est 192.168.1.0/24. Tu as : '
            '192.168.1.1 (routeur), 192.168.1.2 (switch de gestion), '
            '192.168.1.3-10 (serveurs avec IP fixes), 192.168.1.20 (imprimante). '
            'Tu exclus 192.168.1.1 a 192.168.1.20. '
            'Sinon le routeur pourrait donner 192.168.1.3 a un PC, '
            'ce qui crerait un conflit IP avec ton serveur — conflit invisible '
            'jusqu\'a ce que des connexions commencent a tomber aleatoirement.'),
        2: ('Exemple : le pool LAN-POOL distribue les IPs de 192.168.1.21 '
            'a 192.168.1.254 (les autres etant exclues). Chaque PC recoit : '
            'IP automatique + masque 255.255.255.0 + passerelle 192.168.1.1 '
            '+ DNS 8.8.8.8 + domain netops.local. '
            'Avec lease 7 jours, un PC qui ne se reconnecte pas pendant une semaine '
            'libere son IP. Pratique pour les visiteurs en Wi-Fi '
            '(lease court) vs postes fixes (lease long pour stabilite).'),
    },

    # ── 18. VTP ───────────────────────────────────────────────────────────────
    'configurer-vtp-sur-un-domaine-de-switches-cisco': {
        1: ('Exemple : tu as 8 switches dans ton entreprise. Sans VTP, si tu crées le '
            'VLAN 50 (comptabilite), tu dois le configurer manuellement sur les 8 switches. '
            'Avec VTP, tu le crees une seule fois sur le switch serveur (SW-DIST-01) '
            'et il se propage automatiquement sur les 7 clients. '
            'Le domaine "NETOPS-DOMAIN" est comme un nom de groupe — seuls les switches '
            'avec ce nom exact synchronisent leurs VLANs. Le mot de passe empeche '
            'un switch pirate d\'ecraser ta base VLAN.'),
        2: ('Exemple : SW-DIST-01 est en mode "server" — il peut creer, modifier, '
            'supprimer des VLANs. SW-ACC-01 a SW-ACC-07 sont en mode "client" — '
            'ils recoivent et appliquent les changements du serveur mais ne peuvent '
            'pas creer de VLAN localement. Attention : si tu connectes un ancien switch '
            'reconfigure avec un revision number de 45 alors que ton serveur est a 12, '
            'le switch avec 45 ECRASE toute ta base VLAN. '
            'Toujours verifier "show vtp status" avant de connecter un switch inconnu.'),
    },

    # ── 19. Spanning Tree / Root Bridge ───────────────────────────────────────
    'configurer-spanning-tree-stp-et-le-root-bridge': {
        1: ('Exemple : tu as 3 switches : SW-DIST (distribution), SW-ACC-1 et SW-ACC-2 '
            '(acces). Par defaut, STP elu le Root Bridge en comparant les Bridge IDs '
            '(priorite + MAC). Si SW-ACC-1 a la plus petite MAC, il devient Root '
            '— catastrophique car tout le trafic passe par un switch d\'acces ! '
            '"spanning-tree vlan 10,20,30 root primary" force SW-DIST a devenir Root '
            'en abaissant sa priorite a 24576. Rapid PVST+ converge en moins de 2 s '
            'au lieu de 30-50 s pour STP classique.'),
        2: ('Exemple : Fa0/1 est branche au PC de l\'accueil. Sans PortFast, le port '
            'passe par Listening (15s) + Learning (15s) avant de forward — '
            'l\'employe attend 30 secondes apres avoir branche son PC. '
            'Avec PortFast, le port est en Forwarding immediatement. '
            'BPDU Guard protege ce port : si quelqu\'un branche un petit switch '
            'non autorise a la reception, le port passe en err-disabled '
            'des reception d\'un BPDU — protection contre les boucles STP.'),
    },

    # ── 20. OSPFv3 (IPv6) ────────────────────────────────────────────────────
    'configurer-ospfv3-pour-ipv6-sur-routeur-cisco': {
        1: ('Exemple : tu migres ton reseau en dual-stack (IPv4 + IPv6). '
            'OSPFv2 gere deja tes routes IPv4. Tu demarre OSPFv3 process 1 '
            'avec Router-ID 1.1.1.1 (une adresse IPv4 de loopback). '
            'Pourquoi un Router-ID au format IPv4 pour un protocole IPv6 ? '
            'C\'est l\'heritage d\'OSPF — le Router-ID est toujours 32 bits. '
            'Sans Router-ID explicite et si le routeur n\'a aucune IPv4, '
            'OSPFv3 refuse de demarrer.'),
        2: ('Exemple : Gi0/0 est connectee a R2 (lien WAN IPv6 2001:db8:1::/64). '
            'Gi0/1 est connectee aux PCs (LAN 2001:db8:2::/64). '
            'Tu actives OSPFv3 area 0 sur les deux interfaces. '
            'R2 recoit un Hello sur son Gi0/0 depuis l\'adresse link-local de R1 '
            '(FE80::1) — pas depuis l\'adresse globale. '
            'C\'est la grande difference avec OSPFv2 : les adjacences OSPFv3 '
            'utilisent toujours les link-local.'),
        3: ('Exemple : Gi0/1 est le port LAN avec les PCs. Ces PCs ne font pas tourner '
            'OSPFv3, donc envoyer des Hellos vers eux est du gaspillage. '
            'En passive-interface, OSPFv3 annonce le prefixe 2001:db8:2::/64 '
            'a ses voisins WAN, mais n\'envoie aucun Hello sur le LAN. '
            'Un attaquant sur ce LAN ne peut pas non plus forger '
            'un paquet Hello pour perturber le routage.'),
    },

    # ── DHCP Snooping ─────────────────────────────────────────────────────────
    'configurer-dhcp-snooping-sur-switch-cisco': {
        1: ('Exemple : un etudiant branche son Raspberry Pi sur le reseau de '
            'l\'entreprise et lance un faux serveur DHCP dessus. Sans DHCP Snooping, '
            'les autres PCs pourraient obtenir une fausse passerelle de cet etudiant '
            'et tout leur trafic passerait par son Pi (attaque Man-in-the-Middle). '
            'Avec DHCP Snooping actif, le switch bloque automatiquement les reponses '
            'DHCP venant de ports non autorises.'),
        2: ('Exemple : Gi0/1 est le port qui monte vers le switch de distribution '
            '(et donc vers le vrai serveur DHCP) — c\'est lui qui doit etre "trust". '
            'Fa0/5 est le port d\'un PC employe — il reste "untrusted". Si l\'employe '
            'essaie d\'envoyer une reponse DHCP depuis son PC, le switch la bloque. '
            'Le rate-limit a 15 paquets/s empeche aussi une attaque DHCP starvation '
            '(flooding de requetes pour epuiser le pool d\'adresses).'),
    },

    # ── Complements etapes non-triviales ────────────────────────────────────

    # Config routeur base — etapes restantes
    'configuration-de-base-dun-routeur-cisco': {
        1: ('Exemple : tu recois un nouveau routeur Cisco 2911 pour la filiale de Lyon. '
            'Des la premiere connexion console, tu tapes "hostname R-LYON" — le prompt '
            'passe immediatement a R-LYON(config)#. Tu ajoutes "enable secret" pour '
            'bloquer l\'acces privilege. "no ip domain-lookup" t\'evite d\'attendre '
            '30 secondes chaque fois que tu tapes une mauvaise commande par accident.'),
        2: ('Exemple : la ligne console est physiquement accessible en salle serveur. '
            'Sans mot de passe, n\'importe quel technicien de passage pourrait entrer '
            'en mode configure. "exec-timeout 10 0" ferme la session apres 10 min '
            'd\'inactivite — si tu oublies de te deconnecter en quittant la salle. '
            'Sur VTY, "transport input ssh telnet" accepte les connexions SSH (chiffrees) '
            'et Telnet (pour les vieux outils de monitoring) depuis le reseau.'),
        3: ('Exemple : Gi0/0 est branche au modem de l\'operateur (lien 10 Mb/s). '
            'Tu lui donnes l\'IP publique 203.0.113.1/30 fournie par le FAI. '
            'Sans "no shutdown", l\'interface reste down et rien ne passe — '
            'c\'est une erreur classique de debutant qui fait appeler le support FAI '
            'alors que le probleme vient juste de la configuration locale.'),
        4: ('Exemple : Gi0/1 est l\'interface qui distribue le reseau local '
            'de la filiale (192.168.1.0/24). Tous les PCs utilisent '
            '192.168.1.1 comme passerelle par defaut. '
            'La description "LAN-LOCAL" te permet, en lisant la config, '
            'de savoir immediatement a quoi sert cette interface '
            'sans avoir a consulter le plan reseau.'),
        5: ('Exemple : la banniere MOTD "Acces reserve au personnel autorise" '
            'apparait a CHAQUE connexion, avant meme la demande de mot de passe. '
            'Elle a une valeur legale : en cas d\'intrusion, elle prouve '
            'que l\'acces non autorise etait clairement indique. '
            'Sans banniere, un avocat pourrait arguer que l\'acces '
            'n\'etait pas explicitement interdit.'),
    },

    # Config switch base — etapes restantes
    'configuration-de-base-dun-switch-cisco': {
        1: ('Exemple : tu deploies un Catalyst 2960 dans la salle reseau du batiment B. '
            'Tu le nommes SW-BATB-01 pour le distinguer des autres switches. '
            '"service password-encryption" chiffre le mot de passe dans la config — '
            'si quelqu\'un lit le fichier de config sauvegarde, il ne voit pas le '
            'mot de passe en clair. "no ip domain-lookup" evite les recherches DNS '
            'inutiles qui gelent le terminal.'),
        2: ('Exemple : tu crees le VLAN 99 dedie uniquement a la gestion du switch. '
            'Personne ne branche ses PCs sur ce VLAN — c\'est reserve aux admins. '
            'Tu lui donnes l\'IP 192.168.99.10/24. La "ip default-gateway 192.168.99.1" '
            'permet aux admins depuis un autre batiment de joindre le switch via SSH. '
            'Sans cette commande, le switch est joignable uniquement depuis le VLAN 99 local.'),
        3: ('Exemple : avant ce projet, les techniciens se connectaient au switch via Telnet — '
            'les mots de passe passaient en clair sur le reseau. Un audit de securite l\'a '
            'signale. Tu actives SSH v2 avec une cle RSA 2048 bits : maintenant la session '
            'est chiffree. "transport input ssh" sur les VTY bloque Telnet completement '
            '— plus de risque d\'ecoute passive.'),
        4: ('Exemple : "logging synchronous" evite que les messages de log '
            'du switch interrompent la ligne que tu es en train de taper '
            '— tres utile pendant le deploiement. '
            '"exec-timeout 10 0" ferme la session console apres 10 min d\'inactivite. '
            'Si tu laisses la console connectee sans surveillance, '
            'n\'importe qui avec un acces physique a la salle peut '
            'entrer en mode privilege sans mot de passe.'),
    },

    # Inter-VLAN SVI — etape 3 (verifier + sauvegarder)
    'configurer-linter-vlan-sur-switch-l3-svi': {
        1: ('Exemple : sans cette commande, le switch 3750 sait deplacer les trames '
            'entre ses ports (commutation), mais il ne sait pas faire circuler des '
            'paquets entre le VLAN 10 (192.168.10.0/24) et le VLAN 20 '
            '(192.168.20.0/24). C\'est comme activer le moteur d\'une voiture avant '
            'de pouvoir conduire.'),
        2: ('Exemple : tu crees la SVI du VLAN 10 avec l\'IP 192.168.10.1. Tous les '
            'PCs du VLAN 10 doivent configurer 192.168.10.1 comme passerelle par '
            'defaut. Quand un PC du VLAN 10 veut parler a un PC du VLAN 20, il envoie '
            'le paquet a cette IP, et c\'est le switch L3 qui se charge de '
            'l\'acheminer vers le bon VLAN.'),
        3: ('Exemple : "show ip route" doit afficher deux routes "C" (connected) : '
            '"C 192.168.10.0/24 via Vlan10" et "C 192.168.20.0/24 via Vlan20". '
            'Si une SVI n\'est pas dans la table, c\'est qu\'elle est down — '
            'verifier que le VLAN existe et qu\'au moins un port est actif dans ce VLAN. '
            'Un ping depuis le switch vers 192.168.10.1 et 192.168.20.1 '
            'confirme que les deux passerelles sont operationnelles.'),
    },

    # Route statique — etape 2 (verifier + sauvegarder)
    'configurer-une-route-statique-cisco': {
        1: ('Exemple : ton routeur de bureau ne connait pas le reseau du siege '
            '(10.10.0.0/24). Tu lui indiques manuellement : "Pour atteindre '
            '10.10.0.0/24, envoie les paquets vers 192.168.1.254" (le routeur WAN). '
            'C\'est comme donner une adresse a un livreur qui ne connait pas le '
            'chemin — tu lui dis exactement par ou passer.'),
        2: ('Exemple : "show ip route 10.10.0.0" doit afficher '
            '"S 10.10.0.0/24 [1/0] via 192.168.1.254". '
            'Le "S" confirme que c\'est une route statique (Static). '
            'Un ping vers 10.10.0.1 (une IP du siege) depuis le routeur '
            'valide que le chemin fonctionne. '
            '"copy running-config startup-config" sauvegarde la route — '
            'sinon elle disparait apres un reboot.'),
    },

    # VLAN — etape 1 (mode config global)
    'creer-un-vlan-sur-switch-cisco': {
        1: ('Exemple : tu es connecte au switch via SSH. '
            'Le prompt affiche SW1>. Pour creer un VLAN tu dois etre '
            'en mode configuration globale. "enable" te donne le privilege 15 '
            '(SW1#), puis "configure terminal" te place en SW1(config)# — '
            'c\'est de la que toutes les configurations permanentes sont faites. '
            'Toute commande tapee en mode privilege (show, ping) '
            'n\'est pas sauvegardee dans la config.'),
        2: ('Exemple : tu crees le VLAN 20 pour tous les PCs du service Comptabilite. '
            'Tu le nommes VLAN_COMPTA pour que tout le monde comprenne a quoi il '
            'correspond. Sans ce VLAN, les PCs de Compta seraient melanges avec les '
            'autres services sur le meme reseau.'),
        3: ('Exemple : Marie travaille en Comptabilite et son PC est branche sur le '
            'port Gi0/5 du switch. En mettant ce port dans le VLAN 20 (VLAN_COMPTA), '
            'le PC de Marie rejoint automatiquement le reseau Comptabilite. Elle peut '
            'acceder aux serveurs de Compta, mais pas au reseau IT ni au reseau RH.'),
        4: ('Exemple : si tu ne sauvegardes pas avec "copy running-config startup-config", '
            'le VLAN 20 et l\'assignation du port Gi0/5 disparaissent '
            'au prochain reboot du switch. '
            'Sur les switches Cisco, la base VLAN (vlan.dat) est separee '
            'de la startup-config — les deux sont sauvegardes par cette commande. '
            'Verifier avec "show vlan brief" que le VLAN 20 est bien present.'),
    },

    # 31. BGP attributs (Local Pref + AS-Path Prepend) ────────────────────
    'configurer-les-attributs-bgp-local-preference-et-as-path-prepend': {
        1: ('Exemple : ton entreprise est connectee a deux FAI. '
            'FAI-A (fibre 1 Gbps) doit etre le chemin prefere en sortie. '
            'FAI-B (ADSL 100 Mbps) est le secours. '
            '"SET-LOCPREF-HIGH" met la Local Preference a 200 sur les routes de FAI-A '
            '— plus la valeur est haute, plus le chemin est prefere. '
            '"SET-LOCPREF-LOW" laisse FAI-B a 100 (valeur par defaut). '
            'Tous les routeurs iBGP de ton AS recevront ces preferences '
            'et utiliseront FAI-A automatiquement.'),
        2: ('Exemple : tu appliques SET-LOCPREF-HIGH en "in" sur FAI-A '
            '(203.0.113.1) et SET-LOCPREF-LOW en "in" sur FAI-B (203.0.113.5). '
            '"in" signifie : modifier les attributs des routes RECUES de ce voisin. '
            'Apres "clear ip bgp soft in", "show ip bgp" montre les routes de FAI-A '
            'avec LocPrf 200 et celles de FAI-B avec LocPrf 100. '
            'Ton routeur choisit toujours le chemin FAI-A — sauf s\'il tombe.'),
        3: ('Exemple : tu veux que le trafic ENTRANT (venant d\'Internet vers toi) '
            'prefere aussi FAI-A. Tu annoces ton prefixe 192.168.1.0/24 '
            'au FAI-B avec un AS-Path prepende 3 fois ton AS 65001. '
            'Les routeurs Internet voient "65001 65001 65001 65001" pour le chemin FAI-B '
            'contre "65001" pour FAI-A — ils preferent le chemin le plus court '
            'et envoient le trafic par FAI-A. Pratique sans changer les annonces BGP.'),
    },

    # ── 32. Interface IPv6 ────────────────────────────────────────────────────
    'configurer-une-interface-ipv6-sur-routeur-cisco': {
        1: ('Exemple : tu migres ton reseau en dual-stack. Ton routeur a deja '
            'des routes IPv4 via OSPF. Sans "ipv6 unicast-routing", '
            'tu peux configurer des adresses IPv6 sur les interfaces '
            'mais le routeur ne routera aucun paquet IPv6 entre elles '
            '— exactement comme un switch L2 avec des IPs. '
            'Cette seule commande active le moteur de routage IPv6 '
            'sur tout le routeur.'),
        2: ('Exemple : ton FAI te donne le prefixe 2001:db8:acad:1::1/64 '
            'pour ton lien WAN. Tu l\'assignes sur Gi0/0. '
            'En plus de cette adresse globale, le routeur genere automatiquement '
            'une adresse link-local FE80::x derivee de la MAC — '
            'cette adresse est utilisee par OSPF v3 pour les adjacences '
            'et par les protocoles NDP/RA. '
            '"show ipv6 interface brief" montre les deux adresses.'),
        3: ('Exemple : pour le LAN (Gi0/1), tu utilises EUI-64 '
            'avec le prefixe 2001:db8:acad:2::/64. '
            'EUI-64 prend la MAC de Gi0/1 (ex: 00:1A:2B:3C:4D:5E), '
            'l\'etend en inserant FF:FE au milieu et inverse le 7e bit : '
            'resultat 2001:db8:acad:2:021A:2BFF:FE3C:4D5E. '
            'Plus besoin de calculer l\'adresse manuellement — '
            'tres pratique sur les interfaces LAN avec de nombreux routeurs.'),
    },

    # ── 33. SNMPv2c ───────────────────────────────────────────────────────────
    'configurer-snmpv2c-sur-equipement-cisco': {
        1: ('Exemple : ton NMS (Network Management System) a l\'IP 192.168.99.100. '
            'L\'ACL ACL_SNMP_ACCESS n\'autorise que cette IP a interroger le routeur. '
            'Sans cette ACL, n\'importe qui sur le reseau connaissant '
            'la community string "public" pourrait lire toute la configuration '
            'de ton equipement via SNMP — version, interfaces, routes, '
            'utilisation CPU. C\'est une fuite d\'informations classique '
            'signalee dans les audits de securite.'),
        2: ('Exemple : "snmp-server community NETOPS-RO RO ACL_SNMP_ACCESS" '
            'cree une community en lecture seule (RO) liee a l\'ACL. '
            'Ton NMS (Nagios, PRTG, Zabbix) peut maintenant interroger '
            'le routeur avec la community "NETOPS-RO" pour surveiller '
            'les interfaces, la bande passante, le CPU, la memoire. '
            'Location et contact permettent a l\'equipe de savoir '
            'rapidement ou est physiquement l\'equipement sans ouvrir IPAM.'),
    },

    # ── 34. Diagnostiquer trunk 802.1Q ────────────────────────────────────────
    'diagnostiquer-un-trunk-8021q-down-ou-defaillant': {
        1: ('Exemple : les PCs du VLAN 20 (Marketing) ne peuvent plus joindre '
            'le serveur en salle reseau depuis ce matin. Tu commences par la base : '
            '"show interfaces Gi0/1 status" -> port en "notconnect" '
            'alors que le cable est branché. Probleme physique : '
            'mauvais cable, SFP defaillant, ou port desactive. '
            'Si le port est "connected" mais le trunk ne passe pas, '
            'le probleme est de configuration — on passe a l\'etape suivante.'),
        2: ('Exemple : "show interfaces trunk" ne montre pas Gi0/1 '
            'dans la liste des trunks actifs. "show interfaces Gi0/1 trunk" '
            'indique "not-trunking". Cote switch acces, le port est en mode '
            '"dynamic auto" et cote switch distribution aussi — '
            'DTP ne negocie pas car les deux attendent que l\'autre initie. '
            'Solution : forcer "switchport mode trunk" des deux cotes. '
            'Ou : l\'encapsulation est ISL d\'un cote et 802.1Q de l\'autre.'),
        3: ('Exemple : le trunk est up mais les PCs du VLAN 20 n\'ont pas d\'IP. '
            '"show logging | include native" montre : '
            '"Native VLAN mismatch discovered on Gi0/1 (1), with SW-ACC Gi0/2 (99)". '
            'Un cote est en VLAN natif 1, l\'autre en 99. '
            'CDP detecte automatiquement ce mismatch et le logue. '
            'Le trafic non tagge est mal classe — '
            'corriger en mettant le meme VLAN natif des deux cotes.'),
        4: ('Exemple : le trunk est bien configure mais Gi0/1 est en etat '
            '"BLK" (Blocking) pour le VLAN 20 dans "show spanning-tree vlan 20". '
            'STP a decide de bloquer ce port pour eviter une boucle L2. '
            'Normal si c\'est un lien redondant — le port alternatif est bien bloque. '
            'Anormal si c\'est le seul chemin : verifier si un switch en aval '
            'a une priorite STP plus basse que prevu et est devenu Root Bridge '
            'de maniere inattendue.'),
    },

    # ── 35. Diagnostiquer adjacence OSPF ─────────────────────────────────────
    'diagnostiquer-une-adjacence-ospf-manquante': {
        1: ('Exemple : tu ajoutes un nouveau routeur R4 dans le reseau OSPF '
            'mais "show ip ospf neighbor" ne montre aucun voisin. '
            'Ou il apparait avec l\'etat "INIT" ou "2WAY" sans jamais passer "FULL". '
            'INIT = R4 recoit des Hellos de son voisin mais le voisin '
            'n\'a pas encore recu les Hellos de R4. '
            '2WAY = les deux se voient mais ne forment pas d\'adjacence complete '
            '(normal sur un reseau multi-acces pour les non DR/BDR).'),
        2: ('Exemple : "ping 10.0.0.1 source Gi0/0" depuis R4 echoue. '
            'Probleme de connectivite L3 basique avant meme de parler OSPF. '
            'Causes possibles : mauvais masque sur une interface '
            '(10.0.0.1/24 vs 10.0.0.1/30 — pas le meme sous-reseau), '
            'interface en shutdown, ou ACL bloquant les paquets. '
            'OSPF utilise le multicast 224.0.0.5 pour les Hellos : '
            'verifier aussi qu\'aucune ACL ne bloque le multicast.'),
        3: ('Exemple : le ping fonctionne mais pas d\'adjacence. '
            '"show ip ospf interface Gi0/0" revele : '
            '"Hello 10, Dead 40" sur R4 vs "Hello 5, Dead 20" sur R3. '
            'Les hello/dead timers doivent etre identiques des deux cotes — '
            'OSPF refuse l\'adjacence si les timers different. '
            'Autre cause frequente : area differente (R4 en area 1 vs R3 en area 0). '
            'Ou "ip ospf authentication" sur un cote mais pas l\'autre.'),
        4: ('Exemple : tout semble correct mais l\'adjacence reste bloquee '
            'en "EXSTART" ou "EXCHANGE". Cause probable : MTU mismatch. '
            '"show interfaces Gi0/0 | include MTU" sur R4 affiche 1500 '
            'mais sur R3 : 1476 (lien PPPoE avec overhead). '
            'OSPF echange des DBD (Database Descriptor) qui depassent '
            'le MTU du voisin — les paquets sont fragmentes ou droppes. '
            'Solution : "ip ospf mtu-ignore" ou harmoniser les MTU.'),
    },

    # ── 26. Policy Based Routing ─────────────────────────────────────────────
    'configurer-le-policy-based-routing-pbr': {
        1: ('Exemple : tu as deux connexions Internet — FAI-A (fibre, 1 Gbps) '
            'et FAI-B (ADSL, 20 Mbps backup). Les commerciaux (192.168.10.0/24) '
            'doivent toujours passer par FAI-A pour la VoIP et les visioconferences. '
            'L\'ACL "TRAFIC-COMMERCIAUX" matche exactement ce reseau. '
            'Si tu ne definis pas l\'ACL correctement, le PBR s\'applique '
            'a plus de trafic que prevu — toujours tester avec "debug ip policy".'),
        2: ('Exemple : la route-map PBR-COMMERCIAUX sequence 10 dit : '
            '"si trafic matche TRAFIC-COMMERCIAUX, envoie vers FAI-A (203.0.113.2)". '
            '"verify-reachability" est cle : si FAI-A tombe, le routeur '
            'passe automatiquement au chemin de routage normal (FAI-B) '
            'au lieu de dropper le trafic. La sequence 20 sans "set" '
            'laisse tout le reste suivre la table de routage normale — '
            'sans elle, tout trafic non matche est drope silencieusement.'),
        3: ('Exemple : tu appliques la route-map sur Gi0/1 — l\'interface '
            'ou arrivent les paquets des commerciaux depuis leur switch. '
            'PBR s\'applique toujours en ENTREE (ingress) sur l\'interface '
            'source du trafic. Si tu l\'appliques sur la mauvaise interface '
            'ou en sortie, la policy ne s\'applique jamais. '
            '"show ip policy" confirme : "Gi0/1: PBR-COMMERCIAUX".'),
    },

    # ── 27. Routage inter-VLAN MLS ────────────────────────────────────────────
    'configurer-le-routage-inter-vlan-sur-switch-multicouche-mls': {
        1: ('Exemple : ton Catalyst 3750 a 4 VLANs et tu veux remplacer '
            'ton Router-on-a-Stick qui saturait. "ip routing" active la fonction '
            'de routage L3 integree. Sans cette commande, les SVIs que tu vas creer '
            'auront bien une adresse IP mais le switch les traitera comme des interfaces '
            'de gestion uniquement — aucun paquet ne sera route entre VLANs. '
            'C\'est l\'erreur la plus frequente sur les switches L3.'),
        2: ('Exemple : VLAN 10 (RH, 192.168.10.0/24) et VLAN 20 (IT, 192.168.20.0/24). '
            'Tu crees Vlan10 avec IP 192.168.10.1 et Vlan20 avec IP 192.168.20.1. '
            'Ces IPs deviennent les passerelles des PCs respectifs. '
            'La SVI Vlan10 ne passe "up" que si le VLAN 10 existe dans la base VLAN '
            'ET qu\'au moins un port de ce VLAN est en etat up/up. '
            'Si la SVI reste down, verifier avec "show vlan brief" et l\'etat des ports.'),
        3: ('Exemple : Gi0/1 monte vers le routeur edge (acces Internet). '
            '"no switchport" le transforme en port L3 pur — fini le monde switch, '
            'maintenant c\'est un lien point-a-point comme une interface routeur. '
            'L\'IP 10.0.0.2/30 est le lien entre le switch L3 et le routeur. '
            '"ip route 0.0.0.0 0.0.0.0 10.0.0.1" : tout le trafic inconnu '
            '(Internet) est envoye vers le routeur. Sans cette route par defaut, '
            'les PCs peuvent se parler entre VLANs mais pas sortir sur Internet.'),
    },

    # ── 28. STP avancé (Root Guard + Loop Guard) ─────────────────────────────
    'configurer-stp-avance-rstp-root-guard-et-loop-guard': {
        1: ('Exemple : un port en Root du switch de distribution SW-DIST recoit '
            'normalement des BPDUs de SW-CORE (le vrai Root Bridge). '
            'Si la fibre vers SW-CORE a une panne unidirectionnelle '
            '(le port recoit mais n\'envoie plus), le port arrete de recevoir des BPDUs '
            'mais reste en Forwarding — boucle L2 potentielle ! '
            '"spanning-tree loopguard default" surveille tous les ports '
            'root/alternate : si les BPDUs cessent, le port passe en '
            '"loop-inconsistent" (bloque) plutot qu\'en Forwarding.'),
        2: ('Exemple : Gi0/2 de SW-DIST est branché vers SW-ACC-01 (switch d\'acces). '
            'SW-ACC-01 a une priorite par defaut de 32768. '
            'Normalement SW-DIST est Root avec priorite 24576. '
            'Un admin branche accidentellement un switch de conference Gi0/2 '
            'avec priorite 0 — il deviendrait Root Bridge et reconfigurerait '
            'toute la topologie STP ! Root Guard bloque immediatement Gi0/2 '
            'en "root-inconsistent" des reception du BPDU superieur.'),
        3: ('Exemple : Gi0/1 est le port root de SW-DIST vers SW-CORE — '
            'il recoit des BPDUs de SW-CORE regulierement. '
            'En ajoutant "spanning-tree guard loop" explicitement '
            'en plus du defaut global, tu t\'assures que ce port critique '
            'est bien surveille meme si quelqu\'un desactive le defaut global. '
            'Root Guard et Loop Guard ne peuvent JAMAIS etre actifs '
            'sur le meme port — IOS refuse la combinaison.'),
    },

    # ── 29. EtherChannel L3 ───────────────────────────────────────────────────
    'configurer-un-etherchannel-l3-routed-port-channel': {
        1: ('Exemple : le lien entre SW-DIST-01 et SW-CORE est critique. '
            'Un seul lien de 1 Gbps ne suffit plus et STP bloque le second lien. '
            'Tu passes les deux interfaces en mode L3 avec "no switchport" — '
            'elles ne font plus partie du domaine STP. '
            '"channel-group 1 mode active" les regroupe via LACP : '
            'les deux liens s\'additionnent (2 Gbps) et si l\'un tombe, '
            'le trafic continue sur l\'autre sans interruption et sans STP.'),
        2: ('Exemple : l\'IP 10.0.0.1/30 est attribuee au Port-Channel 1 '
            '(pas aux interfaces physiques Gi1/0/1 et Gi1/0/2 — elles n\'ont pas d\'IP). '
            'Du cote de SW-CORE, Port-Channel 1 aura l\'IP 10.0.0.2/30. '
            '"show etherchannel summary" doit afficher "RU" (R = Layer3, U = in use). '
            'Si tu vois "SU" (S = Layer2), c\'est que "no switchport" '
            'n\'a pas ete applique sur les membres — a corriger.'),
    },

    # ── 30. Durcissement L2 ───────────────────────────────────────────────────
    'durcissement-securite-l2-bpdu-guard-storm-control-et-dai': {
        1: ('Exemple : un employe branche un petit switch Netgear personnel '
            'sous son bureau pour avoir plus de ports. Ce switch envoie des BPDUs. '
            'Sans BPDU Guard, Fa0/5 recoit un BPDU et STP se reconfigure — '
            'potentiellement boucle ou coupure. Avec BPDU Guard global, '
            'Fa0/5 passe en err-disabled immediatement. '
            '"errdisable recovery cause bpduguard" + interval 300 : '
            'apres 5 minutes, le port tente de revenir — si le switch pirate '
            'est toujours branche, il se rebloque automatiquement.'),
        2: ('Exemple : un PC infecte par un malware commence a envoyer '
            'des broadcasts en masse (attaque de type "broadcast storm"). '
            'Sans Storm Control, ce trafic inonde tout le VLAN et paralyse '
            'la commutation. Avec "storm-control broadcast level 20 10" : '
            'si les broadcasts depassent 20% de la bande passante du port, '
            'Storm Control coupe le port (action shutdown). '
            'Le seuil descend a 10% avant de le rouvrir — evite l\'effet on/off.'),
        3: ('Exemple : un attaquant lance un ARP poisoning : '
            'il envoie des ARP Reply faux disant "192.168.1.1 = MON-MAC" '
            'pour intercepter le trafic destine a la passerelle. '
            'DAI verifie chaque paquet ARP contre la table DHCP Snooping : '
            '"192.168.1.1 appartient-il bien a cette MAC et ce port ?" '
            'Si non, l\'ARP est drope. Le port "trusted" sur l\'uplink '
            'est obligatoire — sinon les ARP du routeur lui-meme sont bloques '
            'et tout le reseau perd la passerelle.'),
    },

    # ── 21. eBGP ─────────────────────────────────────────────────────────────
    'configurer-ebgp-entre-deux-as-cisco': {
        1: ('Exemple : ton entreprise (AS 65001) se connecte a son FAI (AS 65002) '
            'via un lien /30 : 203.0.113.1 cote toi, 203.0.113.2 cote FAI. '
            '"router bgp 65001" demarre le processus BGP de ton AS. '
            '"neighbor 203.0.113.2 remote-as 65002" dit a ton routeur qui est son '
            'interlocuteur. Le mot de passe MD5 BGP est negocie avec le FAI — '
            'sans lui, la session est refusee. La session passe par les etats '
            'Idle → Active → Connect → Established : ca peut prendre quelques secondes.'),
        2: ('Exemple : tu veux que le FAI achemine le trafic vers ton reseau '
            '192.168.1.0/24. "network 192.168.1.0 mask 255.255.255.0" dit a BGP '
            'd\'annoncer ce prefixe AU FAI. Attention : si la route 192.168.1.0/24 '
            'n\'existe pas dans ta table de routage locale (via OSPF ou en connected), '
            'BGP ne l\'annonce pas — c\'est une protection contre les annonces accidentelles. '
            'Le FAI recoit ton reseau et peut router le trafic Internet vers toi.'),
    },

    # ── 22. NTP ───────────────────────────────────────────────────────────────
    'configurer-ntp-sur-equipement-cisco': {
        1: ('Exemple : sans cette commande, les logs de ton routeur sont en UTC. '
            'Quand tu cherches un incident survenu a 14h heure de Paris, '
            'tu trouves des logs a 13h en hiver ou 12h en ete — perdre du temps '
            'en investigation. "clock timezone CET 1" + "clock summer-time CETDT recurring" '
            'alignent les logs sur l\'heure locale avec passage automatique '
            'heure d\'ete/hiver. Indispensable pour corréler les evenements entre equipements.'),
        2: ('Exemple : sans authentification NTP, n\'importe quel serveur peut '
            'envoyer de fausses mises a l\'heure a ton routeur — une attaque '
            'qui peut invalider les certificats PKI ou fausser les logs de securite. '
            'La cle MD5 "NTP$ecretKey" est partagee entre ton routeur et le serveur NTP. '
            'Seuls les serveurs qui connaissent cette cle sont acceptes. '
            'C\'est obligatoire en environnement PCI-DSS ou ISO 27001.'),
        3: ('Exemple : tu pointes vers deux serveurs NTP internes : '
            '192.168.1.100 (primaire, "prefer") et 192.168.1.101 (backup). '
            'Le routeur se synchronise sur le primaire. Si 192.168.1.100 devient '
            'injoignable, il bascule automatiquement sur 192.168.1.101. '
            'Attention : la premiere sync peut prendre 5 a 15 minutes. '
            '"show ntp status" affiche "unsynced" pendant cette periode — c\'est normal.'),
    },

    # ── 23. EIGRP avance ─────────────────────────────────────────────────────
    'configurer-eigrp-avance-summarisation-et-authentification': {
        1: ('Exemple : ton routeur R1 a 4 reseaux LAN : 192.168.0.0/24, 192.168.1.0/24, '
            '192.168.2.0/24 et 192.168.3.0/24. Au lieu d\'annoncer 4 routes a R2, '
            'tu peux les resumer en 192.168.0.0/22 — une seule route. '
            'La cle EIGRP-AUTH avec la valeur "E1GRP$ecret" sera utilisee pour signer '
            'chaque paquet EIGRP. Si quelqu\'un essaie d\'injecter de fausses routes EIGRP '
            'depuis le reseau, ses paquets seront rejetes car non signes.'),
        2: ('Exemple : sur Gi0/0 (lien vers R2), tu actives l\'auth MD5 '
            'et la summarisation 192.168.0.0/22. Quand R2 regarde sa table de routage, '
            'il ne voit plus 4 routes separees mais une seule route resumes. '
            'Sa table de routage est 4x plus petite pour cette partie du reseau. '
            'L\'adjacence peut brievement se couper le temps que R2 configure aussi '
            'le meme key-chain avec la meme cle — toujours coordonner les deux cotes.'),
    },

    # ── 24. OSPF avance ───────────────────────────────────────────────────────
    'configurer-ospf-avance-areas-cost-et-authentification': {
        1: ('Exemple : par defaut, Cisco calcule le cost OSPF = 100 Mbps / bande passante. '
            'Un lien Gi (1 Gbps) et un lien Fa (100 Mbps) ont TOUS LES DEUX un cost de 1 '
            '— impossible de distinguer le meilleur chemin ! '
            '"auto-cost reference-bandwidth 10000" (10 Gbps) donne : '
            'cost Gi = 10, cost 10G = 1 — ecart significatif. '
            '"area 1 stub" signifie que les routeurs de l\'area 1 ne recevront pas '
            'les LSA externes (E1/E2), remplacees par une route par defaut '
            '— parfait pour des sites distants qui ont juste besoin de sortir.'),
        2: ('Exemple : R-ABR est l\'Area Border Router entre area 0 (backbone) '
            'et area 1 (site distant). Tu annonces 10.1.1.0/24 dans area 1. '
            'Les routeurs de area 1 apprendront ce reseau. '
            'Les routeurs de area 0 apprendront aussi ce reseau via les LSA inter-area. '
            'Un reseau annonce dans la mauvaise area ne sera pas appris par les bons voisins '
            '— verifier toujours avec "show ip ospf database".'),
        3: ('Exemple : Gi0/1 est un lien de secours a 100 Mbps. Le lien principal '
            'Gi0/0 est a 1 Gbps. Avec reference-bandwidth 10000, cost de Gi0/0 = 10 '
            'et Gi0/1 = 100. Tu forces cost de Gi0/1 a 1000 pour que le trafic '
            'evite ce lien sauf urgence. Sur Gi0/0 (lien vers le voisin OSPF), '
            'l\'auth MD5 empeche l\'injection de fausses LSA — '
            'attaque reelle documentee dans les incidents de production.'),
    },

    # ── 25. Redistribution de routes ─────────────────────────────────────────
    'configurer-la-redistribution-de-routes-entre-protocoles': {
        1: ('Exemple : ta filiale utilise EIGRP, le WAN utilise OSPF. '
            'R-BORDER est le routeur frontiere qui parle les deux. '
            'Tu redistribues EIGRP dans OSPF avec "subnets" — ce mot-cle est '
            'OBLIGATOIRE. Sans lui, OSPF n\'accepte que les routes classful : '
            '192.168.1.0/24 passerait, mais 10.1.1.128/26 serait ignoree '
            'car c\'est un sous-reseau de classe A. Le tag 100 marque les routes '
            'redistribuees pour eviter qu\'elles soient redistribuees a nouveau '
            'en sens inverse — protection anti-boucle essentielle.'),
        2: ('Exemple : tu redistribues maintenant OSPF dans EIGRP. '
            'EIGRP a besoin de 5 parametres de metrique : bande passante (1000 kbps), '
            'delai (100 x 10 us), fiabilite (255 = 100%), charge (1), MTU (1500). '
            'Si tu oublies ces 5 valeurs, la commande est rejetee. '
            'Les routes OSPF apparaissent dans EIGRP avec le tag "D EX" '
            '(D = EIGRP, EX = externe). Les routeurs EIGRP de la filiale '
            'savent maintenant comment atteindre les reseaux WAN via le protocole OSPF '
            'sans avoir a faire tourner OSPF eux-memes.'),
    },

    # ── HSRP ──────────────────────────────────────────────────────────────────
    'configurer-hsrp-pour-la-haute-disponibilite': {
        1: ('Exemple : tous les PCs du bureau utilisent 192.168.1.254 comme '
            'passerelle. Avec HSRP, cette IP n\'appartient a aucun routeur physique '
            '— c\'est une IP virtuelle partagee. Le routeur R1 (priorite 110) est '
            'actif et repond pour cette IP. Les PCs ne savent pas qu\'il y a deux '
            'routeurs derriere. Ils font juste confiance a l\'adresse 192.168.1.254.'),
        2: ('Exemple : R1 (priorite 110) est actif mais sa connexion Internet (Gi0/0) '
            'tombe. Sans tracking, R1 resterait quand meme le routeur actif HSRP meme '
            's\'il ne peut plus acceder a Internet — inutile ! Avec le tracking, quand '
            'Gi0/0 tombe, la priorite de R1 baisse a 90 (110-20). R2 avec sa priorite '
            'de 100 devient actif et prend le relais. Le basculement est automatique '
            'en moins de 10 secondes.'),
        3: ('Exemple : sur R2 (le routeur de secours), tu configures le meme groupe '
            'HSRP et la meme VIP 192.168.1.254, mais SANS augmenter la priorite '
            '(elle reste a 100 par defaut). R2 sait alors qu\'il doit laisser R1 etre '
            'actif. Il surveille en silence et est pret a prendre le relais en quelques '
            'secondes si R1 disparait. Le "preempt" sur R2 lui permet de reprendre '
            'le role standby si R1 revient en ligne apres une panne.'),
    },
}


class Command(BaseCommand):
    help = 'Met a jour real_world_example sur les etapes de procedure existantes'

    def handle(self, *args, **options):
        self.stdout.write('=== update_step_examples : mise a jour des exemples concrets ===')
        updated = 0
        skipped = 0
        missing = 0

        for slug, step_examples in EXAMPLES.items():
            try:
                proc = Procedure.objects.get(slug=slug)
            except Procedure.DoesNotExist:
                self.stdout.write(f'  [ABSENT] procedure introuvable : {slug}')
                missing += 1
                continue

            for step_number, example_text in step_examples.items():
                try:
                    step = ProcedureStep.objects.get(procedure=proc, step_number=step_number)
                except ProcedureStep.DoesNotExist:
                    self.stdout.write(f'  [ABSENT] etape {step_number} introuvable dans "{proc.title}"')
                    missing += 1
                    continue

                if step.real_world_example:
                    self.stdout.write(f'  [SKIP]   "{proc.title}" — etape {step_number} (deja renseigne)')
                    skipped += 1
                else:
                    step.real_world_example = example_text
                    step.save(update_fields=['real_world_example'])
                    self.stdout.write(f'  [OK]     "{proc.title}" — etape {step_number}')
                    updated += 1

        self.stdout.write('')
        self.stdout.write(f'=== Termine : {updated} mis a jour, {skipped} ignores, {missing} absents ===')
