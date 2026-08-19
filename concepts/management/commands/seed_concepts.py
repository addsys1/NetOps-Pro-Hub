"""
Commande de seed pedagogique : python manage.py seed_concepts
Ajoute les concepts reseau (mode enfant de 10 ans) par blocs.
Utilise get_or_create sur le slug — sans jamais ecraser l'existant.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from concepts.models import NetworkConcept

CONCEPTS_DATA = [

    # =========================================================================
    # BLOC 1 — Module 1 : Bases (concepts 1 a 5)
    # =========================================================================

    {
        'title': 'Le Reseau',
        'module_number': 1,
        'module_name': 'Bases',
        'level': 'base',
        'icon': 'bi-diagram-3',
        'order': 1,
        'simple_explanation': (
            "Un reseau, c'est quand plusieurs ordinateurs sont connectes ensemble pour pouvoir se parler.\n\n"
            "Imagine une classe d'ecole. Les eleves peuvent se passer des mots. "
            "Chaque eleve, c'est un ordinateur. La classe, c'est le reseau.\n\n"
            "Quand tu envoies un message a ton ami sur WhatsApp, ce message voyage a travers un reseau "
            "de milliers d'ordinateurs avant d'arriver chez lui."
        ),
        'concrete_example': (
            "Pense a la poste dans une ville.\n\n"
            "Il y a des maisons (les ordinateurs), des routes (les cables), "
            "des facteurs (les donnees qui voyagent), et un bureau de poste central (le routeur).\n\n"
            "Un reseau informatique, c'est exactement pareil : des machines reliees par des chemins, "
            "qui s'envoient des informations."
        ),
        'technical_version': (
            "Un reseau est un ensemble d'equipements (ordinateurs, switches, routeurs) "
            "interconnectes pour echanger des donnees via des protocoles communs (TCP/IP)."
        ),
        'summary': "Un reseau, c'est des ordinateurs connectes qui peuvent se parler entre eux.",
        'quiz_q1': "Qu'est-ce qu'un reseau informatique ?",
        'quiz_a1': "C'est un groupe d'ordinateurs connectes ensemble pour s'echanger des informations.",
        'quiz_q2': "Donne un exemple de reseau que tu utilises tous les jours.",
        'quiz_a2': "Internet ! C'est le plus grand reseau du monde. Mais aussi le Wi-Fi de ta maison.",
    },

    {
        'title': "L'Adresse IP",
        'module_number': 1,
        'module_name': 'Bases',
        'level': 'base',
        'icon': 'bi-geo-alt',
        'order': 2,
        'simple_explanation': (
            "Une adresse IP, c'est comme l'adresse de ta maison.\n\n"
            "Quand le facteur veut livrer un colis, il a besoin de savoir OU est ta maison. "
            "Sur Internet, chaque ordinateur a une adresse unique : son adresse IP.\n\n"
            "Ca ressemble a ca : 192.168.1.10\n"
            "C'est 4 nombres separes par des points. Chaque nombre va de 0 a 255.\n\n"
            "Sans adresse IP, les donnees ne savent pas OU aller. C'est comme envoyer une lettre sans ecrire l'adresse !"
        ),
        'concrete_example': (
            "Ta maison a une adresse : '12 rue des Lilas, Paris'.\n\n"
            "Ton ordinateur a aussi une adresse : '192.168.1.10'.\n\n"
            "Quand tu envoies un message a YouTube pour voir une video, "
            "YouTube sait ou te repondre grace a ton adresse IP. "
            "Et toi tu sais ou est YouTube grace a son adresse IP a lui."
        ),
        'technical_version': (
            "Une adresse IPv4 est un identifiant unique de 32 bits (4 octets) note en decimal pointe "
            "(ex: 192.168.1.1). Elle identifie chaque interface reseau sur un reseau IP."
        ),
        'summary': "L'adresse IP est l'adresse unique d'un ordinateur sur le reseau, comme l'adresse d'une maison.",
        'quiz_q1': "A quoi ressemble une adresse IP ?",
        'quiz_a1': "A 4 nombres separes par des points, comme 192.168.1.1. Chaque nombre va de 0 a 255.",
        'quiz_q2': "Pourquoi chaque ordinateur a besoin d'une adresse IP ?",
        'quiz_a2': "Pour que les donnees sachent exactement ou aller. Sans adresse, le message se perdrait.",
    },

    {
        'title': "L'Adresse MAC",
        'module_number': 1,
        'module_name': 'Bases',
        'level': 'base',
        'icon': 'bi-cpu',
        'order': 3,
        'simple_explanation': (
            "L'adresse MAC, c'est le numero de serie grave dans la carte reseau de ton ordinateur. "
            "Il ne change jamais. Il est unique dans le monde entier.\n\n"
            "L'adresse IP peut changer (quand tu te deconnectes du Wi-Fi, tu en recois une nouvelle). "
            "Mais l'adresse MAC, elle, reste toujours la meme. "
            "Elle est fabriclee directement dans le materiel.\n\n"
            "Ca ressemble a ca : AA:BB:CC:11:22:33\n"
            "6 groupes de 2 lettres/chiffres, separes par des deux-points."
        ),
        'concrete_example': (
            "Imagine que ton adresse IP c'est ton adresse postale (elle peut changer si tu demenages).\n\n"
            "Ton adresse MAC, c'est ton numero de passeport. Il est unique, grave dans le passeport, "
            "et tu l'as toute ta vie.\n\n"
            "Les switches utilisent les adresses MAC pour savoir vers quel port envoyer les donnees "
            "dans le meme reseau local."
        ),
        'technical_version': (
            "L'adresse MAC (Media Access Control) est un identifiant materiel unique de 48 bits (6 octets) "
            "attribue par le fabricant a chaque carte reseau. Elle opere au niveau L2 (couche liaison)."
        ),
        'summary': "L'adresse MAC est le numero de serie unique grave dans la carte reseau — elle ne change jamais.",
        'quiz_q1': "Quelle est la difference entre une adresse IP et une adresse MAC ?",
        'quiz_a1': "L'adresse IP peut changer et sert a trouver un ordinateur sur le reseau. L'adresse MAC est fixe, gravee dans le materiel, et sert a identifier l'equipement physique.",
        'quiz_q2': "A quoi ressemble une adresse MAC ?",
        'quiz_a2': "A 6 groupes de 2 caracteres hexadecimaux, comme AA:BB:CC:11:22:33.",
    },

    {
        'title': 'Le Switch',
        'module_number': 1,
        'module_name': 'Bases',
        'level': 'base',
        'icon': 'bi-hdd-network',
        'order': 4,
        'simple_explanation': (
            "Un switch, c'est la boite avec des trous ou tu branches les cables reseau dans une entreprise ou a la maison.\n\n"
            "Son travail : recevoir un message d'un ordinateur et l'envoyer UNIQUEMENT a l'ordinateur qui doit le recevoir.\n\n"
            "Il est tres intelligent : il se souvient de qui est branche sur quel port. "
            "Comme un standardiste qui sait dans quel bureau est chaque personne et dirige les appels au bon endroit."
        ),
        'concrete_example': (
            "Imagine un immeuble avec 24 appartements. Le gardien (le switch) connait tout le monde.\n\n"
            "Quand le facteur apporte un colis pour l'appartement 12, "
            "le gardien l'envoie directement au 12eme — il ne sonne pas a toutes les portes.\n\n"
            "Un vieux 'hub' (l'ancetre du switch) sonnait a toutes les portes en meme temps. "
            "Le switch, lui, est precis et efficace."
        ),
        'technical_version': (
            "Un switch est un equipement L2 qui commute les trames Ethernet en utilisant "
            "une table CAM (Content Addressable Memory) pour associer adresses MAC et ports physiques. "
            "Il fonctionne en mode unicast, multicast ou broadcast."
        ),
        'summary': "Le switch est une boite intelligente qui relie les ordinateurs et envoie les donnees directement au bon destinataire.",
        'quiz_q1': "Comment le switch sait a quel port envoyer les donnees ?",
        'quiz_a1': "Il utilise les adresses MAC. Il se souvient quelle adresse MAC est branchee sur quel port grace a sa table (table CAM).",
        'quiz_q2': "Quelle est la difference entre un switch et un vieux hub ?",
        'quiz_a2': "Le hub envoie tout a tout le monde (comme crier dans une salle). Le switch envoie directement au bon destinataire (comme chuchoter a la bonne personne).",
    },

    {
        'title': 'ARP — Comment trouver une adresse MAC',
        'module_number': 1,
        'module_name': 'Bases',
        'level': 'base',
        'icon': 'bi-search',
        'order': 5,
        'simple_explanation': (
            "ARP, c'est le protocole qui permet de trouver l'adresse MAC d'un ordinateur quand on connait son adresse IP.\n\n"
            "Sur le reseau local, les ordinateurs se parlent avec les adresses MAC. "
            "Mais toi, tu connais l'adresse IP de ton ami. Alors comment trouver son adresse MAC ?\n\n"
            "Tu cries dans la salle : 'Hé, qui a l'adresse IP 192.168.1.5 ?'\n"
            "L'ordinateur qui a cette IP repond : 'C'est moi ! Mon adresse MAC est AA:BB:CC:11:22:33.'\n\n"
            "C'est exactement ce que fait ARP."
        ),
        'concrete_example': (
            "Tu arrives dans une nouvelle classe et tu sais seulement le prenom de quelqu'un : 'Lucas'.\n\n"
            "Tu cries : 'Est-ce que Lucas est la ?'\n"
            "Lucas leve la main et dit 'C'est moi !' — et maintenant tu sais ou il est assis.\n\n"
            "ARP fait pareil : il crie l'adresse IP sur le reseau (ARP Request = broadcast), "
            "et l'ordinateur qui a cette IP repond avec son adresse MAC (ARP Reply = unicast). "
            "Tout le monde peut entendre la question, mais seul Lucas repond."
        ),
        'technical_version': (
            "ARP (Address Resolution Protocol, RFC 826) resout une adresse IPv4 en adresse MAC "
            "via un broadcast (ff:ff:ff:ff:ff:ff) sur le segment L2. "
            "Le resultat est mis en cache dans la table ARP de l'hote."
        ),
        'summary': "ARP est le protocole qui permet de trouver l'adresse MAC d'un ordinateur a partir de son adresse IP.",
        'quiz_q1': "Pourquoi a-t-on besoin de ARP ?",
        'quiz_a1': "Parce que sur le reseau local, les donnees voyagent avec les adresses MAC. ARP permet de trouver l'adresse MAC quand on connait seulement l'adresse IP.",
        'quiz_q2': "Comment fonctionne une requete ARP ?",
        'quiz_a2': "L'ordinateur envoie un message a TOUT LE MONDE (broadcast) en demandant qui a telle adresse IP. Seul l'ordinateur qui a cette IP repond avec son adresse MAC.",
    },

    # =========================================================================
    # BLOC 2 — Module 2 : Organisation du reseau (concepts 6 a 9)
    #          Module 3 : Segmentation — concept 10 (VLAN)
    # =========================================================================

    {
        'title': 'Le Sous-reseau (Subnet)',
        'module_number': 2,
        'module_name': 'Organisation du reseau',
        'level': 'base',
        'icon': 'bi-grid-3x3',
        'order': 1,
        'simple_explanation': (
            "Un sous-reseau, c'est un quartier dans une ville.\n\n"
            "Imagine une grande ville avec des milliers de maisons. "
            "Pour s'organiser, on divise la ville en quartiers : le quartier nord, le quartier sud, le quartier est...\n\n"
            "Sur un reseau informatique, c'est pareil. "
            "On divise le grand reseau en petits sous-reseaux (subnets). "
            "Chaque sous-reseau regroupe des ordinateurs qui sont 'proches' — comme les maisons d'un meme quartier.\n\n"
            "Ca evite que tout le monde se parle en meme temps et ca rend le reseau plus rapide et plus organise."
        ),
        'concrete_example': (
            "Dans une entreprise, il y a le service Comptabilite, le service Informatique et le service RH.\n\n"
            "On leur donne chacun leur propre sous-reseau :\n"
            "- Comptabilite : 192.168.10.0/24\n"
            "- Informatique : 192.168.20.0/24\n"
            "- RH : 192.168.30.0/24\n\n"
            "Chaque service est dans son propre quartier. "
            "Les conversations restent dans le quartier, et ca va beaucoup plus vite."
        ),
        'technical_version': (
            "Un subnet est une subdivision logique d'un reseau IP definie par un prefixe reseau et un masque. "
            "Ex : 192.168.1.0/24 — le /24 indique que les 24 premiers bits identifient le reseau."
        ),
        'summary': "Un sous-reseau est un quartier dans le grand reseau : il regroupe des machines proches pour mieux organiser les communications.",
        'quiz_q1': "Pourquoi divise-t-on un reseau en sous-reseaux ?",
        'quiz_a1': "Pour organiser les machines par groupes, limiter les broadcasts, et ameliorer la securite et les performances.",
        'quiz_q2': "Que signifie le '/24' dans l'adresse 192.168.1.0/24 ?",
        'quiz_a2': "Ca indique que les 24 premiers bits (les 3 premiers nombres) identifient le reseau. Il reste 8 bits pour les hotes, soit 254 adresses utilisables.",
    },

    {
        'title': 'Le Subnetting',
        'module_number': 2,
        'module_name': 'Organisation du reseau',
        'level': 'intermediate',
        'icon': 'bi-scissors',
        'order': 2,
        'simple_explanation': (
            "Le subnetting, c'est l'art de couper un grand reseau en plusieurs petits morceaux.\n\n"
            "Imagine une grande pizza. "
            "Tu peux la couper en 2, en 4, en 8 parts... "
            "Plus tu coupes, plus tu as de parts, mais chaque part est plus petite.\n\n"
            "En informatique, on prend un grand reseau — par exemple 192.168.1.0/24 — "
            "et on le coupe en plusieurs sous-reseaux plus petits.\n\n"
            "Le masque de sous-reseau dit combien de machines peuvent entrer dans chaque morceau. "
            "Plus le masque est grand (ex: /28), plus les morceaux sont petits."
        ),
        'concrete_example': (
            "Tu as un grand batiment avec 200 bureaux (le reseau /24 = 254 adresses).\n\n"
            "Tu decides de le diviser en 4 etages de 50 bureaux chacun (/26 = 62 adresses chacun) :\n"
            "- Etage 1 : 192.168.1.0/26   (bureaux 1 a 62)\n"
            "- Etage 2 : 192.168.1.64/26  (bureaux 63 a 126)\n"
            "- Etage 3 : 192.168.1.128/26 (bureaux 127 a 190)\n"
            "- Etage 4 : 192.168.1.192/26 (bureaux 191 a 254)\n\n"
            "Chaque etage est independant. Les gens d'un etage ne derangent pas les autres."
        ),
        'technical_version': (
            "Le subnetting consiste a emprunter des bits a la partie hote d'une adresse pour creer des sous-reseaux. "
            "Chaque bit emprunte double le nombre de subnets et divise par 2 le nombre d'hotes par subnet. "
            "Formules : nb subnets = 2^n, nb hotes = 2^(32-prefixe) - 2."
        ),
        'summary': "Le subnetting consiste a decouper un grand reseau en petits sous-reseaux en modifiant le masque — comme couper une pizza en parts.",
        'quiz_q1': "Combien d'adresses utilisables y a-t-il dans un /26 ?",
        'quiz_a1': "62 adresses. Formule : 2^(32-26) - 2 = 2^6 - 2 = 64 - 2 = 62. On retire l'adresse reseau et le broadcast.",
        'quiz_q2': "Si tu passes un reseau /24 en /26, combien de sous-reseaux obtiens-tu ?",
        'quiz_a2': "4 sous-reseaux. On a emprunte 2 bits (26-24=2), donc 2^2 = 4 sous-reseaux.",
    },

    {
        'title': 'Adresse Reseau, Hote et Broadcast',
        'module_number': 2,
        'module_name': 'Organisation du reseau',
        'level': 'intermediate',
        'icon': 'bi-diagram-2',
        'order': 3,
        'simple_explanation': (
            "Dans chaque sous-reseau, il y a 3 types d'adresses speciales :\n\n"
            "1. L'adresse RESEAU : c'est le nom du quartier. "
            "On ne peut pas l'utiliser pour une machine. "
            "Ex : 192.168.1.0 — c'est 'le quartier 192.168.1'\n\n"
            "2. Les adresses HOTES : ce sont toutes les adresses du milieu. "
            "Tu peux les donner a des ordinateurs, imprimantes, telephones...\n\n"
            "3. L'adresse BROADCAST : c'est l'adresse pour parler a TOUT LE MONDE dans le quartier en meme temps. "
            "Ex : 192.168.1.255 — si tu envoies un message ici, tout le quartier l'entend."
        ),
        'concrete_example': (
            "Imagine la rue des Roses avec les maisons numerotees de 1 a 254.\n\n"
            "- Numero 0 (192.168.1.0) : c'est le nom de la rue — personne n'habite la.\n"
            "- Numeros 1 a 254 (192.168.1.1 a .254) : ce sont les maisons — les vraies adresses.\n"
            "- Numero 255 (192.168.1.255) : c'est le haut-parleur de la rue. "
            "Quand quelqu'un crie dedans, toutes les maisons entendent.\n\n"
            "Pour 192.168.1.0/24 : 254 maisons disponibles, 1 nom de rue, 1 haut-parleur."
        ),
        'technical_version': (
            "Dans un subnet X.X.X.0/24 : l'adresse reseau (tous bits hote = 0) identifie le subnet, "
            "les adresses hotes sont entre .1 et .254, "
            "le broadcast (tous bits hote = 1) est .255 et envoie a tous les hotes du subnet."
        ),
        'summary': "Chaque sous-reseau a une adresse reseau (nom du quartier), des adresses hotes (les maisons) et une adresse broadcast (le haut-parleur).",
        'quiz_q1': "Dans le reseau 192.168.10.0/24, quelle est l'adresse broadcast ?",
        'quiz_a1': "192.168.10.255 — c'est toujours le dernier numero du sous-reseau. Un message envoye ici est recu par tous les hotes du reseau.",
        'quiz_q2': "Peut-on donner l'adresse 192.168.10.0 ou 192.168.10.255 a un ordinateur ?",
        'quiz_a2': "Non. L'adresse .0 est reservee pour identifier le reseau, et .255 est le broadcast. On ne peut pas les attribuer a des machines.",
    },

    {
        'title': 'La Passerelle par defaut (Default Gateway)',
        'module_number': 2,
        'module_name': 'Organisation du reseau',
        'level': 'base',
        'icon': 'bi-door-open',
        'order': 4,
        'simple_explanation': (
            "La passerelle par defaut, c'est la porte de sortie de ton quartier reseau.\n\n"
            "Quand tu veux envoyer un message a quelqu'un dans TON quartier (meme sous-reseau), "
            "tu lui parles directement — pas besoin de passer par la porte.\n\n"
            "Mais si tu veux parler a quelqu'un dans UN AUTRE quartier (autre sous-reseau ou Internet), "
            "tu dois passer par la porte — la passerelle.\n\n"
            "La passerelle, c'est en general l'adresse IP de ton routeur. "
            "C'est lui qui connait les autres quartiers et qui sait comment y aller."
        ),
        'concrete_example': (
            "Tu habites dans un quartier ferme avec un seul portail pour sortir.\n\n"
            "Si tu veux voir ton voisin d'a cote (meme quartier) : tu traverses la rue directement.\n\n"
            "Si tu veux aller en ville (autre reseau) ou a l'etranger (Internet) : "
            "tu DOIS passer par le portail. Ce portail, c'est ta passerelle.\n\n"
            "Sur ton ordinateur, la passerelle par defaut est souvent 192.168.1.1 ou 192.168.0.1 — "
            "c'est ton routeur Wi-Fi a la maison !"
        ),
        'technical_version': (
            "La default gateway est l'adresse IP du routeur sur le segment local. "
            "Un hote l'utilise pour forwarder les paquets destines a des reseaux non-locaux. "
            "Si aucune route specifique n'existe, le paquet est envoye a la default gateway."
        ),
        'summary': "La passerelle par defaut est la porte de sortie du reseau local — c'est par elle que passent tous les messages destines a l'exterieur.",
        'quiz_q1': "Quand un ordinateur utilise-t-il sa passerelle par defaut ?",
        'quiz_a1': "Quand il veut envoyer un message a un ordinateur qui n'est PAS dans son sous-reseau — par exemple pour aller sur Internet.",
        'quiz_q2': "Qu'est-ce qui se passe si tu n'as pas de passerelle par defaut configuree ?",
        'quiz_a2': "Tu peux parler aux autres ordinateurs de ton reseau local, mais tu ne peux plus acceder a Internet ni aux autres sous-reseaux. Tu es coince dans ton quartier.",
    },

    {
        'title': 'Le VLAN',
        'module_number': 3,
        'module_name': 'Segmentation',
        'level': 'intermediate',
        'icon': 'bi-layers',
        'order': 1,
        'simple_explanation': (
            "Un VLAN, c'est un reseau virtuel invisible cree a l'interieur d'un switch.\n\n"
            "Imagine que tu as un grand bureau avec 50 personnes. "
            "Tout le monde est dans la meme salle mais tu veux que la Comptabilite "
            "ne puisse pas voir les messages de l'Informatique, et vice-versa.\n\n"
            "Avec les VLANs, tu peux creer des murs invisibles entre les groupes, "
            "sans avoir besoin de cables differents ou de salles differentes.\n\n"
            "Chaque VLAN a un numero (entre 1 et 4094). "
            "Les machines dans le VLAN 10 ne voient que les autres machines du VLAN 10."
        ),
        'concrete_example': (
            "Dans une ecole, tous les eleves et les professeurs utilisent le meme reseau Wi-Fi.\n\n"
            "Mais on cree deux VLANs :\n"
            "- VLAN 10 : Professeurs — acces aux notes, aux fichiers confidentiels\n"
            "- VLAN 20 : Eleves — acces a Internet seulement\n\n"
            "Les eleves et les professeurs utilisent les memes cables et le meme switch, "
            "mais grace aux VLANs, ils ne se voient pas et ne peuvent pas s'espionner.\n\n"
            "C'est comme des couloirs invisibles dans les cables."
        ),
        'technical_version': (
            "Un VLAN (Virtual LAN, IEEE 802.1Q) est un domaine de broadcast logique configure sur un switch. "
            "Les trames sont taguees avec un VLAN ID (12 bits, valeurs 1-4094). "
            "Les hotes de VLANs differents ne communiquent qu'a travers un routeur ou un switch L3."
        ),
        'summary': "Un VLAN est un reseau virtuel invisible sur un switch — il separe les machines en groupes independants sans changer le cablage.",
        'quiz_q1': "Deux ordinateurs sont sur le meme switch mais dans des VLANs differents. Peuvent-ils se parler directement ?",
        'quiz_a1': "Non ! Des VLANs differents sont comme des reseaux differents. Il faut passer par un routeur (ou un switch L3) pour communiquer entre VLANs.",
        'quiz_q2': "Quel est l'avantage principal des VLANs ?",
        'quiz_a2': "La securite et l'organisation : on peut separer les services (RH, Compta, IT) sans changer le cablage physique. Chaque groupe reste dans son propre reseau virtuel.",
    },

    # =========================================================================
    # BLOC 3 — Module 3 : Segmentation (suite) + Module 4 : Communication
    # Concepts 11 a 15 : Access Port, Trunk, VTP, Routeur, Table de routage
    # =========================================================================

    {
        'title': "Le Port Access",
        'module_number': 3,
        'module_name': 'Segmentation',
        'level': 'intermediate',
        'icon': 'bi-plug',
        'order': 2,
        'simple_explanation': (
            "Un port access, c'est un port de switch qui appartient a UN SEUL VLAN.\n\n"
            "Imagine que tu as un interrupteur dans ta maison. "
            "Cet interrupteur ne controle qu'une seule lampe — pas plusieurs. "
            "C'est ca, un port access : il ne laisse passer qu'un seul VLAN.\n\n"
            "Quand un ordinateur est branche sur un port access en VLAN 10, "
            "il ne voit QUE les autres machines du VLAN 10. "
            "Il ne sait meme pas que d'autres VLANs existent.\n\n"
            "C'est le type de port qu'on utilise pour connecter les ordinateurs des utilisateurs."
        ),
        'concrete_example': (
            "Dans une entreprise, Marie de la Comptabilite branche son ordinateur "
            "sur le port FastEthernet0/5 du switch.\n\n"
            "Ce port est configure en mode access VLAN 10 (VLAN Comptabilite).\n\n"
            "L'ordinateur de Marie recoit automatiquement une adresse IP du sous-reseau Comptabilite. "
            "Elle voit les imprimantes et serveurs de la Compta. "
            "Elle ne voit pas du tout le reseau de l'Informatique (VLAN 20).\n\n"
            "Le port access fait ce tri pour elle, en silence."
        ),
        'technical_version': (
            "Un port access (switchport mode access) est configure pour un seul VLAN. "
            "Les trames sont transmises sans tag 802.1Q. "
            "L'equipement connecte ne sait pas qu'il est dans un VLAN specifique."
        ),
        'summary': "Un port access connecte un seul appareil a un seul VLAN — c'est le port standard pour les ordinateurs des utilisateurs.",
        'quiz_q1': "Combien de VLANs peut transporter un port access ?",
        'quiz_a1': "Un seul. C'est la definition d'un port access : il appartient a exactement un VLAN.",
        'quiz_q2': "Est-ce que l'ordinateur connecte sur un port access sait dans quel VLAN il est ?",
        'quiz_a2': "Non ! Le switch gere le VLAN de facon transparente. L'ordinateur recoit juste une adresse IP normale et ne voit que les machines de son VLAN.",
    },

    {
        'title': 'Le Trunk (Lien Trunk)',
        'module_number': 3,
        'module_name': 'Segmentation',
        'level': 'intermediate',
        'icon': 'bi-arrows-expand',
        'order': 3,
        'simple_explanation': (
            "Un trunk, c'est un lien qui transporte PLUSIEURS VLANs en meme temps.\n\n"
            "Imagine un tuyau entre deux immeubles. "
            "Dans ce tuyau, tu fais passer de l'eau chaude, de l'eau froide et du gaz — "
            "chaque fluide dans son propre canal invisible.\n\n"
            "Le trunk, c'est pareil : dans un seul cable entre deux switches, "
            "on fait voyager le VLAN 10, le VLAN 20, le VLAN 30... tous en meme temps.\n\n"
            "Pour distinguer les VLANs, chaque message recoit une etiquette (un tag) "
            "avec son numero de VLAN. Le protocole qui fait ca s'appelle 802.1Q."
        ),
        'concrete_example': (
            "Dans un batiment, il y a deux etages connectes par un seul cable reseau.\n\n"
            "Au rez-de-chaussee : switch 1 avec des machines en VLAN 10 et VLAN 20.\n"
            "Au premier etage : switch 2 avec aussi des machines en VLAN 10 et VLAN 20.\n\n"
            "On configure un SEUL cable trunk entre les deux switches. "
            "Dans ce cable, les messages du VLAN 10 ont un badge 'VLAN 10' "
            "et ceux du VLAN 20 ont un badge 'VLAN 20'.\n\n"
            "A l'arrivee, le switch 2 lit le badge et envoie chaque message "
            "uniquement aux bonnes machines."
        ),
        'technical_version': (
            "Un port trunk (switchport mode trunk) transporte plusieurs VLANs via le tagging 802.1Q. "
            "Chaque trame recoit un tag de 4 octets contenant le VLAN ID. "
            "Le VLAN natif (defaut : VLAN 1) est transmis sans tag."
        ),
        'summary': "Un trunk est un lien entre deux switches qui transporte plusieurs VLANs simultanement grace a des etiquettes (tags 802.1Q).",
        'quiz_q1': "Quelle est la difference entre un port access et un port trunk ?",
        'quiz_a1': "Un port access transporte un seul VLAN (pour les PC utilisateurs). Un port trunk transporte plusieurs VLANs en meme temps (pour les liens entre switches ou vers les routeurs).",
        'quiz_q2': "Comment le switch sait a quel VLAN appartient une trame sur un trunk ?",
        'quiz_a2': "Grace au tag 802.1Q — une etiquette ajoutee dans la trame qui contient le numero du VLAN. A l'arrivee, le switch lit ce tag et sait exactement ou envoyer la trame.",
    },

    {
        'title': 'VTP — Synchroniser les VLANs automatiquement',
        'module_number': 3,
        'module_name': 'Segmentation',
        'level': 'intermediate',
        'icon': 'bi-arrow-repeat',
        'order': 4,
        'simple_explanation': (
            "VTP, c'est un systeme qui copie automatiquement la liste des VLANs "
            "sur tous les switches d'un reseau.\n\n"
            "Imagine que tu geres 20 switches dans un batiment. "
            "Sans VTP, si tu crees un nouveau VLAN, tu dois aller sur CHAQUE switch "
            "et le creer manuellement — 20 fois !\n\n"
            "Avec VTP, tu crees le VLAN UNE SEULE FOIS sur le switch principal (le serveur). "
            "VTP l'envoie automatiquement a tous les autres switches (les clients). "
            "En quelques secondes, tous les switches connaissent le nouveau VLAN."
        ),
        'concrete_example': (
            "Pense a un professeur qui photocopie un document pour toute la classe.\n\n"
            "Sans VTP : le prof doit ecrire le meme document 30 fois a la main pour 30 eleves.\n"
            "Avec VTP : le prof ecrit le document une fois sur le tableau (switch serveur), "
            "et la photocopieuse (VTP) en fait automatiquement une copie pour chaque eleve (switches clients).\n\n"
            "ATTENTION : VTP est dangereux ! "
            "Si tu connectes un vieux switch avec une liste de VLANs differente, "
            "il peut ecraser la liste de tout le reseau. "
            "C'est comme si quelqu'un effacait le tableau et reecrivait tout !"
        ),
        'technical_version': (
            "VTP (VLAN Trunking Protocol, Cisco) propage la base de donnees VLAN via les trunks. "
            "Modes : Server (cree/modifie VLANs), Client (recoit seulement), Transparent (local). "
            "Un switch avec un Configuration Revision plus eleve ecrase les autres — risque critique."
        ),
        'summary': "VTP synchronise automatiquement la liste des VLANs sur tous les switches du reseau depuis un serveur central.",
        'quiz_q1': "Quel est le role d'un switch en mode VTP Client ?",
        'quiz_a1': "Il recoit la liste des VLANs du serveur VTP et l'applique automatiquement. Il ne peut pas creer ou modifier des VLANs lui-meme.",
        'quiz_q2': "Quel est le grand danger de VTP ?",
        'quiz_a2': "Connecter un vieux switch avec un numero de revision plus eleve peut ecraser la liste de VLANs de tout le domaine et couper le reseau. Toujours verifier le revision number avant de connecter un switch.",
    },

    {
        'title': 'Le Routeur',
        'module_number': 4,
        'module_name': 'Communication entre reseaux',
        'level': 'base',
        'icon': 'bi-arrow-left-right',
        'order': 1,
        'simple_explanation': (
            "Un routeur, c'est le GPS du reseau. "
            "Son travail : faire voyager les messages d'un reseau a un autre.\n\n"
            "Le switch s'occupe des messages DANS un reseau (meme quartier). "
            "Mais quand un message doit sortir du quartier pour aller ailleurs — "
            "dans un autre sous-reseau ou sur Internet — c'est le routeur qui prend le relai.\n\n"
            "Le routeur connait des chemins. "
            "Il sait que pour aller au reseau 192.168.2.0, il faut passer par telle porte. "
            "Et pour aller sur Internet, il faut passer par une autre porte.\n\n"
            "Il choisit TOUJOURS le meilleur chemin."
        ),
        'concrete_example': (
            "Imagine une ville avec plusieurs quartiers et une route nationale.\n\n"
            "Le switch, c'est les petites rues a l'interieur d'un quartier — il gere le trafic local.\n\n"
            "Le routeur, c'est le grand carrefour a la sortie du quartier. "
            "Quand tu veux aller dans un autre quartier, tu passes par le carrefour. "
            "Le carrefour (routeur) regarde ta destination et t'indique : "
            "'Pour aller au centre-ville, prends la nationale. "
            "Pour aller a l'aeroport, prends l'autoroute.'\n\n"
            "Ton routeur Wi-Fi a la maison fait exactement ca : il envoie tes requetes vers Internet."
        ),
        'technical_version': (
            "Un routeur est un equipement L3 qui forwardes les paquets IP entre differents sous-reseaux "
            "en se basant sur la table de routage. Il decremente le TTL et recalcule le checksum IP."
        ),
        'summary': "Le routeur est le carrefour du reseau — il dirige les paquets d'un reseau vers un autre en choisissant toujours le meilleur chemin.",
        'quiz_q1': "Quelle est la difference entre un switch et un routeur ?",
        'quiz_a1': "Le switch travaille DANS un reseau (meme sous-reseau, adresses MAC). Le routeur travaille ENTRE les reseaux (sous-reseaux differents, adresses IP). Le switch ne sait pas router — le routeur ne sait pas commuter.",
        'quiz_q2': "Dans ta maison, quel appareil joue le role de routeur ?",
        'quiz_a2': "Ta box Internet (Livebox, Freebox, etc.). Elle fait le lien entre ton reseau local (192.168.x.x) et Internet. Elle est a la fois routeur et switch (et souvent point d'acces Wi-Fi).",
    },

    {
        'title': 'La Table de routage',
        'module_number': 4,
        'module_name': 'Communication entre reseaux',
        'level': 'intermediate',
        'icon': 'bi-map',
        'order': 2,
        'simple_explanation': (
            "La table de routage, c'est la carte routiere du routeur.\n\n"
            "Quand un paquet arrive sur le routeur, le routeur regarde dans sa table : "
            "'Ce paquet va vers 192.168.2.5 — par ou je dois l'envoyer ?'\n\n"
            "La table contient des lignes comme :\n"
            "- 'Pour aller au reseau 192.168.1.0/24 : passe par l'interface Gi0/0'\n"
            "- 'Pour aller au reseau 10.0.0.0/8 : passe par le voisin 203.0.113.1'\n"
            "- 'Pour tout le reste (0.0.0.0/0) : va vers Internet via Gi0/1'\n\n"
            "Le routeur cherche toujours la route la plus specifique — "
            "la plus precise qui correspond a la destination."
        ),
        'concrete_example': (
            "Imagine un livreur de pizza avec une carte de la ville.\n\n"
            "Sa carte dit :\n"
            "- 'Rue des Lilas (1-20) : tourne a gauche au carrefour'\n"
            "- 'Rue des Roses (50-100) : prends l'avenue principale'\n"
            "- 'Toutes les autres adresses : suis la nationale'\n\n"
            "Quand il recoit une livraison pour le 15 rue des Lilas, "
            "il suit la premiere regle — la plus precise.\n\n"
            "Le routeur fait pareil : il cherche la ligne la plus precise dans sa table, "
            "et si rien ne correspond, il utilise la route par defaut (0.0.0.0/0) — "
            "comme suivre la nationale quand on ne sait pas."
        ),
        'technical_version': (
            "La table de routage (RIB — Routing Information Base) contient des entrees avec : "
            "prefixe destination, masque, next-hop, interface de sortie, distance administrative et metrique. "
            "Le routeur applique le Longest Prefix Match (LPM) pour choisir la route."
        ),
        'summary': "La table de routage est la carte du routeur — elle dit par ou envoyer chaque paquet selon sa destination.",
        'quiz_q1': "Que fait le routeur si aucune route ne correspond exactement a la destination ?",
        'quiz_a1': "Il utilise la route par defaut (0.0.0.0/0), aussi appelee 'gateway of last resort'. C'est le chemin de secours pour tout le trafic sans destination connue.",
        'quiz_q2': "Qu'est-ce que le Longest Prefix Match ?",
        'quiz_a2': "C'est la regle qui dit : quand plusieurs routes correspondent, le routeur choisit toujours la plus precise (le prefixe le plus long). Ex : /28 est prefere a /24 pour une meme destination.",
    },

    # =========================================================================
    # BLOC 4 — Module 4 : Communication (suite) + Module 5 : Services reseau
    # Concepts 16 a 20 : Inter-VLAN, ROAS, DHCP, DNS, NAT
    # =========================================================================

    {
        'title': 'Le Routage Inter-VLAN',
        'module_number': 4,
        'module_name': 'Communication entre reseaux',
        'level': 'intermediate',
        'icon': 'bi-intersect',
        'order': 3,
        'simple_explanation': (
            "Par defaut, deux VLANs differents ne peuvent pas se parler. "
            "Ils sont isoles, chacun dans sa bulle.\n\n"
            "Le routage inter-VLAN, c'est la solution pour faire communiquer ces deux bulles.\n\n"
            "Pour ca, il faut un routeur (ou un switch L3) qui connait les deux VLANs "
            "et qui peut faire passer les messages de l'un a l'autre.\n\n"
            "C'est comme deux iles separees par la mer. "
            "Sans pont, impossible de passer de l'une a l'autre. "
            "Le routeur, c'est le pont entre les iles-VLANs."
        ),
        'concrete_example': (
            "Dans une entreprise, la Comptabilite (VLAN 10) veut envoyer un fichier "
            "au serveur de l'Informatique (VLAN 20).\n\n"
            "Sans routage inter-VLAN : impossible — les VLANs sont des murs.\n\n"
            "Avec routage inter-VLAN sur un switch L3 :\n"
            "1. Le PC de Compta envoie le fichier a sa passerelle (192.168.10.1 — SVI VLAN 10)\n"
            "2. Le switch L3 voit que la destination est dans le VLAN 20\n"
            "3. Il fait passer le paquet vers le VLAN 20 (192.168.20.0)\n"
            "4. Le serveur Informatique recoit le fichier\n\n"
            "Le switch L3 joue le role de pont entre les deux quartiers."
        ),
        'technical_version': (
            "Le routage inter-VLAN utilise des SVIs (Switch Virtual Interfaces) sur un switch L3 "
            "ou des sous-interfaces sur un routeur. Chaque VLAN a une interface L3 (passerelle). "
            "Le trafic entre VLANs est route au niveau L3 (adresses IP)."
        ),
        'summary': "Le routage inter-VLAN permet a des machines de VLANs differents de communiquer en passant par un routeur ou un switch L3.",
        'quiz_q1': "Sans routage inter-VLAN, est-ce qu'un PC en VLAN 10 peut parler a un PC en VLAN 20 ?",
        'quiz_a1': "Non. Les VLANs sont des reseaux isoles. Sans routeur ou switch L3 entre eux, la communication est impossible.",
        'quiz_q2': "Comment appelle-t-on l'interface virtuelle configuree sur un switch L3 pour router entre VLANs ?",
        'quiz_a2': "Une SVI (Switch Virtual Interface) ou interface VLAN. Ex : 'interface vlan 10' avec une adresse IP — c'est la passerelle des machines du VLAN 10.",
    },

    {
        'title': 'Router-on-a-Stick',
        'module_number': 4,
        'module_name': 'Communication entre reseaux',
        'level': 'intermediate',
        'icon': 'bi-signpost-split',
        'order': 4,
        'simple_explanation': (
            "Router-on-a-Stick (ROAS), ca veut dire 'routeur sur un baton'.\n\n"
            "C'est une methode pour faire du routage inter-VLAN avec UN SEUL cable "
            "entre le routeur et le switch.\n\n"
            "Sur ce cable unique, on fait passer TOUS les VLANs en meme temps (trunk). "
            "Le routeur cree des sous-interfaces virtuelles — une par VLAN. "
            "Chaque sous-interface a sa propre adresse IP et gere un VLAN.\n\n"
            "C'est economique : un seul cable au lieu d'un cable par VLAN. "
            "Mais c'est lent sur de gros reseaux car tout le trafic inter-VLAN "
            "passe par ce meme cable unique."
        ),
        'concrete_example': (
            "Imagine un grand immeuble avec 4 etages (4 VLANs). "
            "Pour que les etages puissent communiquer, tu as besoin d'un ascenseur (le routeur).\n\n"
            "Option normale : 4 ascenseurs — un par etage. Cher !\n\n"
            "Router-on-a-Stick : 1 seul ascenseur avec des boutons differenties "
            "(sous-interfaces). Le meme ascenseur dessert les 4 etages — juste un peu plus lent "
            "car tout le monde utilise le meme.\n\n"
            "Sur Cisco, les sous-interfaces s'appellent Gi0/0.10, Gi0/0.20, etc. "
            "Chacune gere un VLAN avec la commande 'encapsulation dot1Q'."
        ),
        'technical_version': (
            "ROAS utilise une interface physique tronquee avec des sous-interfaces dot1Q. "
            "Chaque sous-interface (Gi0/0.X) a une commande 'encapsulation dot1Q <vlan-id>' "
            "et une adresse IP de passerelle. Limite : tout le trafic inter-VLAN sature le lien physique."
        ),
        'summary': "Router-on-a-Stick permet le routage inter-VLAN via un seul cable trunk, avec des sous-interfaces virtuelles sur le routeur — une par VLAN.",
        'quiz_q1': "Pourquoi appelle-t-on cette methode 'Router-on-a-Stick' ?",
        'quiz_a1': "Parce que tout passe par un seul lien (le 'baton') entre le switch et le routeur. Ce lien unique supporte tous les VLANs en mode trunk.",
        'quiz_q2': "Quel est le principal inconvenient du Router-on-a-Stick ?",
        'quiz_a2': "Tout le trafic inter-VLAN passe par un seul cable physique. Sur de grands reseaux tres actifs, ce cable devient un goulot d'etranglement. Mieux vaut alors utiliser un switch L3.",
    },

    {
        'title': 'DHCP — Attribution automatique des adresses IP',
        'module_number': 5,
        'module_name': 'Services reseau',
        'level': 'base',
        'icon': 'bi-hand-index',
        'order': 1,
        'simple_explanation': (
            "DHCP, c'est le service qui donne automatiquement une adresse IP "
            "a chaque ordinateur qui se connecte au reseau.\n\n"
            "Sans DHCP, tu devrais configurer manuellement l'adresse IP de chaque machine. "
            "Dans une entreprise avec 500 ordinateurs, ce serait un cauchemar !\n\n"
            "Avec DHCP, c'est automatique :\n"
            "1. Ton ordi arrive sur le reseau et crie : 'Bonjour ! Quelqu'un peut me donner une adresse ?'\n"
            "2. Le serveur DHCP repond : 'Oui ! Prends le 192.168.1.42 — valable 7 jours.'\n"
            "3. Ton ordi utilise cette adresse.\n\n"
            "C'est appele un 'bail' (lease) — comme une location temporaire."
        ),
        'concrete_example': (
            "Imagine un parking avec des places numerotees.\n\n"
            "Sans DHCP : chaque voiture a une place reservee a vie — "
            "meme si la voiture n'est pas la, la place est bloquee.\n\n"
            "Avec DHCP : un agent (le serveur DHCP) est a l'entree. "
            "Quand une voiture arrive, l'agent dit : 'Prends la place 42 — tu peux rester 8h.' "
            "Quand tu pars, l'agent recupère la place et la donne a une autre voiture.\n\n"
            "Quand tu te connectes au Wi-Fi de ta maison, ta box joue ce role : "
            "elle te donne automatiquement une adresse IP temporaire."
        ),
        'technical_version': (
            "DHCP (RFC 2131) attribue dynamiquement une adresse IP, un masque, une passerelle "
            "et un DNS via le processus DORA : Discover (broadcast) > Offer > Request > Ack. "
            "Le bail a une duree definie — le client doit renouveler avant expiration."
        ),
        'summary': "DHCP distribue automatiquement des adresses IP aux machines du reseau — comme un agent de parking qui attribue les places a l'arrivee.",
        'quiz_q1': "Que signifie DORA dans le processus DHCP ?",
        'quiz_a1': "Discover (le client cherche un serveur), Offer (le serveur propose une IP), Request (le client accepte l'offre), Acknowledge (le serveur confirme). C'est la poignee de main DHCP en 4 etapes.",
        'quiz_q2': "Qu'est-ce qu'un bail DHCP (lease) ?",
        'quiz_a2': "C'est la duree pendant laquelle une adresse IP est reservee pour un appareil. Apres expiration, l'adresse est liberee et peut etre donnee a quelqu'un d'autre.",
    },

    {
        'title': 'DNS — Le Carnet d\'adresses d\'Internet',
        'module_number': 5,
        'module_name': 'Services reseau',
        'level': 'base',
        'icon': 'bi-book',
        'order': 2,
        'simple_explanation': (
            "DNS, c'est le service qui traduit les noms de sites en adresses IP.\n\n"
            "Toi, tu retiens facilement 'google.com'. "
            "Mais les ordinateurs, eux, communiquent avec des adresses IP comme '142.250.74.46'.\n\n"
            "Le DNS fait la traduction : quand tu tapes 'google.com', "
            "ton ordinateur demande au DNS : 'C'est quoi l'adresse IP de google.com ?' "
            "Le DNS repond : '142.250.74.46'. "
            "Ton ordinateur va ensuite directement a cette adresse.\n\n"
            "Sans DNS, tu devrais memoriser l'adresse IP de chaque site que tu visites. "
            "Personne ne ferait ca !"
        ),
        'concrete_example': (
            "Imagine un carnet de contacts sur ton telephone.\n\n"
            "Tu ne retiens pas le numero '06 12 34 56 78' de ton ami Lucas. "
            "Tu retiens juste 'Lucas'. Quand tu veux l'appeler, "
            "ton telephone cherche 'Lucas' dans le carnet et compose le bon numero.\n\n"
            "DNS, c'est le carnet de contacts d'Internet. "
            "Tu dis 'youtube.com', le DNS cherche le numero (l'IP), "
            "et ton navigateur appelle le bon serveur.\n\n"
            "Les serveurs DNS publics les plus connus : 8.8.8.8 (Google) et 1.1.1.1 (Cloudflare)."
        ),
        'technical_version': (
            "DNS (RFC 1034/1035) est un systeme hierarchique de resolution de noms. "
            "Il resout des FQDNs en adresses IP via des enregistrements (A, AAAA, CNAME, MX...). "
            "La resolution passe par les resolvers, root servers, TLD servers et serveurs autoritaires."
        ),
        'summary': "DNS traduit les noms de sites (google.com) en adresses IP — c'est le carnet d'adresses d'Internet.",
        'quiz_q1': "Que se passerait-il si le DNS tombait en panne ?",
        'quiz_a1': "Tu ne pourrais plus acceder aux sites par leur nom. Internet fonctionnerait encore, mais tu devrais taper directement les adresses IP — ce que personne ne connait par coeur.",
        'quiz_q2': "Quel type d'enregistrement DNS permet de trouver l'adresse IPv4 d'un nom de domaine ?",
        'quiz_a2': "L'enregistrement de type A. Ex : 'google.com A 142.250.74.46'. Pour IPv6, c'est un enregistrement AAAA.",
    },

    {
        'title': 'NAT — Partager une seule adresse IP publique',
        'module_number': 5,
        'module_name': 'Services reseau',
        'level': 'intermediate',
        'icon': 'bi-shuffle',
        'order': 3,
        'simple_explanation': (
            "NAT, c'est la technique qui permet a tous les ordinateurs de ta maison "
            "de partager une seule adresse IP publique pour aller sur Internet.\n\n"
            "Ta box a UNE adresse IP publique visible depuis Internet (ex: 82.45.12.7). "
            "Mais chez toi, tu as 5 appareils : PC, telephone, tablette, TV, console...\n\n"
            "NAT joue le role d'un receptionniste dans un hotel :\n"
            "- Quand le PC envoie une requete, NAT note 'c'est le PC qui demande' et l'envoie depuis l'IP publique.\n"
            "- Quand la reponse revient, NAT sait que c'est pour le PC et lui livre.\n\n"
            "Ca resout aussi le probleme de manque d'adresses IPv4 dans le monde !"
        ),
        'concrete_example': (
            "Un immeuble de 50 appartements a une seule boite aux lettres exterieure "
            "avec une seule adresse postale visible depuis l'exterieur.\n\n"
            "Le gardien (NAT/PAT) gere tout :\n"
            "- Appartement 3 commande un colis : le gardien note 'appt 3' et met l'adresse de l'immeuble.\n"
            "- Le colis arrive a l'adresse de l'immeuble. Le gardien lit ses notes et le livre a l'appt 3.\n\n"
            "Depuis l'exterieur, on ne voit que l'immeuble — jamais les appartements individuels. "
            "C'est exactement comme ca que NAT cache ton reseau prive derriere une seule IP publique."
        ),
        'technical_version': (
            "NAT (Network Address Translation, RFC 3022) traduit les adresses IP privees (RFC 1918) "
            "en adresse publique. PAT (Port Address Translation / NAT Overload) multiplexe "
            "plusieurs connexions via des numeros de port uniques sur une seule IP publique."
        ),
        'summary': "NAT permet a tout un reseau prive de partager une seule adresse IP publique pour communiquer avec Internet.",
        'quiz_q1': "Pourquoi NAT est-il si important dans les reseaux d'aujourd'hui ?",
        'quiz_a1': "Parce que les adresses IPv4 publiques sont rares et limitees. Avec NAT, des milliers de reseaux prives utilisent les memes plages d'adresses privees (192.168.x.x) sans conflit sur Internet.",
        'quiz_q2': "Quelle est la difference entre NAT et PAT ?",
        'quiz_a2': "NAT traduit une IP privee en une IP publique (1 pour 1). PAT (ou NAT Overload) traduit plusieurs IP privees en UNE SEULE IP publique en utilisant des ports differents pour distinguer les connexions.",
    },

    # =========================================================================
    # BLOC 5 — Module 6 : Transport & logique + Module 7 : Stabilite & securite
    # Concepts 21 a 25 : TCP vs UDP, Modele OSI, STP, EtherChannel, ACL
    # =========================================================================

    {
        'title': 'TCP vs UDP',
        'module_number': 6,
        'module_name': 'Transport et logique',
        'level': 'intermediate',
        'icon': 'bi-send',
        'order': 1,
        'simple_explanation': (
            "TCP et UDP sont deux facons d'envoyer des donnees sur le reseau. "
            "Ils sont tres differents dans leur maniere de travailler.\n\n"
            "TCP, c'est l'envoie recommande : tu envoies un paquet, "
            "tu attends la confirmation que ca soit arrive, "
            "et si ca n'arrive pas tu renvoies. "
            "C'est fiable mais un peu plus lent.\n\n"
            "UDP, c'est l'envoie rapide : tu envoies et c'est tout. "
            "Tu ne verifies pas si ca arrive. "
            "C'est rapide mais sans garantie.\n\n"
            "Regle simple : quand l'exactitude est critique (un site web, un email), on utilise TCP. "
            "Quand la vitesse est plus importante que la perfection (une video live, un jeu), on utilise UDP."
        ),
        'concrete_example': (
            "TCP, c'est comme envoyer un colis avec suivi et signature.\n"
            "Le facteur livre, tu signes pour confirmer. "
            "Si personne ne repond, il repasse. Tu es sur de recevoir le colis.\n\n"
            "UDP, c'est comme distribuer des tracts dans les boites aux lettres.\n"
            "Tu glisses le tract et tu passes au suivant. "
            "Tu ne sais pas si quelqu'un l'a lu. C'est rapide mais sans garantie.\n\n"
            "Exemples reels :\n"
            "- TCP : naviguer sur un site web (HTTP), envoyer un email, telecharger un fichier\n"
            "- UDP : appel video (Zoom), jeu en ligne, streaming live, DNS"
        ),
        'technical_version': (
            "TCP (RFC 793) est un protocole oriente connexion avec handshake 3-way (SYN/SYN-ACK/ACK), "
            "controle de flux, retransmission et ordonnancement. "
            "UDP (RFC 768) est sans connexion, sans accusé de reception — faible overhead, latence minimale."
        ),
        'summary': "TCP garantit la livraison des donnees (fiable mais plus lent). UDP envoie sans verifier (rapide mais sans garantie).",
        'quiz_q1': "Pourquoi un appel video (Zoom) utilise UDP plutot que TCP ?",
        'quiz_a1': "Parce que la vitesse prime sur la perfection. Si une image est perdue, il vaut mieux continuer que s'arreter pour la retransmettre — ca causerait des coupures et des decalages dans la conversation.",
        'quiz_q2': "Qu'est-ce que le handshake 3-way de TCP ?",
        'quiz_a2': "C'est l'etablissement de connexion TCP en 3 etapes : SYN (je veux parler), SYN-ACK (ok, je suis la), ACK (parfait, on commence). Avant d'envoyer des donnees, les deux cotes se mettent d'accord.",
    },

    {
        'title': 'Le Modele OSI',
        'module_number': 6,
        'module_name': 'Transport et logique',
        'level': 'intermediate',
        'icon': 'bi-stack',
        'order': 2,
        'simple_explanation': (
            "Le modele OSI, c'est une facon d'organiser comment les reseaux fonctionnent "
            "en 7 couches superposees — comme les etages d'un immeuble.\n\n"
            "Chaque couche a un role precis et ne s'occupe que de son travail :\n\n"
            "Couche 7 - Application : ce que tu vois (le site web, l'email)\n"
            "Couche 6 - Presentation : le format et le chiffrement des donnees\n"
            "Couche 5 - Session : gere les conversations ouvertes\n"
            "Couche 4 - Transport : TCP ou UDP — livraison fiable ou rapide\n"
            "Couche 3 - Reseau : les adresses IP et le routage\n"
            "Couche 2 - Liaison : les adresses MAC et le switch\n"
            "Couche 1 - Physique : le cable, le signal electrique ou la lumiere\n\n"
            "En pratique, on parle surtout de L1, L2 et L3."
        ),
        'concrete_example': (
            "Imagine envoyer une lettre a l'etranger :\n\n"
            "L7 - Tu ecris la lettre (le message)\n"
            "L6 - Tu la traduis en anglais (le format)\n"
            "L5 - Tu ouvres une conversation avec ton correspondant\n"
            "L4 - Tu choisis la methode d'envoi : lettre recommandee (TCP) ou boite aux lettres (UDP)\n"
            "L3 - Tu ecris l'adresse complete du pays (adresse IP)\n"
            "L2 - Le facteur local connait les maisons de la rue (adresse MAC)\n"
            "L1 - Le camion qui transporte physiquement la lettre (le cable)\n\n"
            "Chaque couche fait son travail et passe le relai a la suivante."
        ),
        'technical_version': (
            "Le modele OSI (ISO 7498) decrit 7 couches d'abstraction. "
            "En pratique, le modele TCP/IP en utilise 4 (Application, Transport, Internet, Acces reseau). "
            "L1=bits, L2=trames, L3=paquets, L4=segments. "
            "Chaque couche encapsule les donnees de la couche superieure."
        ),
        'summary': "Le modele OSI decoupe le fonctionnement d'un reseau en 7 couches — chacune a un role precis, de la couche physique (cable) a l'application (le site web).",
        'quiz_q1': "A quelle couche OSI travaille un switch ? Et un routeur ?",
        'quiz_a1': "Le switch travaille en couche 2 (Liaison) avec les adresses MAC. Le routeur travaille en couche 3 (Reseau) avec les adresses IP. Un switch L3 travaille aux deux couches.",
        'quiz_q2': "Qu'est-ce que l'encapsulation dans le modele OSI ?",
        'quiz_a2': "C'est le fait d'emballer les donnees d'une couche dans celles de la couche inferieure. Ex : les donnees applicatives sont mises dans un segment TCP (L4), puis dans un paquet IP (L3), puis dans une trame Ethernet (L2).",
    },

    {
        'title': 'STP — Eviter les Boucles dans le Reseau',
        'module_number': 7,
        'module_name': 'Stabilite et securite',
        'level': 'intermediate',
        'icon': 'bi-shield-check',
        'order': 1,
        'simple_explanation': (
            "STP resout un probleme tres dangereux : les boucles dans les reseaux L2.\n\n"
            "Imagine que tu envoies un message en broadcast sur un reseau avec deux chemins entre deux switches. "
            "Le message arrive par le chemin A, repart par le chemin B, revient par A... "
            "et tourne en boucle pour toujours ! Ca bouche completement le reseau en quelques secondes. "
            "On appelle ca une 'tempete de broadcast'.\n\n"
            "STP (Spanning Tree Protocol) empeche ca intelligemment : "
            "il detecte les chemins redondants et en bloque UN. "
            "Si le chemin principal tombe en panne, STP debloque l'autre chemin automatiquement.\n\n"
            "Resultat : la redondance est preservee, mais sans boucle."
        ),
        'concrete_example': (
            "Imagine deux villes reliees par deux ponts.\n\n"
            "Sans STP : une voiture qui veut traverser passe le pont A, "
            "puis repasse le pont B, puis repasse le A... elle tourne indefiniment. "
            "Les ponts sont bloques, plus personne ne passe.\n\n"
            "Avec STP : le gestionnaire decide que le pont A est le principal et ferme le pont B. "
            "Tout le trafic passe par A. Si A s'effondre (panne), "
            "le gestionnaire ouvre automatiquement le pont B en 30 secondes.\n\n"
            "STP choisit le 'Root Bridge' — le switch central — et bloque les ports redondants."
        ),
        'technical_version': (
            "STP (IEEE 802.1D) elu un Root Bridge via le BID (Bridge ID = priorite + MAC). "
            "Il calcule les chemins les moins couteux vers le Root et bloque les ports redondants (BLK). "
            "RSTP (802.1w) converge en < 2s contre 30-50s pour STP classique."
        ),
        'summary': "STP empeche les boucles L2 en bloquant les liens redondants — et les reactivant automatiquement en cas de panne.",
        'quiz_q1': "Pourquoi une boucle L2 est-elle si dangereuse ?",
        'quiz_a1': "Elle cree une 'tempete de broadcast' : les messages circulent en boucle indefiniment, consomment toute la bande passante et paralysent completement le reseau en quelques secondes.",
        'quiz_q2': "Qu'est-ce que le Root Bridge dans STP ?",
        'quiz_a2': "C'est le switch central elu par STP autour duquel toute la topologie est calculee. Tous les autres switches cherchent le chemin le plus court vers lui. On choisit celui avec la priorite la plus basse (par defaut 32768).",
    },

    {
        'title': 'EtherChannel — Grouper des Cables pour Plus de Debit',
        'module_number': 7,
        'module_name': 'Stabilite et securite',
        'level': 'intermediate',
        'icon': 'bi-layout-three-columns',
        'order': 2,
        'simple_explanation': (
            "EtherChannel, c'est la technique qui regroupe plusieurs cables physiques "
            "en un seul gros lien logique.\n\n"
            "Imagine que tu veux deplacer des cartons d'une piece a une autre. "
            "Tu as 4 personnes disponibles. "
            "Tu peux les faire travailler chacun sur son propre chemin en meme temps.\n\n"
            "EtherChannel fait pareil : 4 cables de 1 Gbps groupes = 1 lien logique de 4 Gbps. "
            "Si un cable tombe en panne, les 3 autres continuent de fonctionner — "
            "la connexion ne coupe pas.\n\n"
            "Et STP voit tout ca comme UN SEUL lien — donc pas de boucle !"
        ),
        'concrete_example': (
            "Pour relier deux switches, tu as deux options :\n\n"
            "Option A : 1 cable de 1 Gbps. Rapide, mais si le cable casse : coupure totale.\n\n"
            "Option B : 4 cables de 1 Gbps en EtherChannel. "
            "Tu obtiens 4 Gbps de bande passante ET si un cable casse, "
            "les 3 autres prennent le relai sans interruption.\n\n"
            "Les protocoles de negociation s'appellent LACP (standard, recommande) "
            "et PAgP (Cisco uniquement). "
            "LACP fait se mettre d'accord les deux switches sur le groupement."
        ),
        'technical_version': (
            "EtherChannel (IEEE 802.3ad pour LACP) regroupe 2 a 8 interfaces physiques en un Port-Channel logique. "
            "STP voit le bundle comme un seul lien. "
            "La distribution du trafic se fait par hashing (MAC src/dst, IP src/dst selon la config)."
        ),
        'summary': "EtherChannel groupe plusieurs cables en un seul lien logique pour multiplier la bande passante et assurer la redondance sans boucle STP.",
        'quiz_q1': "Quels sont les deux avantages principaux de l'EtherChannel ?",
        'quiz_a1': "1. Plus de bande passante (agreger plusieurs liens). 2. Redondance : si un lien physique tombe, les autres continuent sans coupure de service.",
        'quiz_q2': "Pourquoi EtherChannel n'est-il pas bloque par STP ?",
        'quiz_a2': "Parce que STP voit l'ensemble des liens groupes comme UN SEUL lien logique (Port-Channel). Pour STP, il n'y a pas de redondance visible — donc pas de boucle possible.",
    },

    {
        'title': 'ACL — Les Listes de Controle d\'Acces',
        'module_number': 7,
        'module_name': 'Stabilite et securite',
        'level': 'intermediate',
        'icon': 'bi-funnel',
        'order': 3,
        'simple_explanation': (
            "Une ACL, c'est une liste de regles que le routeur suit pour decider "
            "si un message a le droit de passer ou doit etre bloque.\n\n"
            "C'est comme un videur a l'entree d'une boite de nuit qui a une liste :\n"
            "- 'Les gens de la rue des Roses : entrez'\n"
            "- 'Les gens de la rue du Danger : refus'\n"
            "- 'Tout le monde sinon : refus'\n\n"
            "Le routeur lit les regles une par une, du haut vers le bas. "
            "Des qu'une regle correspond, il applique l'action (autoriser ou bloquer) "
            "et s'arrete — il ne continue pas a lire les autres regles.\n\n"
            "A la fin de toute ACL, il y a toujours une regle invisible : 'deny all' — "
            "tout ce qui n'est pas autorise est bloque."
        ),
        'concrete_example': (
            "Dans une entreprise, on veut que :\n"
            "- Les employes (192.168.1.0/24) puissent aller sur Internet\n"
            "- Les stagiaires (192.168.2.0/24) ne puissent PAS aller sur Internet\n"
            "- Personne d'autre ne passe\n\n"
            "L'ACL sur le routeur ressemble a ca :\n"
            "Regle 1 : AUTORISER 192.168.1.0/24 -> n'importe ou\n"
            "Regle 2 : BLOQUER  192.168.2.0/24 -> n'importe ou\n"
            "(Regle invisible : BLOQUER tout le reste)\n\n"
            "L'ACL standard filtre uniquement par adresse source. "
            "L'ACL etendue peut filtrer par source, destination ET port (ex: bloquer uniquement le port 80 = HTTP)."
        ),
        'technical_version': (
            "Les ACL Cisco sont des listes ordonnees de ACEs (Access Control Entries) avec permit/deny. "
            "ACL standard (1-99) : filtre sur IP source uniquement. "
            "ACL etendue (100-199) : filtre sur IP src/dst, protocole, port. "
            "Appliquees sur une interface en 'in' ou 'out'. Implicit deny any any en fin de liste."
        ),
        'summary': "Une ACL est une liste de regles sur un routeur qui autorise ou bloque le trafic — comme un videur avec une liste a l'entree.",
        'quiz_q1': "Qu'est-ce que le 'implicit deny' a la fin d'une ACL ?",
        'quiz_a1': "C'est une regle invisible ajoutee automatiquement a la fin de toute ACL : 'deny any any'. Tout ce qui n'est pas explicitement autorise est bloque. C'est pourquoi il faut toujours verifier qu'on n'a pas oublie d'autoriser du trafic legitime.",
        'quiz_q2': "Quelle est la difference entre une ACL standard et une ACL etendue ?",
        'quiz_a2': "L'ACL standard filtre uniquement sur l'adresse IP source (moins precise). L'ACL etendue peut filtrer sur la source, la destination, le protocole (TCP/UDP/ICMP) et le numero de port — beaucoup plus fine et flexible.",
    },

    # =========================================================================
    # BLOC 6 — Module 8 : Niveau entreprise + debut Niveau Avance CCNP
    # Concepts 26 a 30 : OSPF, Troubleshooting, Routing avance, EIGRP, eBGP
    # =========================================================================

    {
        'title': 'OSPF — Le Protocole de Routage Dynamique',
        'module_number': 8,
        'module_name': 'Niveau entreprise',
        'level': 'intermediate',
        'icon': 'bi-broadcast',
        'order': 1,
        'simple_explanation': (
            "OSPF est un protocole qui permet aux routeurs de se parler entre eux "
            "pour apprendre automatiquement les routes du reseau.\n\n"
            "Sans OSPF, un administrateur doit entrer manuellement chaque route "
            "sur chaque routeur — et dans un grand reseau, ca devient vite impossible.\n\n"
            "Avec OSPF, les routeurs deviennent des amis :\n"
            "1. Ils se presentent en echangeant des messages Hello\n"
            "2. Ils se racontent tout ce qu'ils connaissent sur le reseau\n"
            "3. Chacun calcule les meilleurs chemins tout seul\n"
            "4. Si quelque chose change (panne, nouveau lien), ils se reprevenient "
            "et recalculent en quelques secondes."
        ),
        'concrete_example': (
            "Imagine 4 guides touristiques qui travaillent dans la meme ville.\n\n"
            "Chaque guide connait parfaitement son quartier. "
            "Chaque matin, ils se retrouvent et se partagent leurs connaissances : "
            "'La rue du Marche est fermee pour travaux', "
            "'Un nouveau raccourci vient d'ouvrir vers la gare'...\n\n"
            "Ainsi, chaque guide connait toute la ville et peut calculer le meilleur itineraire "
            "pour n'importe quelle destination.\n\n"
            "OSPF fait pareil : chaque routeur partage sa 'carte' (LSA — Link State Advertisement) "
            "avec ses voisins, jusqu'a ce que tout le monde ait la meme carte complete (LSDB)."
        ),
        'technical_version': (
            "OSPF (RFC 2328, RFC 5340 pour v3) est un protocole IGP Link-State qui utilise "
            "l'algorithme SPF (Dijkstra). Les routeurs echangent des LSAs et construisent une LSDB commune. "
            "Il supporte les areas hierarchiques (area 0 = backbone obligatoire)."
        ),
        'summary': "OSPF est un protocole de routage dynamique : les routeurs apprennent automatiquement toutes les routes du reseau en partageant leur carte entre voisins.",
        'quiz_q1': "Comment deux routeurs OSPF deviennent-ils voisins ?",
        'quiz_a1': "En echangeant des paquets Hello sur leurs interfaces. Pour devenir voisins (adjacence FULL), ils doivent avoir le meme area ID, le meme masque de sous-reseau et les memes timers Hello/Dead.",
        'quiz_q2': "Qu'est-ce qu'une LSA dans OSPF ?",
        'quiz_a2': "Une Link-State Advertisement — c'est la 'carte' qu'un routeur envoie a ses voisins pour leur dire quels reseaux il connait et via quels liens. Toutes les LSAs ensemble forment la LSDB (base de donnees topologique).",
    },

    {
        'title': 'Troubleshooting — Trouver la Panne',
        'module_number': 8,
        'module_name': 'Niveau entreprise',
        'level': 'intermediate',
        'icon': 'bi-bug',
        'order': 2,
        'simple_explanation': (
            "Le troubleshooting, c'est la methodologie pour trouver et resoudre les pannes reseau.\n\n"
            "Un bon technicien ne touche pas au hasard en esperant que ca marche. "
            "Il suit une methode logique, couche par couche :\n\n"
            "Etape 1 : Definir le probleme — qu'est-ce qui ne marche pas exactement ?\n"
            "Etape 2 : Commencer par le bas (couche 1) — le cable est-il branche ?\n"
            "Etape 3 : Remonter les couches — L2 (MAC), L3 (IP), L4 (port), L7 (application)\n"
            "Etape 4 : Tester a chaque etape — ping, traceroute, show commands\n"
            "Etape 5 : Corriger et verifier que tout fonctionne\n\n"
            "La methode Top-Down commence par l'application et descend. "
            "Bottom-Up commence par le cable. Les deux sont valides."
        ),
        'concrete_example': (
            "Tu ne peux plus acceder a un site web. Par ou commencer ?\n\n"
            "L1 : Le cable est branche ? Le port du switch est-il vert ?\n"
            "L2 : Le switch voit-il l'adresse MAC de ton PC ? (show mac address-table)\n"
            "L3 : Ton PC a-t-il une adresse IP ? Ping vers la passerelle fonctionne ?\n"
            "L4 : Le port 443 (HTTPS) est-il ouvert vers le serveur ?\n"
            "L7 : Le navigateur a-t-il un certificat expire ou un proxy mal configure ?\n\n"
            "En suivant cette methode, tu trouves la panne en 5 minutes "
            "au lieu de passer 2 heures a tout verifier dans le desordre."
        ),
        'technical_version': (
            "Le troubleshooting methodique s'appuie sur le modele OSI (bottom-up ou top-down). "
            "Outils cles : ping (L3), traceroute (L3 hop-by-hop), show interfaces (L1/L2), "
            "show ip route (L3), show running-config, debug (dernier recours en production)."
        ),
        'summary': "Le troubleshooting est une methode systematique couche par couche pour identifier et corriger rapidement les pannes reseau.",
        'quiz_q1': "Pourquoi commencer le troubleshooting par la couche 1 (physique) ?",
        'quiz_a1': "Parce que c'est la base : si le cable est debranche ou casse, rien d'autre ne peut fonctionner. Inutile de chercher une panne de routage si le lien physique est mort. On va du plus simple au plus complexe.",
        'quiz_q2': "A quoi sert la commande 'traceroute' dans le troubleshooting ?",
        'quiz_a2': "Elle montre le chemin exact qu'emprunte un paquet hop par hop (routeur par routeur) vers la destination. Elle permet d'identifier exactement a quel routeur le trafic s'arrete ou prend un mauvais chemin.",
    },

    {
        'title': 'Routing Avance — Redistribution et Politique de Routage',
        'module_number': 9,
        'module_name': 'Niveau Avance CCNP',
        'level': 'advanced',
        'icon': 'bi-signpost-2',
        'order': 1,
        'simple_explanation': (
            "Dans les grands reseaux, plusieurs protocoles de routage coexistent parfois. "
            "Il faut alors les faire se parler — c'est la redistribution.\n\n"
            "Imagine deux entreprises qui fusionnent. "
            "L'une utilisait OSPF, l'autre EIGRP. "
            "Pour que tout le monde se voie, un routeur frontiere apprend les routes OSPF "
            "et les 'traduit' en routes EIGRP — et vice versa. Ce routeur fait de la redistribution.\n\n"
            "La politique de routage (route-map, prefix-list), c'est les regles qu'on pose "
            "pour decider QUELLES routes redistribuer, avec quelle metrique, "
            "et lesquelles ignorer. C'est le niveau avance du controle du trafic."
        ),
        'concrete_example': (
            "Imagine un grand pays avec deux systemes postaux : La Poste (OSPF) et DHL (EIGRP).\n\n"
            "Un centre de tri frontiere (routeur de redistribution) recoit les colis La Poste "
            "et les reexpedie via DHL — et inversement.\n\n"
            "Mais il a des regles : il ne redistribue pas les colis fragiles (certaines routes sensibles), "
            "et il marque les colis redistribues avec un code special (tag) "
            "pour eviter qu'ils reviennent dans l'autre sens et creent une boucle.\n\n"
            "En Cisco : 'redistribute ospf 1 into eigrp 100 metric 1000 100 255 1 1500' "
            "traduit les routes OSPF en routes EIGRP avec une metrique definie."
        ),
        'technical_version': (
            "La redistribution injecte des routes d'un protocole (source) dans un autre (cible) "
            "via le routeur ASBR/frontiere. Les route-maps et prefix-lists filtrent et taggent "
            "les routes pour eviter les boucles de redistribution (deny les routes taggees en retour)."
        ),
        'summary': "La redistribution permet de faire communiquer deux protocoles de routage differents via un routeur frontiere — avec des filtres pour eviter les boucles.",
        'quiz_q1': "Pourquoi faut-il taguer les routes lors d'une redistribution bidirectionnelle ?",
        'quiz_a1': "Pour eviter les boucles de redistribution. Sans tag, une route OSPF redistribuee dans EIGRP pourrait etre redistribuee a nouveau dans OSPF — et tourner en boucle indefiniment en perturbant tout le routage.",
        'quiz_q2': "Qu'est-ce qu'une route-map dans le contexte de la redistribution ?",
        'quiz_a2': "C'est un outil de filtrage et de modification des routes. Elle permet de choisir quelles routes redistribuer (match), de modifier leurs attributs (set metrique, tag, local-pref) et d'en bloquer certaines.",
    },

    {
        'title': 'EIGRP — Le Protocole de Routage Cisco',
        'module_number': 9,
        'module_name': 'Niveau Avance CCNP',
        'level': 'advanced',
        'icon': 'bi-diagram-3',
        'order': 2,
        'simple_explanation': (
            "EIGRP est un protocole de routage dynamique cree par Cisco. "
            "Il est plus rapide a converger qu'OSPF et plus simple a configurer dans les petits reseaux.\n\n"
            "Ce qui rend EIGRP special, c'est l'algorithme DUAL :\n\n"
            "Chaque routeur connait non seulement le meilleur chemin (le Successor), "
            "mais aussi un chemin de secours deja calcule (le Feasible Successor). "
            "En cas de panne, le routeur bascule immediatement sur le chemin de secours "
            "sans avoir besoin de recalculer — quasi-instantane !\n\n"
            "EIGRP utilise 5 parametres pour calculer sa metrique : "
            "la bande passante, le delai, la fiabilite, la charge et le MTU."
        ),
        'concrete_example': (
            "Imagine que tu conduis vers le travail.\n\n"
            "Tu as un itineraire principal (Successor) : l'autoroute A6 — 20 minutes.\n"
            "Tu as aussi un itineraire de secours deja connu (Feasible Successor) : la nationale N7 — 35 minutes.\n\n"
            "Si l'autoroute est bouchee (panne du lien), "
            "tu prends immediatement la N7 sans sortir la carte et recalculer. "
            "Tu pars en 2 secondes au lieu de 30 secondes.\n\n"
            "OSPF dans ce cas devrait recalculer toute la carte de la ville (algorithme SPF). "
            "EIGRP, lui, a deja la solution de secours en memoire — convergence ultrarapide."
        ),
        'technical_version': (
            "EIGRP (RFC 7868) utilise l'algorithme DUAL (Diffusing Update Algorithm). "
            "Il maintient une table de topologie avec Successor (FD minimale) "
            "et Feasible Successor (RD < FD du Successor). "
            "Metrique composite : principalement bande passante et delai par defaut."
        ),
        'summary': "EIGRP est le protocole de routage Cisco avec convergence ultra-rapide grace a l'algorithme DUAL qui precalcule un chemin de secours pret a l'emploi.",
        'quiz_q1': "Qu'est-ce qu'un Feasible Successor dans EIGRP ?",
        'quiz_a1': "C'est un chemin de secours deja calcule et valide, pret a etre utilise instantanement si le chemin principal (Successor) tombe en panne. Il doit avoir une distance rapportee (RD) inferieure a la distance feasible (FD) du Successor.",
        'quiz_q2': "Pourquoi EIGRP converge plus vite qu'OSPF apres une panne ?",
        'quiz_a2': "Parce qu'EIGRP a deja un chemin de secours (Feasible Successor) precalcule. Il bascule dessus instantanement. OSPF doit d'abord diffuser les LSAs a tous les routeurs, puis recalculer l'algorithme SPF — ce qui prend plus de temps.",
    },

    {
        'title': 'eBGP — Le Protocole de Routage d\'Internet',
        'module_number': 9,
        'module_name': 'Niveau Avance CCNP',
        'level': 'advanced',
        'icon': 'bi-globe2',
        'order': 3,
        'simple_explanation': (
            "BGP est LE protocole qui fait fonctionner Internet. "
            "Tous les grands operateurs du monde (Orange, Google, Amazon...) "
            "utilisent BGP pour echanger leurs routes.\n\n"
            "eBGP (external BGP) connecte des reseaux appartenant a des organisations differentes "
            "(des AS — Autonomous Systems). Chaque organisation a son propre numero d'AS.\n\n"
            "La grande force de BGP : on peut decider precisement QUELLES routes on accepte "
            "et QUELLES routes on annonce. "
            "BGP ne cherche pas le chemin le plus court comme OSPF — "
            "il choisit le chemin selon des politiques decidees par les administrateurs.\n\n"
            "C'est un protocole de politique, pas juste de performance."
        ),
        'concrete_example': (
            "Imagine les grandes villes du monde reliees par des autoroutes internationales.\n\n"
            "Chaque pays (AS) gere ses propres routes interieures (OSPF/EIGRP). "
            "BGP, c'est les accords diplomatiques entre pays : "
            "'Tu peux faire passer ton trafic par mon territoire, "
            "mais seulement vers ces destinations, pas d'autres.'\n\n"
            "Orange (AS 5511) annonce a SFR (AS 15557) : "
            "'Je peux atteindre le reseau 82.64.0.0/11 par ici.'\n"
            "SFR repond : 'Ok, je t'envoie le trafic destine a ces adresses.'\n\n"
            "C'est exactement comme ca qu'Internet route les milliards de paquets "
            "qui traversent la planete chaque seconde."
        ),
        'technical_version': (
            "eBGP (RFC 4271) est un EGP (Exterior Gateway Protocol) base sur des sessions TCP (port 179). "
            "Il echange des prefixes IP avec des attributs (AS-Path, Next-Hop, Local-Pref, MED, Communities). "
            "La selection du meilleur chemin suit 13 criteres ordonnés (Weight > Local-Pref > AS-Path > ...)."
        ),
        'summary': "eBGP est le protocole qui connecte les grands reseaux d'Internet entre eux — chaque organisation choisit quelles routes accepter et annoncer selon ses politiques.",
        'quiz_q1': "Quelle est la difference fondamentale entre BGP et OSPF/EIGRP ?",
        'quiz_a1': "OSPF et EIGRP cherchent le chemin le plus court/rapide (metrique technique). BGP choisit le chemin selon des politiques : accords commerciaux, securite, preference d'operateur. C'est un protocole de politique, pas de performance.",
        'quiz_q2': "Qu'est-ce qu'un AS (Autonomous System) dans le contexte BGP ?",
        'quiz_a2': "Un AS est un ensemble de reseaux sous le meme controle administratif (une entreprise, un FAI, un cloud provider) avec un numero unique attribue par l'IANA. Ex : Google = AS 15169, Cloudflare = AS 13335. BGP interconnecte ces AS entre eux.",
    },

    # =========================================================================
    # BLOC 7 — Module 9 CCNP (suite) : concepts 31 a 35
    # BGP Neighbor, BGP Attributes, OSPF DR/BDR, Redistribution, PBR
    # =========================================================================

    {
        'title': 'BGP Neighbor — Les Voisins BGP',
        'module_number': 9,
        'module_name': 'CCNP Avance',
        'level': 'advanced',
        'icon': 'bi-people',
        'order': 6,
        'simple_explanation': (
            "Un 'BGP neighbor' (ou 'BGP peer'), c'est un routeur avec qui ton routeur a conclu "
            "un accord pour echanger des informations de routage.\n\n"
            "Contrairement a OSPF qui trouve ses voisins tout seul, BGP ne decouvre rien "
            "automatiquement — tu dois dire manuellement a ton routeur :\n"
            "'L'adresse de mon voisin est 10.0.0.1 et il appartient a l'AS 65001'.\n\n"
            "Une fois la relation etablie (session TCP port 179), les deux routeurs s'envoient "
            "leurs tables de routage completes. Si la connexion tombe, BGP retire toutes les "
            "routes apprises par ce voisin — c'est pourquoi la stabilite des sessions BGP est critique."
        ),
        'concrete_example': (
            "Imagine deux operateurs telecom : Orange et SFR.\n\n"
            "Orange ne peut pas envoyer automatiquement ses clients vers SFR sans accord. "
            "Ils signent un contrat de peering (interconnexion), configurent leurs routeurs "
            "de bordure pour se 'connaitre' mutuellement, et commencent a s'echanger "
            "leurs routes.\n\n"
            "Routeur Orange dit a son BGP :\n"
            "'Mon voisin est 195.10.0.1 (SFR), AS 5410'\n\n"
            "Routeur SFR dit :\n"
            "'Mon voisin est 194.20.0.1 (Orange), AS 3215'\n\n"
            "Une session BGP s'etablit. Orange annonce ses blocs IP. SFR annonce les siens. "
            "Les clients de chaque operateur peuvent maintenant joindre l'autre."
        ),
        'technical_version': (
            "BGP utilise TCP port 179 pour etablir des sessions entre peers. "
            "eBGP (external BGP) : voisins dans des AS differents, TTL=1 par defaut. "
            "iBGP (internal BGP) : voisins dans le meme AS, TTL=255. "
            "Commande : 'neighbor X.X.X.X remote-as YYYY'. "
            "Etats BGP : Idle -> Connect -> Active -> OpenSent -> OpenConfirm -> Established. "
            "La session Established est le seul etat ou les routes sont echangees."
        ),
        'summary': "Un BGP neighbor est un routeur partenaire configure manuellement pour echanger des routes BGP via une session TCP — contrairement a OSPF, rien n'est automatique.",
        'quiz_q1': "Pourquoi BGP ne decouvre-t-il pas ses voisins automatiquement comme OSPF ?",
        'quiz_a1': "BGP est un protocole inter-operateurs qui necessite des accords commerciaux et de securite explicites. On ne peut pas permettre a n'importe qui de devenir voisin et d'injecter des routes. Chaque session est configuree manuellement avec l'AS du voisin pour garantir que c'est bien le bon partenaire.",
        'quiz_q2': "Quelle est la difference entre eBGP et iBGP ?",
        'quiz_a2': "eBGP (external BGP) : session entre routeurs de deux AS differents — typiquement entre deux operateurs differents. iBGP (internal BGP) : session entre routeurs du meme AS — pour distribuer les routes BGP en interne. iBGP necessite soit un full-mesh soit des Route Reflectors car il ne re-annonce pas les routes apprises d'iBGP a d'autres pairs iBGP.",
    },

    {
        'title': 'BGP Attributes — Choisir le Meilleur Chemin',
        'module_number': 9,
        'module_name': 'CCNP Avance',
        'level': 'advanced',
        'icon': 'bi-sliders',
        'order': 7,
        'simple_explanation': (
            "BGP peut recevoir plusieurs chemins pour atteindre la meme destination. "
            "Pour choisir le meilleur, il utilise des 'attributs' — des criteres de selection "
            "qu'on peut manipuler.\n\n"
            "C'est comme choisir un vol Paris-New York :\n"
            "- Certains ont une escale (AS_PATH long = moins prefere)\n"
            "- Tu preferes peut-etre une compagnie en particulier (LOCAL_PREF)\n"
            "- L'autre compagnie propose un prix plus bas (MED plus faible = prefere)\n\n"
            "BGP evalue ces attributs dans un ordre precis jusqu'a trouver un gagnant."
        ),
        'concrete_example': (
            "Ton routeur recoit 3 chemins vers Google (8.8.8.8) :\n\n"
            "Chemin A via Telecom1 : LOCAL_PREF=200, AS_PATH= AS65001 AS15169\n"
            "Chemin B via Telecom2 : LOCAL_PREF=100, AS_PATH= AS65002 AS15169\n"
            "Chemin C via Telecom3 : LOCAL_PREF=200, AS_PATH= AS65003 AS15169\n\n"
            "Etape 1 : LOCAL_PREF le plus ELEVE gagne -> A et C a 200 (B elimine)\n"
            "Etape 2 : AS_PATH le plus COURT entre A et C -> meme longueur (2 AS)\n"
            "Etape 3 : ORIGIN code, MED, eBGP > iBGP, IGP metric...\n"
            "Etape 4 : Router-ID le plus BAS -> A gagne si son Router-ID < C\n\n"
            "Resultat : Chemin A est selectionne et installe dans la table de routage."
        ),
        'technical_version': (
            "Ordre de selection BGP (best path selection algorithm) — mnemo 'We Love Oranges AS Oranges Mean Pure Refreshment' : "
            "Weight (Cisco, local) > LOCAL_PREF (plus haut = mieux) > Locally originated > AS_PATH length (plus court = mieux) > "
            "ORIGIN (IGP < EGP < Incomplete) > MED (plus bas = mieux) > eBGP > iBGP > IGP metric > Router-ID (plus bas = mieux). "
            "LOCAL_PREF est l'attribut le plus utilise pour controler le trafic sortant. "
            "AS_PATH prepending est utilise pour rendre un chemin moins attractif."
        ),
        'summary': "Les attributs BGP (LOCAL_PREF, AS_PATH, MED...) sont des criteres evalues dans un ordre precis pour determiner le meilleur chemin vers une destination.",
        'quiz_q1': "Quel attribut BGP est le plus souvent utilise pour controler quel lien WAN sortant est prefere ?",
        'quiz_a1': "LOCAL_PREF (Local Preference). Plus la valeur est ELEVEE, plus le chemin est prefere. On le modifie en 'in' sur les sessions iBGP. Exemple : si tu as deux FAI, tu mets LOCAL_PREF=200 sur les routes du FAI principal et LOCAL_PREF=100 sur le FAI de backup — tout le trafic sortant preferera le FAI principal.",
        'quiz_q2': "A quoi sert l'AS_PATH prepending ?",
        'quiz_a2': "A rendre un chemin BGP moins attractif pour les autres AS. Tu ajoutes artificiellement ton propre AS plusieurs fois dans l'AS_PATH (ex: 65001 65001 65001), ce qui allonge le chemin. Les autres AS preferent les chemins courts, donc ils eviteront ce chemin. Utile pour forcer le trafic entrant a arriver par un lien specifique.",
    },

    {
        'title': 'OSPF Avance — DR et BDR',
        'module_number': 9,
        'module_name': 'CCNP Avance',
        'level': 'advanced',
        'icon': 'bi-broadcast-pin',
        'order': 8,
        'simple_explanation': (
            "Quand plusieurs routeurs OSPF sont sur le meme reseau (ex: un switch avec 10 routeurs), "
            "sans organisation ca fait un chaos d'echanges : chaque routeur parle a tous les autres.\n\n"
            "Pour eviter ca, OSPF elu un chef : le DR (Designated Router). "
            "Et un vice-chef : le BDR (Backup Designated Router).\n\n"
            "Tous les autres routeurs ne parlent QU'au DR. Le DR centralise et redistribue "
            "l'information a tout le monde. Resultat : beaucoup moins de messages, "
            "reseau plus stable.\n\n"
            "Si le DR tombe, le BDR prend sa place automatiquement."
        ),
        'concrete_example': (
            "Imagine une reunion de 10 employes. Sans chef, tout le monde parle en meme temps — c'est le chaos.\n\n"
            "Avec un chef (DR) et un vice-chef (BDR) :\n"
            "- Chaque employe communique UNIQUEMENT avec le chef\n"
            "- Le chef centralise toutes les infos et les redistribue a tout le monde\n"
            "- Si le chef tombe malade, le vice-chef prend la releve immediatement\n\n"
            "En OSPF, l'election se fait par priorite (0-255, plus haute gagne). "
            "A priorite egale, le Router-ID le plus eleve gagne.\n\n"
            "Attention : l'election n'a lieu QUE sur les reseaux multi-acces (Ethernet). "
            "Sur les liens point-a-point, il n'y a pas de DR/BDR."
        ),
        'technical_version': (
            "DR/BDR election sur reseaux broadcast multi-access (type Ethernet). "
            "Priorite OSPF : 0-255 (defaut 1), priorite 0 = ne participe pas a l'election. "
            "Router-ID : IP la plus haute ou loopback configuree. "
            "Les autres routeurs sont des DROTHER — ils envoient leurs LSA en multicast 224.0.0.6 (AllDR). "
            "DR/BDR envoient leurs LSA en multicast 224.0.0.5 (AllSPF). "
            "Commande : 'ip ospf priority X'. L'election est non-preemptive : changer la priorite "
            "apres l'election ne change pas le DR tant que celui-ci ne tombe pas."
        ),
        'summary': "Sur un reseau multi-acces, OSPF elu un DR (Designated Router) pour centraliser les echanges et reduire le trafic — les autres routeurs ne parlent qu'au DR.",
        'quiz_q1': "Pourquoi OSPF a-t-il besoin d'un DR sur un reseau Ethernet ?",
        'quiz_a1': "Sans DR, chaque routeur formerait une adjacence avec tous les autres. Sur un reseau avec N routeurs, ca ferait N*(N-1)/2 adjacences et autant d'echanges LSA. Avec un DR, chaque routeur n'a qu'une adjacence avec le DR (et une avec le BDR) — les echanges sont centralises et le nombre de messages est drastiquement reduit.",
        'quiz_q2': "Comment forcer un routeur a devenir DR ?",
        'quiz_a2': "En augmentant sa priorite OSPF avec 'ip ospf priority 255' sur l'interface concernee. La valeur maximale est 255, la valeur 0 empeche de participer a l'election. Attention : l'election est non-preemptive — si un DR est deja elu, changer la priorite n'a d'effet qu'au prochain demarrage du reseau ou crash du DR actuel.",
    },

    {
        'title': 'Redistribution de Routes',
        'module_number': 9,
        'module_name': 'CCNP Avance',
        'level': 'advanced',
        'icon': 'bi-arrow-left-right',
        'order': 9,
        'simple_explanation': (
            "La redistribution, c'est le fait de 'traduire' des routes d'un protocole "
            "de routage vers un autre.\n\n"
            "Imagine que tu as deux groupes dans ton reseau :\n"
            "- Le groupe A parle OSPF (comme parler francais)\n"
            "- Le groupe B parle EIGRP (comme parler anglais)\n\n"
            "Sans redistribution, les deux groupes ne peuvent pas se parler — "
            "ils ne se comprennent pas.\n\n"
            "Avec la redistribution, un routeur 'bilingue' (le routeur de redistribution) "
            "traduit les routes OSPF en routes EIGRP et vice-versa. "
            "Tout le monde peut maintenant se joindre."
        ),
        'concrete_example': (
            "Scenario reel : une fusion d'entreprises.\n\n"
            "Entreprise A (rachetee) utilise OSPF depuis 10 ans.\n"
            "Entreprise B (racheteur) utilise EIGRP.\n\n"
            "On ne peut pas tout migrer en une nuit. Alors on configure la redistribution "
            "sur le routeur de bordure entre les deux reseaux :\n\n"
            "router ospf 1\n"
            "  redistribute eigrp 100 subnets  <- Les routes EIGRP entrent dans OSPF\n\n"
            "router eigrp 100\n"
            "  redistribute ospf 1 metric 1000 100 255 1 1500  <- Routes OSPF entrent dans EIGRP\n\n"
            "Maintenant les employes des deux entreprises peuvent se joindre mutuellement, "
            "meme avec des protocoles differents."
        ),
        'technical_version': (
            "La redistribution injecte des routes externes dans un domaine de routage avec une metrique seed. "
            "Risque majeur : les boucles de routage (routing loops) et le suboptimal routing. "
            "Pour eviter les boucles en redistribution bidirectionnelle : utiliser des route-maps avec tags. "
            "Route-map avec tag : taguer les routes redistribuees d'OSPF vers EIGRP avec tag 10, "
            "puis filtrer ce tag lors de la redistribution EIGRP -> OSPF. "
            "Administrative Distance : OSPF=110, EIGRP=90/170 (interne/externe). "
            "Les routes redistribuees apparaissent comme routes externes (E2 dans OSPF, D EX dans EIGRP)."
        ),
        'summary': "La redistribution permet a deux protocoles de routage differents de s'echanger leurs routes via un routeur 'traducteur' — indispensable lors de fusions ou migrations.",
        'quiz_q1': "Quel est le principal risque de la redistribution bidirectionnelle entre deux protocoles ?",
        'quiz_a1': "Les boucles de routage. Si on redistribue OSPF -> EIGRP et EIGRP -> OSPF sans precaution, une route peut etre exportee d'OSPF vers EIGRP, puis re-importee d'EIGRP vers OSPF comme route externe — parfois avec une metrique meilleure que l'originale. La solution classique est de taguer les routes redistribuees et de filtrer ces tags lors de la redistribution inverse.",
        'quiz_q2': "Comment les routes redistribuees apparaissent-elles dans la table de routage OSPF ?",
        'quiz_a2': "Elles apparaissent comme routes externes OSPF de type E2 (External Type 2) par defaut, avec le code 'O E2' dans 'show ip route'. Contrairement aux routes internes OSPF, le cout d'une route E2 ne change pas en traversant le domaine OSPF — il reste celui defini au point de redistribution. Les routes E1 (moins courantes) ajoutent le cout interne en plus.",
    },

    {
        'title': 'PBR — Policy-Based Routing',
        'module_number': 9,
        'module_name': 'CCNP Avance',
        'level': 'advanced',
        'icon': 'bi-signpost-split',
        'order': 10,
        'simple_explanation': (
            "Normalement, un routeur envoie les paquets selon sa table de routage : "
            "il regarde juste l'adresse de destination et choisit la sortie.\n\n"
            "PBR (Policy-Based Routing) brise cette regle. Il permet de dire :\n"
            "'Ce paquet vient de tel utilisateur, ou utilise tel port, ou a telle taille — "
            "alors IGNORE la table de routage normale et envoie-le par CE chemin special.'\n\n"
            "C'est comme avoir un GPS qui suit des regles personnalisees :\n"
            "- Les camions prennent l'autoroute (lien haut debit)\n"
            "- Les voitures prennent la nationale (lien bas cout)\n"
            "Meme destination, routes differentes selon le type de vehicule."
        ),
        'concrete_example': (
            "Scenario : une entreprise a deux liens WAN.\n"
            "- Lien A : fibre 1 Gbps, cher -> reserve aux serveurs et applications critiques\n"
            "- Lien B : ADSL 20 Mbps, pas cher -> navigation web des employes\n\n"
            "Avec la table de routage normale, tous les paquets prendraient le meme chemin. "
            "Avec PBR, on configure des regles :\n\n"
            "Regle 1 : Si source = serveurs (10.0.10.0/24) -> sortir par Lien A\n"
            "Regle 2 : Si port destination = 80/443 (HTTP/HTTPS) et source = employes -> sortir par Lien B\n"
            "Regle 3 : Tout le reste -> table de routage normale\n\n"
            "Les serveurs ont toujours la fibre. Les employes naviguent sur l'ADSL. "
            "Optimisation des couts sans changer la topologie."
        ),
        'technical_version': (
            "PBR s'implemente via route-map appliquee sur une interface en 'ip policy route-map NOM'. "
            "La route-map utilise des match (acl, length, tos) et des set (ip next-hop, ip interface, default next-hop). "
            "Ordre d'evaluation : PBR est verifie AVANT la table de routage. "
            "Si le paquet matche, il suit le PBR. S'il ne matche pas, la table de routage normale s'applique. "
            "'set ip next-hop' force un next-hop meme si une meilleure route existe. "
            "'set ip default next-hop' s'applique seulement si aucune route specifique n'existe. "
            "PBR local (sur paquets generes par le routeur lui-meme) : 'ip local policy route-map NOM'."
        ),
        'summary': "PBR permet de forcer certains paquets a prendre une route specifique independamment de la table de routage — base sur la source, le port, ou d'autres criteres de politique.",
        'quiz_q1': "Quelle est la difference fondamentale entre le routage normal et PBR ?",
        'quiz_a1': "Le routage normal se base UNIQUEMENT sur l'adresse IP de destination. PBR peut se baser sur n'importe quel critere : adresse source, protocole, port, taille du paquet, TOS/DSCP... PBR est evalue en PREMIER, avant la table de routage. Si un paquet matche une regle PBR, il prend le chemin defini sans consulter la table de routage.",
        'quiz_q2': "Quelle est la difference entre 'set ip next-hop' et 'set ip default next-hop' dans un PBR ?",
        'quiz_a2': "'set ip next-hop' force le prochain saut MEME si la table de routage a une route plus specifique vers la destination. 'set ip default next-hop' n'est utilise que si la table de routage n'a PAS de route pour la destination (comme une route par defaut de secours). En pratique, 'set ip next-hop' est plus contraignant et 'set ip default next-hop' est plus souple.",
    },

    # =========================================================================
    # BLOC 8 — Module 10 : Haute disponibilite et securite avancee
    # Concepts 36 a 40 : EtherChannel L3, HSRP, DHCP Snooping, PortFast/BPDU Guard, Root/Loop Guard
    # =========================================================================

    {
        'title': 'EtherChannel Layer 3 — Agregation de Liens Routed',
        'module_number': 10,
        'module_name': 'Haute disponibilite',
        'level': 'advanced',
        'icon': 'bi-diagram-2',
        'order': 1,
        'simple_explanation': (
            "Un EtherChannel Layer 3 c'est comme un EtherChannel normal — plusieurs cables "
            "physiques fondes en un seul lien logique — mais au lieu d'etre un lien de switch "
            "(couche 2), c'est un lien de routeur avec une adresse IP dessus.\n\n"
            "L'avantage : pas besoin de STP sur ce lien (STP ne joue que sur la couche 2). "
            "Pas de port bloque, tout le debit est utilise, et si un cable tombe, "
            "les autres compensent sans interruption.\n\n"
            "C'est la solution privilegiee entre deux routeurs ou entre un routeur et un switch "
            "de distribution quand on veut redondance + bande passante maximale."
        ),
        'concrete_example': (
            "Dans un datacenter, le routeur de coeur est connecte au switch de distribution "
            "avec 4 liens de 1 Gbps chacun.\n\n"
            "Solution Layer 2 EtherChannel : on regroupe les 4 liens en un port-channel, "
            "mais STP bloque toujours les boucles et un lien peut etre en standby.\n\n"
            "Solution Layer 3 EtherChannel : on configure le port-channel comme interface routee "
            "(no switchport + ip address) :\n\n"
            "interface port-channel 1\n"
            "  no switchport\n"
            "  ip address 10.0.0.1 255.255.255.252\n\n"
            "Resultat : 4 Gbps effectifs, aucun blocage STP, routage direct. "
            "Si un lien tombe, LACP redistribue immediatement le trafic sur les 3 restants."
        ),
        'technical_version': (
            "EtherChannel L3 (routed port-channel) : interface port-channel configuree avec 'no switchport' + adresse IP. "
            "Protocoles de negotiation : LACP (802.3ad, ouvert) ou PAgP (Cisco proprietaire). "
            "LACP modes : active/active ou active/passive. PAgP modes : desirable/desirable ou desirable/auto. "
            "Load balancing : src-mac, dst-mac, src-dst-mac, src-ip, dst-ip, src-dst-ip (selon plateforme). "
            "Commande verification : 'show etherchannel summary' — chercher le flag 'P' (port en port-channel) "
            "et 'RU' (routed, in use) sur le port-channel."
        ),
        'summary': "EtherChannel L3 agrege plusieurs liens physiques en un seul lien routed avec IP — cumul de bande passante, redondance, sans intervention STP.",
        'quiz_q1': "Quelle est la difference entre un EtherChannel Layer 2 et un EtherChannel Layer 3 ?",
        'quiz_a1': "EtherChannel L2 : le port-channel est un lien de commutation (trunk ou access), STP s'applique. EtherChannel L3 : le port-channel a l'option 'no switchport' et une adresse IP — c'est un lien routed. STP ne s'applique pas dessus, tout le debit est actif, et c'est utilise entre equipements de routage (core <-> distribution par exemple).",
        'quiz_q2': "Quels sont les deux protocoles de negotiation EtherChannel et leurs modes actifs ?",
        'quiz_a2': "LACP (802.3ad, standard ouvert) : modes 'active' (initie la negotiation) et 'passive' (attend). Pour que ca marche : au moins un cote en 'active'. PAgP (Cisco proprietaire) : modes 'desirable' (initie) et 'auto' (attend). Pour que ca marche : au moins un cote en 'desirable'. LACP est prefere car interoperable avec des equipements non-Cisco.",
    },

    {
        'title': 'HSRP — Passerelle par Defaut Redondante',
        'module_number': 10,
        'module_name': 'Haute disponibilite',
        'level': 'advanced',
        'icon': 'bi-shield-check',
        'order': 2,
        'simple_explanation': (
            "Les PCs d'un reseau ont besoin d'une passerelle par defaut (le routeur) "
            "pour acceder a Internet. Mais que se passe-t-il si ce routeur tombe ?\n\n"
            "Sans HSRP : toutes les machines perdent Internet jusqu'a ce qu'un admin reconfigure "
            "manuellement une nouvelle passerelle sur chaque PC.\n\n"
            "Avec HSRP : deux routeurs partagent une meme 'adresse IP virtuelle'. "
            "Les PCs pointent vers cette IP virtuelle. En coulisse :\n"
            "- Routeur A est ACTIF (il repond a cette IP)\n"
            "- Routeur B est en STANDBY (il surveille A)\n"
            "Si A tombe, B devient actif et prend l'IP virtuelle en moins de 10 secondes. "
            "Les PCs ne se rendent compte de rien."
        ),
        'concrete_example': (
            "Reseau entreprise : les PCs ont pour passerelle 192.168.1.1\n\n"
            "Routeur A : 192.168.1.2 (vraie IP) + priorite HSRP 110\n"
            "Routeur B : 192.168.1.3 (vraie IP) + priorite HSRP 100\n"
            "IP virtuelle HSRP : 192.168.1.1 (la passerelle des PCs)\n\n"
            "Etat normal : Routeur A est ACTIVE (priorite la plus haute), il repond au .1\n"
            "Routeur B est STANDBY, il envoie des messages 'hello' a A toutes les 3 secondes\n\n"
            "Routeur A tombe :\n"
            "Routeur B ne recoit plus de hello -> attente du hold timer (10 sec) -> "
            "Routeur B devient ACTIVE et prend l'IP .1\n\n"
            "Les PCs continuent d'envoyer leurs paquets vers .1 — ils ne voient aucune coupure (ou une coupure de 10 sec max)."
        ),
        'technical_version': (
            "HSRP (Hot Standby Router Protocol) : protocole Cisco (RFC 2281). "
            "Groupes HSRP par interface. Etat : Initial -> Learn -> Listen -> Speak -> Standby -> Active. "
            "Timers par defaut : hello 3s, hold 10s. Peuvent etre optimises a 1s/3s ou 200ms/700ms (msec). "
            "Preemption : desactivee par defaut — 'standby X preempt' pour re-elire quand le routeur principal revient. "
            "Authentication MD5 possible. HSRP v2 : supporte IPv6, groupes 0-4095. "
            "Equivalent ouvert : VRRP (RFC 5798). Equivalent Cisco multiprotocole : GLBP (load balancing actif/actif)."
        ),
        'summary': "HSRP permet a deux routeurs de partager une IP virtuelle — si le routeur actif tombe, le standby prend le relais automatiquement sans reconfiguration des postes clients.",
        'quiz_q1': "Pourquoi configure-t-on 'standby X preempt' sur le routeur HSRP principal ?",
        'quiz_a1': "Sans preempt, si le routeur principal (priorite 110) tombe et que le standby prend le relais, quand le principal revient il NE reprend PAS automatiquement le role actif. L'ancien standby reste actif. Avec 'standby X preempt', le routeur avec la priorite la plus haute reprend le role actif des qu'il revient en ligne — comportement generalement souhaite pour revenir a l'etat nominal.",
        'quiz_q2': "Quelle est la difference entre HSRP, VRRP et GLBP ?",
        'quiz_a2': "HSRP (Cisco proprietaire) : un seul routeur actif a la fois, un standby. Simple mais sous-optimal (le standby ne fait rien). VRRP (standard IEEE) : equivalent d'HSRP mais interoperable avec du materiel non-Cisco. GLBP (Cisco proprietaire) : plusieurs routeurs actifs simultanement qui se partagent la charge (load balancing) — un seul AVG (Active Virtual Gateway) qui repond ARP, plusieurs AVF (Active Virtual Forwarders) qui traitent le trafic.",
    },

    {
        'title': 'DHCP Snooping — Protection contre les Faux Serveurs DHCP',
        'module_number': 10,
        'module_name': 'Haute disponibilite',
        'level': 'advanced',
        'icon': 'bi-shield-exclamation',
        'order': 3,
        'simple_explanation': (
            "DHCP Snooping est une fonction de securite sur les switches qui protege "
            "contre une attaque simple mais dangereuse : le faux serveur DHCP.\n\n"
            "Attaque sans protection : un attaquant branche son PC et y fait tourner "
            "un serveur DHCP. Les autres PCs du reseau recoivent des adresses IP de cet attaquant, "
            "avec SA passerelle — et maintenant tout le trafic passe par lui. "
            "Il peut tout lire. C'est une attaque 'Man in the Middle'.\n\n"
            "Avec DHCP Snooping, le switch classe les ports en deux categories :\n"
            "- TRUSTED : les vrais serveurs DHCP (votre routeur/serveur)\n"
            "- UNTRUSTED : tous les autres ports (les PCs des employes)\n\n"
            "Si un PC ordinaire tente d'envoyer une reponse DHCP (DHCP Offer/Ack), "
            "le switch bloque le paquet immediatement."
        ),
        'concrete_example': (
            "Reseau entreprise avec un seul vrai serveur DHCP sur le port Gi0/1 du switch.\n\n"
            "Configuration DHCP Snooping :\n\n"
            "ip dhcp snooping\n"
            "ip dhcp snooping vlan 10\n\n"
            "interface GigabitEthernet0/1  (port vers le vrai serveur DHCP)\n"
            "  ip dhcp snooping trust\n\n"
            "Tous les autres ports sont UNTRUSTED par defaut.\n\n"
            "Resultat : si un employe branche un raspberry pi avec un faux serveur DHCP, "
            "le switch voit une DHCP Offer sur un port UNTRUSTED et la bloque. "
            "Aucun PC ne recoira d'adresse de ce faux serveur.\n\n"
            "Bonus : DHCP Snooping cree une 'binding table' — une liste de qui a quelle IP, "
            "sur quel port, avec quel MAC. Cette table est utilisee par d'autres protections "
            "comme Dynamic ARP Inspection (DAI) et IP Source Guard."
        ),
        'technical_version': (
            "DHCP Snooping : filtre les messages DHCP sur les ports UNTRUSTED. "
            "Messages autorises sur UNTRUSTED : DISCOVER, REQUEST (client vers serveur). "
            "Messages bloques sur UNTRUSTED : OFFER, ACK, NAK (serveur vers client). "
            "Binding table : {MAC, IP, VLAN, Interface, Lease time} — persistante si 'ip dhcp snooping database'. "
            "Rate limiting sur ports UNTRUSTED contre DHCP starvation attack : 'ip dhcp snooping limit rate X'. "
            "Option 82 : ajoutee par defaut sur les relais DHCP, peut poser probleme avec certains serveurs — 'no ip dhcp snooping information option'."
        ),
        'summary': "DHCP Snooping classe les ports du switch en trusted/untrusted et bloque toute reponse DHCP sur les ports non autorises — protection contre les faux serveurs DHCP et attaques Man-in-the-Middle.",
        'quiz_q1': "Quelle est la difference entre un port DHCP Snooping trusted et untrusted ?",
        'quiz_a1': "Un port TRUSTED peut envoyer tous les types de messages DHCP (Offer, Ack, Nak) — c'est le port connecte au vrai serveur DHCP ou au routeur DHCP relay. Un port UNTRUSTED (defaut) ne peut envoyer que des messages de demande DHCP (Discover, Request) — les messages de reponse DHCP venant d'un port UNTRUSTED sont consideres comme une attaque et bloques par le switch.",
        'quiz_q2': "A quoi sert la 'DHCP Snooping binding table' et comment est-elle utilisee ?",
        'quiz_a2': "La binding table enregistre pour chaque bail DHCP : l'adresse MAC, l'IP attribuee, le VLAN, le port du switch, et la duree du bail. Elle est utilisee par deux autres mecanismes de securite : Dynamic ARP Inspection (DAI) qui verifie que les reponses ARP correspondent bien a la binding table (protection contre ARP spoofing), et IP Source Guard qui bloque les paquets IP dont la source ne correspond pas a la binding table.",
    },

    {
        'title': 'PortFast et BPDU Guard — Securiser les Ports Utilisateurs',
        'module_number': 10,
        'module_name': 'Haute disponibilite',
        'level': 'advanced',
        'icon': 'bi-lightning-charge',
        'order': 4,
        'simple_explanation': (
            "STP met du temps avant qu'un port soit pret a envoyer du trafic "
            "(environ 30-50 secondes : listening + learning). C'est bien pour les interconnexions "
            "de switches, mais inutile et penalisant pour les prises murales des employes.\n\n"
            "PortFast dit au switch : 'Ce port est connecte directement a un PC, "
            "pas a un autre switch. Passe IMMEDIATEMENT en forwarding, sans attendre STP.'\n\n"
            "Mais si quelqu'un branche un switch non-autorise sur cette prise, "
            "ca cree un risque de boucle STP...\n\n"
            "BPDU Guard resout ca : 'Si ce port PortFast recoit un BPDU (paquet STP), "
            "c'est qu'un switch vient d'etre branche. COUPE le port immediatement (err-disabled).'"
        ),
        'concrete_example': (
            "Salle de formation : 20 prises murales, chacune pour un PC d'etudiant.\n\n"
            "Sans PortFast : chaque fois qu'un etudiant branche son PC, il attend 30-50 secondes "
            "avant d'avoir le reseau. Son DHCP expire, son OS affiche 'Reseau non disponible'.\n\n"
            "Avec PortFast + BPDU Guard :\n\n"
            "interface range Fa0/1-20\n"
            "  spanning-tree portfast\n"
            "  spanning-tree bpduguard enable\n\n"
            "Maintenant : le PC obtient le reseau immediatement a la connexion.\n\n"
            "Scenario de securite : un etudiant branche un mini-switch. "
            "Ce switch envoie des BPDUs. Le port Fa0/X passe en err-disabled. "
            "L'etudiant n'a plus de reseau. L'admin voit une alerte. "
            "Le mini-switch non autorise est neutralise automatiquement."
        ),
        'technical_version': (
            "PortFast : bypasse les etats STP Listening et Learning, passe directement en Forwarding. "
            "Utiliser UNIQUEMENT sur ports edge (terminaux, imprimantes, PCs) — JAMAIS entre switches. "
            "Configuration globale : 'spanning-tree portfast default' (active sur tous les ports access). "
            "Configuration interface : 'spanning-tree portfast'. "
            "BPDU Guard : 'spanning-tree bpduguard enable' (interface) ou 'spanning-tree portfast bpduguard default' (global). "
            "Port en err-disabled : 'show interfaces | include err-disabled'. "
            "Recovery : 'shutdown' + 'no shutdown' ou automatique avec 'errdisable recovery cause bpduguard' + 'errdisable recovery interval 300'."
        ),
        'summary': "PortFast active immediatement un port sans attendre STP — ideal pour les PCs. BPDU Guard desactive automatiquement ce port si un switch non autorise y est branche.",
        'quiz_q1': "Pourquoi ne faut-il JAMAIS activer PortFast sur un port interconnectant deux switches ?",
        'quiz_a1': "PortFast bypasse les etats STP (Listening, Learning) qui ont un role crucial : detecter les boucles avant d'autoriser le trafic. Sur un lien entre switches, il peut exister des boucles physiques. Si PortFast est actif, le port envoie du trafic immediatement — avant que STP ait le temps de detecter et bloquer la boucle. Resultat : une tempete de broadcast qui paralyse tout le reseau.",
        'quiz_q2': "Un port passe en err-disabled apres reception d'un BPDU Guard. Comment le restaurer proprement ?",
        'quiz_a2': "Deux methodes : 1) Manuellement : faire 'shutdown' puis 'no shutdown' sur l'interface apres avoir retire l'equipement problematique. 2) Automatiquement : configurer 'errdisable recovery cause bpduguard' et 'errdisable recovery interval 300' (300 secondes). Le port se relance seul apres le delai. Toujours s'assurer que l'equipement non autorise a ete retire avant la recovery pour eviter que le port se desactive a nouveau.",
    },

    {
        'title': 'Root Guard et Loop Guard — Proteger la Topologie STP',
        'module_number': 10,
        'module_name': 'Haute disponibilite',
        'level': 'advanced',
        'icon': 'bi-shield-lock',
        'order': 5,
        'simple_explanation': (
            "Root Guard et Loop Guard sont deux protections STP qui ciblent des problemes differents.\n\n"
            "Root Guard protege contre un switch intrus qui voudrait devenir Root Bridge. "
            "Si un nouveau switch arrive avec une priorite STP plus basse (meilleure) que le Root actuel, "
            "il pourrait etre elu Root Bridge et perturber toute la topologie. "
            "Root Guard dit : 'Sur ce port, si je recois un Superior BPDU (qui voudrait devenir Root), "
            "je bloque ce port immediatement.'\n\n"
            "Loop Guard protege contre les boucles liees aux liens unidirectionnels. "
            "Si un cable envoie des paquets dans un sens mais pas dans l'autre (panne partielle), "
            "un port Blocking qui ne recoit plus de BPDU pourrait croire qu'il peut passer en Forwarding "
            "et creer une boucle. Loop Guard empeche ca."
        ),
        'concrete_example': (
            "Root Guard — scenario :\n"
            "Ton reseau a un Root Bridge bien configure (core switch, priorite 0). "
            "Un technicien branche un nouveau switch en production sans le configurer. "
            "Ce switch a la priorite par defaut (32768) et un MAC eleve. "
            "Mais si son MAC est plus bas que celui du Root actuel, il devient Root Bridge "
            "et toute la topologie STP se recalcule — coupure reseau pendant 30-50 secondes.\n\n"
            "Avec Root Guard sur les ports des switches d'acces :\n"
            "interface Gi0/24  (port vers le switch d'acces)\n"
            "  spanning-tree guard root\n"
            "Si ce port recoit un Superior BPDU -> port en root-inconsistent (bloque). "
            "Pas de recalcul STP, pas de coupure.\n\n"
            "Loop Guard — scenario :\n"
            "Lien fibre unidirectionnel (panne laser TX). Le port Blocking ne recoit plus de BPDU. "
            "Sans Loop Guard : STP croit que le port peut devenir Root Port -> Forwarding -> boucle. "
            "Avec Loop Guard : le port passe en loop-inconsistent (bloque) plutot qu'en Forwarding."
        ),
        'technical_version': (
            "Root Guard : 'spanning-tree guard root' sur les ports ne devant JAMAIS recevoir de Superior BPDU. "
            "Le port passe en root-inconsistent (equivalent Blocking). "
            "Retire automatiquement quand les Superior BPDUs s'arretent. "
            "A configurer sur les ports vers les switches d'acces et les clients, "
            "JAMAIS vers les switches de distribution/coeur.\n\n"
            "Loop Guard : 'spanning-tree guard loop' ou 'spanning-tree loopguard default' (global). "
            "Protege les ports Root Port et Alternate Port (ports qui attendent des BPDUs). "
            "Si le port cesse de recevoir des BPDUs, il passe en loop-inconsistent au lieu de Forwarding. "
            "Incompatible avec PortFast. Complementaire de UDLD (Unidirectional Link Detection)."
        ),
        'summary': "Root Guard empeche un switch non autorise de devenir Root Bridge. Loop Guard empeche une boucle STP due a la perte de BPDUs sur un lien defaillant.",
        'quiz_q1': "Sur quels ports doit-on activer Root Guard et pourquoi pas sur tous les ports ?",
        'quiz_a1': "Root Guard doit etre active sur les ports qui ne devraient JAMAIS etre le chemin vers le Root Bridge — typiquement les ports vers les switches d'acces et les ports clients. On NE l'active PAS vers les switches de distribution ou le coeur, car ces ports sont precisement ceux qui pointent vers le Root Bridge. Si on mettait Root Guard sur un port vers le Root, ce port serait bloque des la reception du premier BPDU du Root — coupure immediate.",
        'quiz_q2': "Quelle est la difference entre l'etat 'root-inconsistent' (Root Guard) et 'err-disabled' (BPDU Guard) ?",
        'quiz_a2': "BPDU Guard met le port en 'err-disabled' — completement arrete, aucun paquet ne passe, intervention manuelle (ou errdisable recovery) necessaire pour le ranimer. Root Guard met le port en 'root-inconsistent' — bloque pour le trafic, mais STP continue de surveiller. Des que les Superior BPDUs s'arretent (le switch problematique est retire), le port revient automatiquement en etat normal sans intervention.",
    },

    # =========================================================================
    # BLOC 9 — Module 10 (fin) : concepts 41 a 44
    # Port Security, DAI, IP Source Guard, SPAN
    # =========================================================================

    {
        'title': 'Port Security — Limiter les Equipements sur un Port',
        'module_number': 10,
        'module_name': 'Haute disponibilite',
        'level': 'advanced',
        'icon': 'bi-lock',
        'order': 6,
        'simple_explanation': (
            "Port Security permet de controler QUELS appareils ont le droit de se brancher "
            "sur un port de switch.\n\n"
            "Chaque appareil reseau a une adresse MAC unique (comme une carte d'identite). "
            "Port Security dit au switch :\n"
            "'Sur ce port, je n'accepte que X adresses MAC maximum. "
            "Si quelqu'un branche un appareil non autorise, reagis.'\n\n"
            "Les reactions possibles :\n"
            "- Protect : jette les paquets inconnus en silence\n"
            "- Restrict : jette + envoie une alerte (SNMP)\n"
            "- Shutdown : coupe le port completement (err-disabled)\n\n"
            "C'est utile pour empecher un employe de brancher un switch personnel, "
            "un PC non autorise, ou de deplacer son PC sur une autre prise."
        ),
        'concrete_example': (
            "Bureau comptabilite : chaque prise murale doit accepter UN SEUL PC.\n\n"
            "interface FastEthernet0/5\n"
            "  switchport mode access\n"
            "  switchport port-security\n"
            "  switchport port-security maximum 1\n"
            "  switchport port-security violation shutdown\n"
            "  switchport port-security mac-address sticky\n\n"
            "Le 'mac-address sticky' est pratique : le switch apprend automatiquement "
            "le premier MAC qui se connecte et le note comme autorise. "
            "Pas besoin de taper le MAC manuellement.\n\n"
            "Scenario : la comptable part en vacances. Son collegue branche son propre PC "
            "sur sa prise. Le switch voit un nouveau MAC -> port en err-disabled. "
            "Le collegue n'a pas le reseau. L'admin recoit une alerte. "
            "La comptable retrouvera son port a son retour apres une remise en service."
        ),
        'technical_version': (
            "Port Security s'applique uniquement sur ports en mode access ou trunk statique (pas dynamique). "
            "Modes : static (mac configure manuellement), dynamic (appris, perdu au reload), sticky (appris + sauvegarde dans running-config). "
            "Violation modes : protect (drop silencieux), restrict (drop + SNMP trap + compteur), shutdown (err-disabled — le plus courant). "
            "Commandes de verification : 'show port-security', 'show port-security address', 'show port-security interface Fx/x'. "
            "Recovery err-disabled : 'shutdown' + 'no shutdown' ou 'errdisable recovery cause psecure-violation'."
        ),
        'summary': "Port Security limite le nombre de MACs autorises sur un port et desactive ce port si un equipement non autorise se connecte — protection contre les branchements sauvages.",
        'quiz_q1': "Quelle est la difference entre les modes de violation 'restrict' et 'shutdown' ?",
        'quiz_a1': "Restrict : le port RESTE actif mais les paquets des MACs non autorises sont jetes silencieusement. Un compteur de violations s'incremente et une alerte SNMP peut etre envoyee. Le trafic des MACs legitimes continue. Shutdown : le port passe en err-disabled immediatement — TOUT le trafic est coupe, y compris le MAC legitime. C'est le mode le plus securise mais aussi le plus impactant pour l'utilisateur.",
        'quiz_q2': "A quoi sert l'option 'sticky' dans Port Security ?",
        'quiz_a2': "L'option 'sticky' permet au switch d'apprendre automatiquement les adresses MAC qui se connectent sur le port ET de les sauvegarder dans la running-config (comme si elles avaient ete configurees manuellement). Avantage : pas besoin de connaitre le MAC a l'avance, le switch l'apprend au premier branchement. La MAC sticky est persistante au reload si on fait 'copy running startup'. Sans sticky, les MACs dynamiques sont perdus au redemarrage.",
    },

    {
        'title': 'Dynamic ARP Inspection — Proteger contre l\'ARP Spoofing',
        'module_number': 10,
        'module_name': 'Haute disponibilite',
        'level': 'advanced',
        'icon': 'bi-shield-fill-check',
        'order': 7,
        'simple_explanation': (
            "Tu te souviens d'ARP ? C'est le protocole qui associe une adresse IP a une adresse MAC. "
            "Le probleme : ARP fait confiance a tout le monde. N'importe qui peut envoyer "
            "une fausse reponse ARP et dire 'Moi, je suis l'adresse 192.168.1.1 et mon MAC c'est XX:XX'.\n\n"
            "Un attaquant peut se faire passer pour la passerelle du reseau. "
            "Tous les PCs envoient alors leur trafic a l'attaquant — qui peut tout lire "
            "avant de le retransmettre. C'est l'ARP Spoofing / ARP Poisoning.\n\n"
            "DAI (Dynamic ARP Inspection) demande au switch de verifier chaque reponse ARP "
            "contre la DHCP Snooping binding table : 'Cette IP et ce MAC correspondent-ils "
            "a ce que je sais ?' Si non, le paquet est rejete."
        ),
        'concrete_example': (
            "Attaque sans DAI :\n"
            "Attaquant envoie un ARP gratuit : 'Je suis 192.168.1.1 (la passerelle), mon MAC = AA:BB'\n"
            "Tous les PCs mettent a jour leur cache ARP avec ce faux mapping\n"
            "Tout le trafic Internet des employes passe par l'attaquant\n\n"
            "Avec DAI configure :\n\n"
            "ip arp inspection vlan 10\n\n"
            "interface Gi0/1  (vers le routeur/serveur DHCP)\n"
            "  ip arp inspection trust\n\n"
            "Le switch verifie chaque ARP sur les ports UNTRUSTED :\n"
            "ARP de l'attaquant : 'IP 192.168.1.1 = MAC AA:BB'\n"
            "Binding table dit : 'IP 192.168.1.1 = MAC CC:DD (le vrai routeur)'\n"
            "-> Discordance -> ARP rejete -> attaque neutralisee\n\n"
            "Les PCs ne mettent jamais a jour leur cache avec la fausse association."
        ),
        'technical_version': (
            "DAI s'appuie sur la DHCP Snooping binding table pour valider les paquets ARP. "
            "Sur les ports UNTRUSTED : chaque ARP request/reply est inspecte. "
            "Si IP/MAC ne correspondent pas a la binding table -> paquet rejete + log. "
            "Pour les IPs statiques (pas de DHCP) : configurer des ARP ACLs manuelles avec 'arp access-list'. "
            "Rate limiting DAI : 'ip arp inspection limit rate X' (par defaut 100 pps) contre ARP flood. "
            "Commandes : 'show ip arp inspection', 'show ip arp inspection statistics'. "
            "DAI necessite DHCP Snooping actif sur le meme VLAN."
        ),
        'summary': "DAI inspecte chaque reponse ARP sur les ports non autorises et la rejette si le couple IP/MAC ne correspond pas a la binding table DHCP — protection contre l'ARP Spoofing.",
        'quiz_q1': "Pourquoi DAI necessite-t-il que DHCP Snooping soit configure au prealable ?",
        'quiz_a1': "DAI valide les paquets ARP en comparant le couple IP/MAC avec la DHCP Snooping binding table. Cette table est construite par DHCP Snooping en enregistrant chaque attribution DHCP : qui a recu quelle IP, sur quel port, avec quel MAC. Sans cette table, DAI n'a pas de reference pour savoir si une association ARP est legitime ou falsifiee. Exception : pour les equpements avec IP statique, on configure des ARP ACLs manuelles.",
        'quiz_q2': "Que se passe-t-il si DAI est mal configure et qu'un port legitime (ex: le routeur) est en UNTRUSTED ?",
        'quiz_a2': "Les ARP du routeur seraient inspectes contre la binding table. Comme le routeur a souvent une IP statique (pas d'entree DHCP dans la binding table), ses ARP seraient rejetes. Le routeur deviendrait injoignable pour les clients du VLAN — coupure reseau. C'est pourquoi les ports vers l'infrastructure (routeurs, serveurs DHCP, autres switches de confiance) doivent etre configures en 'ip arp inspection trust'.",
    },

    {
        'title': 'IP Source Guard — Bloquer l\'Usurpation d\'Adresse IP',
        'module_number': 10,
        'module_name': 'Haute disponibilite',
        'level': 'advanced',
        'icon': 'bi-patch-check',
        'order': 8,
        'simple_explanation': (
            "IP Source Guard empeche un utilisateur de changer manuellement son adresse IP "
            "pour se faire passer pour quelqu'un d'autre.\n\n"
            "Sans protection : un employe peut configurer manuellement l'IP d'un serveur "
            "sur son PC. Le trafic qui lui est destine arrive sur son PC. "
            "C'est de l'usurpation d'identite reseau.\n\n"
            "IP Source Guard dit au switch : 'Sur ce port, je n'accepte que les paquets "
            "dont l'IP source correspond a ce que la binding table DHCP dit.'\n\n"
            "Si l'employe change son IP, ses paquets sont bloques car "
            "l'IP ne correspond plus a ce que le serveur DHCP lui a attribue."
        ),
        'concrete_example': (
            "Scenario sans IP Source Guard :\n"
            "Serveur RH a l'IP 10.0.0.10 (IP statique)\n"
            "Employe malveillant configure son PC en 10.0.0.10\n"
            "Le trafic destine au serveur RH arrive maintenant sur le PC de l'employe\n"
            "Il peut recuperer des donnees confidentielles\n\n"
            "Avec IP Source Guard :\n\n"
            "interface FastEthernet0/12  (port de l'employe)\n"
            "  ip verify source\n\n"
            "Le switch verifie chaque paquet entrant sur Fa0/12 :\n"
            "Binding table dit : Fa0/12 -> MAC aabb.ccdd -> IP 10.0.0.50 (attribuee par DHCP)\n"
            "Paquet avec IP source 10.0.0.10 -> ne correspond pas -> bloque\n"
            "L'employe malveillant n'a pas de connectivite avec la fausse IP.\n\n"
            "Note : 'ip verify source port-security' verifie en plus l'adresse MAC."
        ),
        'technical_version': (
            "IP Source Guard cree des VACL (VLAN ACLs) dynamiques basees sur la DHCP Snooping binding table. "
            "Deux modes : 'ip verify source' (filtre sur IP source uniquement), "
            "'ip verify source port-security' (filtre sur IP source ET MAC source). "
            "Pour les IPs statiques : ajouter manuellement des entrees avec 'ip source binding MAC vlan VLAN ip IP interface INT'. "
            "Commandes de verification : 'show ip verify source', 'show ip source binding'. "
            "Necessite DHCP Snooping. Compatible avec DAI — les deux sont complementaires : "
            "IPSG filtre au niveau IP (couche 3), DAI filtre au niveau ARP (couche 2/3)."
        ),
        'summary': "IP Source Guard bloque les paquets dont l'IP source ne correspond pas a la binding table DHCP — empeche l'usurpation d'adresse IP sur un port switch.",
        'quiz_q1': "Quelle est la difference entre IP Source Guard et DAI en termes de protection ?",
        'quiz_a1': "DAI protege contre l'ARP Spoofing : il inspecte les paquets ARP (couche 2/3) pour empecher la falsification du cache ARP des autres machines. IP Source Guard protege contre l'IP Spoofing : il inspecte les paquets IP ordinaires (couche 3) pour empecher qu'un port utilise une adresse IP qu'il n'est pas cense avoir. Les deux s'appuient sur la meme DHCP binding table et sont complementaires — DAI protege la resolution d'adresses, IPSG protege le trafic IP.",
        'quiz_q2': "Comment configurer IP Source Guard pour un equipement avec une adresse IP statique (pas de DHCP) ?",
        'quiz_a2': "Puisque cet equipement n'a pas d'entree dans la DHCP Snooping binding table, il faut l'ajouter manuellement avec la commande : 'ip source binding XXXX.XXXX.XXXX vlan Y ip Z.Z.Z.Z interface IntX/X' (en remplacant par les vraies valeurs MAC, VLAN, IP et interface). Sans cette entree manuelle, IP Source Guard bloquerait tous les paquets de cet equipement car il ne trouverait pas son IP dans la binding table.",
    },

    {
        'title': 'SPAN — Analyser le Trafic Reseau sans le Couper',
        'module_number': 10,
        'module_name': 'Haute disponibilite',
        'level': 'advanced',
        'icon': 'bi-binoculars',
        'order': 9,
        'simple_explanation': (
            "SPAN (Switched Port Analyzer), aussi appele 'port mirroring', "
            "est une fonction qui copie le trafic d'un port (ou d'un VLAN entier) "
            "vers un autre port ou tu as branche un outil d'analyse.\n\n"
            "Pourquoi ? Parce qu'un switch moderne ne diffuse pas le trafic a tout le monde "
            "(contrairement a un hub). Chaque conversation est privee entre les deux ports. "
            "Pour voir ce qui se passe sur un autre port, il faut que le switch te fasse "
            "une copie.\n\n"
            "Utilisations :\n"
            "- Brancher Wireshark pour capturer le trafic d'un serveur suspect\n"
            "- Alimenter un IDS/IPS (systeme de detection d'intrusion)\n"
            "- Analyser les performances reseau\n"
            "- Diagnostiquer un probleme applicatif"
        ),
        'concrete_example': (
            "Scenario : un serveur web (Gi0/5) a un comportement suspect. "
            "L'equipe securite veut capturer son trafic avec Wireshark "
            "depuis leur PC d'analyse branche sur Gi0/24.\n\n"
            "Configuration SPAN :\n\n"
            "monitor session 1 source interface GigabitEthernet0/5 both\n"
            "monitor session 1 destination interface GigabitEthernet0/24\n\n"
            "'both' signifie copier le trafic entrant ET sortant du serveur. "
            "On peut aussi mettre 'rx' (entrant seulement) ou 'tx' (sortant seulement).\n\n"
            "Resultat : le trafic du serveur continue normalement (SPAN ne perturbe pas). "
            "En plus, une copie de chaque paquet arrive sur Gi0/24. "
            "Wireshark voit tout.\n\n"
            "RSPAN (Remote SPAN) : faire la meme chose mais vers un switch distant, "
            "via un VLAN RSPAN dedie. ERSPAN (Encapsulated) : encapsuler le trafic "
            "dans GRE pour l'envoyer sur un reseau IP routed."
        ),
        'technical_version': (
            "SPAN local : source et destination sur le meme switch. "
            "Source : interface(s) ou VLAN(s). Destination : un seul port (desactive pour le trafic normal). "
            "Limitations : le port destination ne peut pas etre source d'une autre session SPAN. "
            "Nombre de sessions SPAN simultanoes : varie selon la plateforme (souvent 2-4). "
            "RSPAN : utilise un VLAN RSPAN special (sans trafic normal) pour transporter le trafic mirore entre switches. "
            "ERSPAN (Cisco) : encapsule dans GRE (type II ou III), permet l'envoi sur un reseau L3 routed. "
            "Verification : 'show monitor session 1'. "
            "Impact performance : SPAN a un impact minimal, mais ERSPAN consomme de la CPU pour l'encapsulation GRE."
        ),
        'summary': "SPAN copie le trafic d'un port ou VLAN vers un port d'analyse sans perturber le trafic original — indispensable pour Wireshark, IDS, et le diagnostic reseau sur un switch.",
        'quiz_q1': "Pourquoi a-t-on besoin de SPAN sur un switch alors qu'on n'en avait pas besoin sur un hub ?",
        'quiz_a1': "Un hub (concentrateur) diffuse chaque trame recue sur TOUS ses ports — n'importe quel PC connecte voit le trafic de tout le monde (d'ou les collisions et la necessite de CSMA/CD). Un switch est plus intelligent : il envoie chaque trame uniquement vers le port de destination. Un PC connecte sur le port A ne voit que son propre trafic, pas celui du port B. SPAN est donc necessaire pour 'forcer' le switch a envoyer une copie du trafic vers un port d'analyse.",
        'quiz_q2': "Quelle est la difference entre SPAN, RSPAN et ERSPAN ?",
        'quiz_a2': "SPAN (local) : source et destination sur le MEME switch physique — le plus simple. RSPAN (Remote SPAN) : source et destination sur des switches DIFFERENTS dans le meme reseau L2, le trafic mirore transite dans un VLAN RSPAN dedie entre les switches. ERSPAN (Encapsulated Remote SPAN) : comme RSPAN mais encapsule dans GRE, peut traverser un reseau L3 routed — permet d'envoyer le trafic mirore vers un analyseur dans un autre datacenter ou site distant.",
    },

]


class Command(BaseCommand):
    help = 'Ajoute les concepts reseau pedagogiques (mode enfant de 10 ans)'

    def handle(self, *args, **options):
        self.stdout.write('=== seed_concepts : ajout des concepts reseau ===')
        created = 0
        skipped = 0
        for data in CONCEPTS_DATA:
            slug = slugify(data['title'])
            concept, was_created = NetworkConcept.objects.get_or_create(
                slug=slug,
                defaults={
                    'title':               data['title'],
                    'module_number':       data['module_number'],
                    'module_name':         data['module_name'],
                    'level':               data['level'],
                    'icon':                data['icon'],
                    'order':               data['order'],
                    'simple_explanation':  data['simple_explanation'],
                    'concrete_example':    data['concrete_example'],
                    'technical_version':   data['technical_version'],
                    'summary':             data['summary'],
                    'quiz_q1':             data['quiz_q1'],
                    'quiz_a1':             data['quiz_a1'],
                    'quiz_q2':             data['quiz_q2'],
                    'quiz_a2':             data['quiz_a2'],
                },
            )
            if was_created:
                self.stdout.write(f'  [OK] {concept.title}')
                created += 1
            else:
                self.stdout.write(f'  [SKIP] deja present : {concept.title}')
                skipped += 1

        self.stdout.write('')
        self.stdout.write(f'=== Termine : {created} crees, {skipped} ignores ===')
