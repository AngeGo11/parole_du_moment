import 'package:flutter/foundation.dart';

class ApiConfig {
  ApiConfig._();

  /// Base URL du backend. S'adapte automatiquement selon la plateforme.
  static String get baseUrl {
    // Vérifier si l'URL est définie via une variable d'environnement
    const envUrl = String.fromEnvironment('API_BASE_URL');
    if (envUrl.isNotEmpty) {
      return envUrl;
    }

    // Détection automatique selon la plateforme
    if (kIsWeb) {
      // Pour le web, utiliser 127.0.0.1 qui est plus fiable que localhost
      return 'http://127.0.0.1:8000';
    }

    // Pour les plateformes mobiles, utiliser defaultTargetPlatform
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        // Android émulateur : 10.0.2.2 pointe vers localhost de la machine hôte
        // Android appareil physique : utiliser l'IP locale de votre machine
        // Exemple: http://192.168.1.XXX:8000 (remplacez XXX par votre IP)
        return 'http://10.0.2.2:8000';

      case TargetPlatform.iOS:
        // iOS simulateur : localhost fonctionne directement
        // iOS appareil physique : utiliser l'IP locale de votre machine
        // Exemple: http://192.168.1.XXX:8000 (remplacez XXX par votre IP)
        return 'http://localhost:8000';

      default:
        // Par défaut pour les autres plateformes (Windows, macOS, Linux)
        return 'http://localhost:8000';
    }
  }

  // Timeout augmenté pour permettre les appels LLM (analyse + génération spirituelle)
  static const Duration requestTimeout = Duration(seconds: 60);

  static Uri homeSearchUri() => Uri.parse('$baseUrl/api/home/search');
}
