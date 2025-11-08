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

# ⚠️ IMPORTANT : Pré-calculer les embeddings (une seule fois, obligatoire)
python scripts/compute_embeddings.py --translation lsg

# Lancer le serveur
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 🔑 Obtenir vos Clés API

1. **OpenAI API Key** :
   - Créez un compte sur [console.groq.com](https://console.groq.com)
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
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_ANALYSIS=llama3-70b-8192  # Modèle pour l'analyse (par défaut: llama3-70b-8192)
GROQ_MODEL_GENERATION=llama3-70b-8192  # Modèle pour la génération (par défaut: llama3-70b-8192)
# Note: Obtenez votre clé API sur https://console.groq.com
# Modèles disponibles: llama3-70b-8192, llama3-8b-8192, gemma-7b-it, gemma2-9b-it

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

# Embeddings Configuration (Recherche Vectorielle)
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2  # Modèle d'embeddings (optionnel)
# Alternatives: all-MiniLM-L6-v2 (plus rapide), all-mpnet-base-v2 (meilleure qualité)
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

## 🔍 Recherche Vectorielle avec Embeddings

### 📋 Vue d'ensemble

Le système utilise la **recherche vectorielle avec embeddings** pour trouver les versets les plus pertinents, peu importe les mots utilisés par l'utilisateur. Cette technologie permet une compréhension sémantique profonde plutôt qu'une simple correspondance de mots-clés.

### 🎯 Pourquoi les Embeddings ?

| **Méthode Traditionnelle** ❌ | **Recherche Vectorielle** ✅ |
|-------------------------------|------------------------------|
| Recherche par mots-clés exacts | Compréhension sémantique |
| "je suis triste" ≠ "mon cœur est lourd" | "je suis triste" = "mon cœur est lourd" |
| Dépend des collections de liaison | Fonctionne indépendamment |
| Peut échouer si mot manquant | Trouve toujours des résultats pertinents |
| Résultats parfois aléatoires | Résultats toujours pertinents |

### 🚀 Installation et Configuration

#### 1. Installer les dépendances

Les dépendances nécessaires sont déjà dans `requirements.txt` :

```bash
cd backend
pip install -r requirements.txt
```

Cela installera automatiquement :
- `sentence-transformers` : Pour générer les embeddings
- `numpy` : Pour les calculs vectoriels
- `tqdm` : Pour les barres de progression

#### 2. Pré-calculer les embeddings (une seule fois)

**⚠️ IMPORTANT** : Cette étape est **obligatoire** avant d'utiliser l'application. Elle calcule et stocke les embeddings de tous les versets dans MongoDB.

```bash
# Pour toutes les traductions (peut prendre plusieurs minutes)
python scripts/compute_embeddings.py

# Pour une traduction spécifique (recommandé, plus rapide)
python scripts/compute_embeddings.py --translation lsg
```

**Exemple de sortie** :
```
🔌 Connexion à MongoDB: mongodb://localhost:27017
📚 Base de données: parole_du_moment_db
✅ Service d'embeddings initialisé (dimension: 384)
📖 Traitement uniquement de la traduction: lsg
📊 Nombre total de versets à traiter: 31102
Calcul des embeddings: 100%|████████████| 31102/31102 [05:23<00:00]
✅ Traitement terminé!
   Total traité: 31102
   Mis à jour: 31102
   Ignorés (déjà calculés ou erreurs): 0
```

#### 3. Configuration optionnelle

Dans votre fichier `.env`, vous pouvez personnaliser le modèle d'embeddings :

```env
# Modèle d'embeddings (optionnel)
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2  # Par défaut
# Alternatives:
# - all-MiniLM-L6-v2 (plus rapide, moins bon pour le français)
# - all-mpnet-base-v2 (meilleure qualité, plus lent)
```

### 🔧 Fonctionnement Technique

#### Architecture de la Recherche

```
┌─────────────────────────────────────────────────────────┐
│         Texte Utilisateur                               │
│    "Je me sens seul et perdu"                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│      Génération Embedding (Temps Réel)                  │
│  sentence-transformers → Vecteur [384 dimensions]       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│      Comparaison avec Embeddings Pré-calculés           │
│  Similarité Cosinus → TOP 20 versets                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│      Score Hybride                                      │
│  70% Similarité Vectorielle                             │
│  + 30% Correspondance Émotions/Thèmes                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│      Verset Sélectionné                                 │
│  "Car je connais les projets que j'ai formés sur vous"  │
│  Jérémie 29:11                                          │
└─────────────────────────────────────────────────────────┘
```

#### Étapes Détaillées

1. **Analyse du Texte Utilisateur** (Groq API)
   - Extrait émotions, thèmes et mots-clés
   - Exemple : `emotions=['solitude'], themes=['présence de Dieu']`

2. **Recherche Vectorielle** (Local, Gratuit)
   - Génère un embedding du texte utilisateur
   - Compare avec tous les embeddings pré-calculés des versets
   - Trouve les TOP 20 versets les plus similaires sémantiquement

3. **Score Hybride**
   - **70%** : Score de similarité vectorielle (compréhension sémantique)
   - **30%** : Score sémantique
     - 60% : Correspondance avec émotions/thèmes détectés
     - 40% : Correspondance avec mots-clés dans le contenu

4. **Sélection du Meilleur Verset**
   - Le verset avec le score combiné le plus élevé est sélectionné
   - Passé au LLM pour générer l'explication, la méditation et la prière

### 📊 Modèle d'Embeddings Utilisé

**Modèle par défaut** : `paraphrase-multilingual-MiniLM-L12-v2`

| Caractéristique | Valeur |
|-----------------|--------|
| **Dimension** | 384 |
| **Langues** | Multilingue (excellent pour le français) |
| **Vitesse** | Rapide (~100ms par verset) |
| **Qualité** | Bon équilibre qualité/vitesse |
| **Coût** | Gratuit (local) |

### 🔄 Quand Recalculer les Embeddings ?

#### ✅ Une seule fois suffit normalement

Les embeddings sont calculés **une seule fois** et stockés dans MongoDB (champ `embedding` de chaque verset). Le script est intelligent et vérifie automatiquement si un embedding existe déjà.

#### 🔁 Quand relancer le script ?

1. **Ajout de nouveaux versets** : Si vous importez de nouveaux versets dans MongoDB
2. **Changement de modèle** : Si vous changez `EMBEDDING_MODEL` dans `.env`
3. **Suppression accidentelle** : Si les embeddings ont été supprimés par erreur

#### 💡 Exemple d'utilisation

```bash
# Première fois : calcule TOUS les embeddings
python scripts/compute_embeddings.py --translation lsg
# Résultat : "Mis à jour: 31102, Ignorés: 0"

# Deuxième fois : ne fait rien (déjà calculés)
python scripts/compute_embeddings.py --translation lsg
# Résultat : "Mis à jour: 0, Ignorés: 31102"

# Si vous ajoutez 10 nouveaux versets, relancez :
python scripts/compute_embeddings.py --translation lsg
# Résultat : "Mis à jour: 10, Ignorés: 31102"
```

### ✨ Avantages de la Recherche Vectorielle

1. **Compréhension Sémantique** 🧠
   - Capture le sens, pas seulement les mots
   - "je suis triste" = "mon cœur est lourd" = "je pleure" → même résultat

2. **Flexibilité Linguistique** 🌍
   - Fonctionne avec différentes formulations
   - Comprend les synonymes et expressions variées

3. **Robustesse** 🛡️
   - Moins dépendant des collections de liaison (`versets_emotions`, `versets_themes`)
   - Fonctionne même si l'extraction d'émotions/thèmes échoue

4. **Performance** ⚡
   - Rapide même avec des milliers de versets
   - Gratuit (pas besoin d'API externe)
   - Local (pas de dépendance réseau)

5. **Pertinence** 🎯
   - Résultats toujours pertinents, peu importe les mots utilisés
   - Score hybride combine sémantique et métadonnées

### 🐛 Dépannage

#### Erreur : "Aucun verset avec embedding trouvé"

**Solution** : Exécutez le script de pré-calcul :
```bash
python scripts/compute_embeddings.py --translation lsg
```

#### Erreur : "ModuleNotFoundError: No module named 'sentence_transformers'"

**Solution** : Installez les dépendances :
```bash
pip install -r requirements.txt
```

#### Le script est lent

**Normal** : Le calcul initial peut prendre plusieurs minutes pour des milliers de versets. C'est normal et ne se fait qu'une seule fois.

#### Changer le modèle d'embeddings

1. Modifiez `EMBEDDING_MODEL` dans `.env`
2. Supprimez les embeddings existants (optionnel) :
   ```javascript
   // Dans MongoDB shell
   db.versets.updateMany({}, {$unset: {embedding: ""}})
   ```
3. Relancez le script :
   ```bash
   python scripts/compute_embeddings.py --translation lsg
   ```

### 📝 Notes Importantes

- ⚠️ **Les embeddings sont stockés dans MongoDB** : Chaque verset a un champ `embedding` (liste de 384 nombres)
- ⚠️ **Le calcul initial peut prendre du temps** : Quelques minutes pour des milliers de versets
- ✅ **Les embeddings sont réutilisés** : Calculés une seule fois, utilisés indéfiniment
- ✅ **Le script est idempotent** : Relancer est sans risque, il ne recalcule que ce qui manque
- ✅ **Fallback automatique** : Si les embeddings ne sont pas disponibles, le système utilise les méthodes traditionnelles

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
│   ├── Home/               # Module Home (recherche de versets)
│   │   ├── chains.py      # Chaînes LangChain (analyse + génération)
│   │   ├── retriever.py   # Recherche de versets (vectorielle + traditionnelle)
│   │   ├── embeddings.py  # Service d'embeddings vectoriels
│   │   └── schemas.py     # Modèles Pydantic
│   ├── scripts/           # Scripts utilitaires
│   │   └── compute_embeddings.py  # Pré-calcul des embeddings
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
- **Groq** pour l'API d'IA rapide et gratuite (llama-3.1-8b-instant)
- **LangChain** pour l'orchestration et la gestion de la mémoire conversationnelle
- **sentence-transformers** pour les embeddings vectoriels multilingues
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


## Diagramme de flux (Home)

┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : SAISIE UTILISATEUR (Frontend Flutter)              │
│  ────────────────────────────────────────────────────────────  │
│  L'utilisateur tape : "Je me sens seul et perdu"              │
│  + Sélectionne langue: "fr"                                   │
│  + Sélectionne traduction: "Louis Segond 1910"                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : RÉCEPTION API (backend/Home/__init__.py)           │
│  ────────────────────────────────────────────────────────────  │
│  POST /api/home/search                                         │
│  {                                                              │
│    "text": "Je me sens seul et perdu",                        │
│    "language": "fr",                                           │
│    "translation_id": "lsg",                                    │
│    "bible_version": "Louis Segond 1910"                        │
│  }                                                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 : ANALYSE DU TEXTE (chains.py)                       │
│  ────────────────────────────────────────────────────────────  │
│  🔍 Analyse avec Groq (llama-3.1-8b-instant)                  │
│                                                                 │
│  Input: "Je me sens seul et perdu"                            │
│  ↓                                                              │
│  Prompt: "Analyse le message et identifie émotions/thèmes"    │
│  ↓                                                              │
│  Output: AnalysisResult {                                      │
│    emotions: ['solitude'],                                     │
│    themes: ['présence de Dieu', 'guidance'],                   │
│    keywords: ['seul', 'perdu'],                                │
│    summary: "L'utilisateur exprime solitude..."               │
│  }                                                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 4 : RECHERCHE DU VERSET (retriever.py)                 │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  4.1. Construire la requête vectorielle                        │
│       query_text = "Je me sens seul et perdu"                 │
│                                                                 │
│  4.2. RECHERCHE VECTORIELLE (Prioritaire)                     │
│       ┌──────────────────────────────────────┐                │
│       │ Générer embedding du texte           │                │
│       │ sentence-transformers → [384 dims]   │                │
│       └──────────────┬───────────────────────┘                │
│                      │                                         │
│                      ▼                                         │
│       ┌──────────────────────────────────────┐                │
│       │ Comparer avec embeddings pré-calculés│                │
│       │ Similarité cosinus → TOP 20 versets  │                │
│       └──────────────┬───────────────────────┘                │
│                      │                                         │
│                      ▼                                         │
│       Résultats: [verset1 (score: 0.85),                     │
│                   verset2 (score: 0.82), ...]                 │
│                                                                 │
│  4.3. Recherche émotions/thèmes (pour score hybride)          │
│       - Chercher "solitude" dans collection "emotions"        │
│       - Chercher "présence de Dieu" dans "themes"             │
│       - Trouver versets liés via versets_emotions/themes      │
│                                                                 │
│  4.4. SCORE HYBRIDE                                            │
│       Pour chaque verset trouvé :                              │
│       Score final = (score_vectoriel × 0.7)                   │
│                 + (score_sémantique × 0.3)                    │
│                                                                 │
│       score_sémantique =                                       │
│         (correspondance_émotions_thèmes × 0.6)                │
│         + (correspondance_mots_clés × 0.4)                    │
│                                                                 │
│  4.5. Sélectionner le meilleur verset                         │
│       → Verset avec le score combiné le plus élevé            │
│       Exemple: Jérémie 29:11                                   │
│                                                                 │
│  4.6. Fallback (si recherche vectorielle échoue)              │
│       - Recherche regex dans contenu                           │
│       - Recherche par mots-clés                                │
│       - Verset aléatoire (dernier recours)                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼ VerseDocument
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 5 : GÉNÉRATION CONTENU SPIRITUEL (chains.py)           │
│  ────────────────────────────────────────────────────────────  │
│  🤖 Génération avec Groq (llama-3.1-8b-instant)               │
│                                                                 │
│  Input au LLM:                                                 │
│  {                                                              │
│    "verse_text": "Car je connais les projets...",             │
│    "verse_reference": "Jérémie 29:11",                        │
│    "user_message": "Je me sens seul et perdu",                │
│    "emotions": "solitude",                                     │
│    "themes": "présence de Dieu, guidance",                    │
│    "keywords": "seul, perdu",                                 │
│    "language": "fr"                                            │
│  }                                                              │
│                                                                 │
│  Prompt: "Tu es un pasteur. Génère :                          │
│           1. EXPLICATION du verset                            │
│           2. MÉDITATION personnelle                            │
│           3. PRIÈRE suggérée"                                 │
│                                                                 │
│  ↓                                                              │
│                                                                 │
│  Output: SpiritualContent {                                    │
│    explanation: "Ce verset nous rappelle que Dieu...",       │
│    meditation: "Prends un moment pour méditer...",            │
│    prayer: "Seigneur, merci pour ta parole..."                 │
│  }                                                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 6 : CONSTRUCTION RÉPONSE (__init__.py)                  │
│  ────────────────────────────────────────────────────────────  │
│  VerseResponse {                                                │
│    text: "Car je connais les projets...",                     │
│    reference: "Jérémie 29:11",                                │
│    explanation: "...",                                         │
│    meditation: "...",                                         │
│    prayer: "...",                                              │
│    keywords: ["seul", "perdu"],                               │
│    metadata: {                                                 │
│      translation: "lsg",                                      │
│      book: "Jérémie",                                         │
│      chapter: 29,                                             │
│      verse: 11                                                │
│    }                                                            │
│  }                                                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼ HTTP 200 OK
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 7 : AFFICHAGE (Frontend Flutter)                        │
│  ────────────────────────────────────────────────────────────  │
│  L'utilisateur voit :                                          │
│  ┌─────────────────────────────────────────┐                 │
│  │ 📖 Jérémie 29:11                        │                 │
│  │                                          │                 │
│  │ "Car je connais les projets que j'ai    │                 │
│  │  formés sur vous, dit l'Éternel..."     │                 │
│  │                                          │                 │
│  │ 💡 EXPLICATION                           │                 │
│  │ Ce verset nous rappelle que Dieu...     │                 │
│  │                                          │                 │
│  │ 🧘 MÉDITATION                            │                 │
│  │ Prends un moment pour méditer...        │                 │
│  │                                          │                 │
│  │ 🙏 PRIÈRE                                │                 │
│  │ Seigneur, merci pour ta parole...       │                 │
│  └─────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘