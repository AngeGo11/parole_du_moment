# 🙏📖 Parole du Moment - Laisse la parole te parler au bon moment

---

## 🌟 À Propos

**Parole du Moment** est une application mobile spirituelle qui utilise une IA(**Intelligence
Spirituelle**) pour proposer des versets bibliques adaptés aux situations de vie de l'utilisateur.
Décrivez votre situation actuelle, et votre assistant spirituel personnel vous suggérera le verset
parfait pour vous accompagner dans ce moment, avec des conseils personnalisés et une guidance
spirituelle.

### ✨ Fonctionnalités

- 🙏 **Assistant Spirituel IA** : Votre compagnon spirituel personnel qui comprend vos besoins et
  vous guide
- 🤖 **Intelligence Spirituelle** : Analyse profonde de votre situation avec conseils personnalisés.
- 📱 **Interface Intuitive** : Design épuré et moderne avec une palette de couleurs spirituelles
- 📖 **Base de Données Biblique** : Accès à une vaste collection de versets et commentaires
- 💭 **Personnalisation Avancée** : Suggestions adaptées à votre contexte personnel et spirituel
- 🗣️ **Conversation Spirituelle** : Dialogue interactif avec votre assistant pour un accompagnement
  continu
- 🔄 **Mise à Jour Quotidienne** : Nouveaux versets, prières et fonctionnalités régulières

## 🙏 Assistant Spirituel IA

L'**Assistant Spirituel** est le cœur de l'application. Il s'agit d'une Intelligence Spirituelle
avancée qui :

### 🧠 **Capacités de l'Assistant**

- **Écoute Active** : Comprend profondément votre situation et vos émotions
- **Guidance Personnalisée** : Propose des conseils adaptés à votre cheminement spirituel
- **Conversation Naturelle** : Dialogue fluide et empathique comme avec un conseiller spirituel
- **Mémoire Contextuelle** : Se souvient de vos échanges précédents pour un accompagnement cohérent
- **Sagesse Biblique** : Puise dans la richesse des Écritures pour vous éclairer

### 💬 **Types d'Interactions**

- **Consultation Spirituelle** : Partagez vos préoccupations et recevez guidance
- **Étude Biblique** : Explorez les Écritures avec des explications personnalisées
- **Prière Guidée** : Accompagnement dans vos moments de prière
- **Réflexion Quotidienne** : Méditations et réflexions adaptées à votre journée

## 🤖 Architecture IA : LangChain + OpenAI

### 🎯 Pourquoi LangChain + OpenAI ?

Notre choix technologique **LangChain + OpenAI** est la meilleure combinaison pour créer un assistant spirituel intelligent et contextuel :

|            **OpenAI seul** ❌                   |           **LangChain + OpenAI** ✅ |
|-------------------------------------------------|-------------------------------------------------|
| ❌ Pas de mémoire conversationnelle native     | ✅ Mémoire conversationnelle automatique |
| ❌ Gestion manuelle de l'historique            | ✅ Historique géré pour vous |
| ❌ Code complexe pour RAG                      | ✅ RAG (Retrieval Augmented Generation) intégré |
| ❌ Templates de prompts difficiles à maintenir | ✅ Templates de prompts réutilisables |
| ❌ Code difficile à maintenir                  | ✅ Code propre et maintenable |

### 🧩 Architecture Technique

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Flutter)                 │
│              Interface utilisateur mobile              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                     │
│              /api/assistant/chat                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           LangChain (Orchestration)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Memory Management (Conversation History)        │  │
│  │  └─ ConversationBufferMemory                     │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  RAG Chain (Retrieval Augmented Generation)     │  │
│  │  └─ MongoDB Vector Store → Prompt → LLM         │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Prompt Templates (Spiritual Guidance)           │  │
│  │  └─ Spiritual AI Prompts                        │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              OpenAI GPT-4 (Intelligence)                │
│         Modèle conversationnel avancé                   │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              MongoDB (Base de données)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Versets    │  │  Historique  │  │  Utilisateurs│ │
│  │   Bibliques  │  │ Conversation │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### ✨ Avantages de LangChain

1. **Mémoire Conversationnelle Automatique** 🔄
   - Conservation automatique de l'historique des conversations
   - Contexte maintenu entre les sessions
   - Personnalisation basée sur les interactions précédentes

2. **RAG Intégré** 📚
   - Recherche intelligente dans le corpus biblique MongoDB
   - Retrieval de versets pertinents selon le contexte
   - Génération de réponses enrichies avec références bibliques

3. **Templates de Prompts Réutilisables** 📝
   - Prompts spirituels pré-configurés et modulaires
   - Personnalisation facile selon le type d'interaction
   - Gestion centralisée des instructions spirituelles

4. **Code Maintenable** 🛠️
   - Architecture modulaire et extensible
   - Séparation claire des responsabilités
   - Intégration facile de nouvelles fonctionnalités

5. **Gestion d'Erreurs Robuste** 🛡️
   - Retry automatique en cas d'échec
   - Fallback gracieux
   - Logging intégré pour le debugging

## 🎨 Palette de Couleurs

L'application utilise une palette de couleurs inspirée de la spiritualité :

- **Marron Bible** `#8d6e63` - Couleur principale, évoquant la terre et la stabilité
- **Or Doux** `#d4af37` - Accents dorés, symbolisant la lumière divine

## 🏗️ Architecture

### Frontend (Flutter)

- **Framework** : Flutter 3.8.1+
- **Langage** : Dart
- **Plateformes** : Android, iOS, Web, Desktop

### Backend (Python)

- **Framework** : FastAPI
- **Intelligence Spirituelle** : **LangChain + OpenAI GPT-4** 🎯
  - **OpenAI GPT-4** → Le cerveau (intelligence)
  - **LangChain** → Le système nerveux (orchestration)
- **Assistant IA** : Modèle conversationnel spécialisé en guidance spirituelle avec mémoire conversationnelle automatique
- **Base de données** : MongoDB local avec corpus biblique enrichi
- **API** : RESTful API + WebSocket pour conversations temps réel
- **RAG (Retrieval Augmented Generation)** : Intégré via LangChain pour recherche contextuelle dans les versets bibliques

### Authentification & Services

- **Authentification** : Firebase Authentication (Email/Password, Google, etc.)
- **Backend Database** : MongoDB pour le stockage des versets, utilisateurs, et historiques
- **Sécurité** : JWT tokens via Firebase pour sécuriser les endpoints API

## 🚀 Installation

### Prérequis

- Flutter SDK 3.8.1+
- Python 3.8+
- MongoDB 6.0+ (local)
- Git
- Android Studio (pour le développement Android)
- Firebase CLI (optionnel)

### Installation du Frontend

```bash
# Cloner le repository
git clone https://github.com/votre-username/parole_du_moment.git
cd parole_du_moment

# Installer les dépendances Flutter
flutter pub get

# Lancer l'application
flutter run
```

### Installation du Backend

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances Python (inclut LangChain + OpenAI)
cd backend
pip install -r requirements.txt

# Configurer les variables d'environnement
# Créer un fichier .env dans le dossier backend avec vos clés API
# Voir la section Configuration ci-dessous

# Démarrer MongoDB local
mongod --dbpath /path/to/your/data/directory

# Importer les données bibliques dans MongoDB
python backend/import_all_data.py

# Lancer le serveur
python app.py
```

### 🔑 Obtenir vos Clés API

1. **OpenAI API Key** :
   - Créez un compte sur [platform.openai.com](https://platform.openai.com)
   - Allez dans API Keys → Créez une nouvelle clé secrète
   - Copiez la clé dans votre fichier `.env`

2. **LangSmith (Optionnel)** :
   - LangSmith est utile pour le monitoring et le debugging
   - Créez un compte sur [smith.langchain.com](https://smith.langchain.com)
   - Obtenez votre clé API pour le tracing avancé

### Installation de MongoDB

#### Windows

```bash
# Télécharger MongoDB Community Server depuis https://www.mongodb.com/try/download/community
# Installer avec les options par défaut
# Démarrer MongoDB
mongod
```

#### macOS

```bash
# Avec Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community
```

#### Linux (Ubuntu/Debian)

```bash
# Importer la clé publique
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Créer le fichier de liste
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Mettre à jour et installer
sudo apt-get update
sudo apt-get install -y mongodb-org

# Démarrer MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

## 🔧 Configuration

### Variables d'Environnement

Créez un fichier `.env` dans le dossier backend :

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4  # ou gpt-3.5-turbo pour des coûts réduits

# LangChain Configuration
LANGCHAIN_TRACING_V2=false  # Mettre à true pour activer le tracing LangSmith
LANGCHAIN_API_KEY=your_langsmith_api_key  # Optionnel, pour le monitoring

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=parole_du_moment_db

# Firebase Configuration
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com

# Application Configuration
SECRET_KEY=your_secret_key_here
API_BASE_URL=http://localhost:8000

# Memory Configuration (LangChain)
MEMORY_MAX_TOKEN_LIMIT=2000  # Limite de tokens pour la mémoire conversationnelle
```

### Configuration Flutter

Modifiez `lib/config/api_config.dart` :

```dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000';
  static const String apiVersion = 'v1';
  static const String firebaseProjectId = 'your_firebase_project_id';
}
```

### Configuration Firebase

1. **Ajouter le fichier de configuration Firebase** :
    - Téléchargez `google-services.json` depuis votre projet Firebase Console
    - Placez-le dans `android/app/google-services.json`

2. **Configuration iOS** (si applicable) :
    - Téléchargez `GoogleService-Info.plist` depuis Firebase Console
    - Placez-le dans `ios/Runner/GoogleService-Info.plist`

3. **Activer l'authentification** :
    - Dans Firebase Console → Authentication → Sign-in method
    - Activer "Email/Password" et/ou "Google" selon vos besoins

## 📚 Structure du Projet

```
parole_du_moment/
├── lib/                    # Code source Flutter
│   ├── main.dart
│   ├── services/           # Services API et Firebase
│   │   ├── firebase_service.dart  # Service Firebase Auth
│   │   └── api_service.dart       # Service API backend
│   ├── screens/            # Écrans de l'application
│   │   ├── auth/           # Authentification (login, register)
│   │   ├── assistant/      # Interface assistant spirituel
│   │   └── conversation/   # Chat avec l'IA
│   └── widgets/            # Composants réutilisables
├── backend/                # Code source Python
│   ├── app.py             # Point d'entrée FastAPI
│   ├── models/            # Modèles MongoDB
│   ├── services/          # Services métier
│   │   ├── spiritual_ai.py # Intelligence Spirituelle (LangChain + OpenAI)
│   │   ├── assistant.py    # Assistant conversationnel avec mémoire
│   │   ├── mongodb_service.py # Service MongoDB
│   │   └── rag_service.py  # Service RAG pour recherche biblique
│   ├── api/               # Endpoints API
│   │   └── assistant.py   # Routes API pour l'assistant
│   ├── prompts/           # Prompts spirituels personnalisés (LangChain)
│   │   ├── spiritual_guidance.py
│   │   └── bible_study.py
│   ├── chains/            # Chains LangChain
│   │   ├── conversation_chain.py
│   │   └── retrieval_chain.py
│   └── import_all_data.py # Script d'importation des données bibliques
├── dataset/               # Données bibliques
│   ├── emotions.json      # Émotions et sentiments
│   ├── themes.json        # Thèmes spirituels
│   ├── users.json         # Utilisateurs de test
│   ├── livres.json        # Livres bibliques
│   ├── versets.json       # Versets bibliques
│   └── bible/             # Corpus biblique complet
├── android/               # Configuration Android
│   └── app/
│       ├── google-services.json  # Configuration Firebase
│       └── build.gradle.kts      # Configuration build
├── assets/                # Ressources (images, icônes)
└── docs/                  # Documentation
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Fork** le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. **Commit** vos changements (`git commit -m 'Add some AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une **Pull Request**

### Guidelines de Contribution

- Respectez le style de code existant
- Ajoutez des tests pour les nouvelles fonctionnalités
- Documentez vos changements
- Utilisez des messages de commit clairs

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Communauté Flutter** pour l'excellent framework
- **OpenAI** pour l'API GPT-4 d'intelligence artificielle avancée
- **LangChain** pour l'orchestration et la gestion de la mémoire conversationnelle
- **MongoDB** pour la base de données NoSQL flexible
- **Firebase** pour l'authentification sécurisée
- **Communauté chrétienne** pour l'inspiration spirituelle

## 📞 Contact

- **Développeur** : [Votre Nom]
- **Email** : votre.email@example.com
- **GitHub** : [@votre-username](https://github.com/votre-username)

---

<div align="center">
  <p>Fait avec ❤️ et 🙏 pour la gloire de Dieu</p>
  <p><em>"Ta parole est une lampe à mes pieds, et une lumière sur mon sentier." - Psaume 119:105</em></p>
</div>
