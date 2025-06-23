# forum_academique_django
Forum académique collaboratif : Ce projet est un forum académique web conçu pour l’Université UCC. Il vise à favoriser l’apprentissage collaboratif entre étudiants et encadreurs.  Construit avec  Django, avec une gestion des rôles, des contributions (texte &amp; fichiers), des groupes , des TP, et des réactions de type “j’aime / je n’aime pas”.

# 🎓 Forum Académique Collaboratif – UCC

Ce projet est une plateforme web destinée à favoriser les échanges académiques et l’apprentissage collaboratif à l’Université Catholique du Congo (UCC).

---

## 🛠️ Fonctionnalités principales

- Création de **travaux pratiques** et **sujets de discussion**
- **Groupes de travail** avec chefs et encadrement
- Soumission de **contributions** (texte ou fichiers)
- **Commentaires** et **réactions** (👍 / 👎)
- Rôles différenciés : Étudiant · Professeur · Administrateur
- Interface simple, responsive et intuitive

---

## 🧱 Technologies utilisées

- **Django** (framework web principal)
- **MySQL** (base de données relationnelle)
- **Gunicorn** (serveur applicatif Python)
- **Nginx** (reverse proxy & serveur statique)
- **Docker** *(optionnel pour déploiement)*
- HTML/CSS/JS (avec `fetch()` pour appels dynamiques)

---

## 📦 Installation locale (Linux/Windows)

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/ton-utilisateur/forum-academique-ucc.git
   cd forum-academique-ucc
Installer les dépendances :

bash
Copier
Modifier
pip install -r requirements.txt
Configurer la base de données dans settings.py (MySQL recommandé).

Effectuer les migrations :

bash
Copier
Modifier
python manage.py makemigrations
python manage.py migrate
Créer un superutilisateur :

bash
Copier
Modifier
python manage.py createsuperuser
Lancer le serveur :

bash
Copier
Modifier
python manage.py runserver
📂 Structure du projet
csharp
Copier
Modifier
Forum/
├── main/               # App principale
├── templates/          # Templates HTML
├── static/             # Fichiers CSS/JS
├── media/              # Fichiers uploadés
├── requirements.txt    # Dépendances
├── README.md
└── manage.py
