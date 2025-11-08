# Configuration Ollama pour l'Assistant Spirituel

## Installation d'Ollama

1. **Télécharger Ollama** : https://ollama.ai/download
2. **Installer** selon votre système d'exploitation
3. **Démarrer Ollama** (démarre automatiquement un serveur local sur `http://localhost:11434`)

## Télécharger Mistral 7B

```bash
ollama pull mistral:7b
```

Cela télécharge le modèle Mistral 7B (~4GB) et le rend disponible localement.

## Configuration dans le backend

### Variables d'environnement (.env)

Ajoutez ces variables dans votre fichier `.env` :

```env
# Ollama Configuration (optionnel - valeurs par défaut)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=mistral:7b
```

### Vérifier que Ollama fonctionne

```bash
# Tester Ollama directement
ollama run mistral:7b "Bonjour, comment allez-vous ?"

# Ou via curl
curl http://localhost:11434/api/generate -d '{
  "model": "mistral:7b",
  "prompt": "Bonjour, comment allez-vous ?"
}'
```

## Utilisation

Une fois Ollama démarré avec Mistral 7B, l'API Assistant est prête à être utilisée.

### Endpoint principal

```
POST /api/assistant/chat
```

Body:
```json
{
  "user_id": "firebase_uid",
  "message": "Je me sens découragé",
  "conversation_id": null,  // Optionnel pour nouvelle conversation
  "language": "fr"
}
```

## Dépannage

### Ollama ne démarre pas
- Vérifiez que le port 11434 n'est pas utilisé
- Redémarrez Ollama : `ollama serve`

### Modèle non trouvé
- Vérifiez que Mistral 7B est téléchargé : `ollama list`
- Si absent, téléchargez-le : `ollama pull mistral:7b`

### Erreur de connexion
- Vérifiez que Ollama est démarré : `curl http://localhost:11434/api/tags`
- Vérifiez l'URL dans `.env` : `OLLAMA_BASE_URL=http://localhost:11434/v1`

## Alternatives

Si vous préférez utiliser un autre modèle Ollama :

```bash
# Modèles disponibles
ollama list

# Autres modèles français recommandés
ollama pull mistral:7b-instruct-q4_K_M  # Version quantifiée (plus légère)
ollama pull llama2:7b                    # Alternative
ollama pull codellama:7b                 # Pour le code si besoin
```

Puis mettez à jour `.env` :
```env
OLLAMA_MODEL=mistral:7b-instruct-q4_K_M
```

