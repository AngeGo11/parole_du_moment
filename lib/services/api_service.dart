import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

/// Modèle pour la requête de recherche de verset
class VerseRequest {
  final String text;
  final String? userId;
  final String language;
  final bool includeAnalysis;

  VerseRequest({
    required this.text,
    this.userId,
    this.language = 'fr',
    this.includeAnalysis = true,
  });

  Map<String, dynamic> toJson() => {
    'text': text,
    if (userId != null) 'user_id': userId,
    'language': language,
    'include_analysis': includeAnalysis,
  };
}

/// Modèle pour les métadonnées du verset
class VerseMetadata {
  final String? translation;
  final String? book;
  final int? chapter;
  final int? verse;

  VerseMetadata({this.translation, this.book, this.chapter, this.verse});

  factory VerseMetadata.fromJson(Map<String, dynamic> json) => VerseMetadata(
    translation: json['translation'] as String?,
    book: json['book'] as String?,
    chapter: json['chapter'] as int?,
    verse: json['verse'] as int?,
  );
}

/// Modèle pour le résultat d'analyse
class AnalysisResult {
  final List<String> emotions;
  final List<String> themes;
  final List<String> keywords;
  final String? summary;

  AnalysisResult({
    required this.emotions,
    required this.themes,
    required this.keywords,
    this.summary,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) => AnalysisResult(
    emotions: List<String>.from(json['emotions'] ?? []),
    themes: List<String>.from(json['themes'] ?? []),
    keywords: List<String>.from(json['keywords'] ?? []),
    summary: json['summary'] as String?,
  );
}

/// Modèle pour la réponse du verset
class VerseResponse {
  final String text;
  final String reference;
  final String explanation;
  final String? meditation;
  final String? prayer;
  final List<String> keywords;
  final VerseMetadata? metadata;
  final AnalysisResult? analysis;

  VerseResponse({
    required this.text,
    required this.reference,
    required this.explanation,
    this.meditation,
    this.prayer,
    required this.keywords,
    this.metadata,
    this.analysis,
  });

  factory VerseResponse.fromJson(Map<String, dynamic> json) => VerseResponse(
    text: json['text'] as String,
    reference: json['reference'] as String,
    explanation: json['explanation'] as String,
    meditation: json['meditation'] as String?,
    prayer: json['prayer'] as String?,
    keywords: List<String>.from(json['keywords'] ?? []),
    metadata: json['metadata'] != null
        ? VerseMetadata.fromJson(json['metadata'] as Map<String, dynamic>)
        : null,
    analysis: json['analysis'] != null
        ? AnalysisResult.fromJson(json['analysis'] as Map<String, dynamic>)
        : null,
  );
}

/// Modèle pour la requête à l'assistant
class AssistantRequest {
  final String userId;
  final String message;
  final String? conversationId;
  final String language;

  AssistantRequest({
    required this.userId,
    required this.message,
    this.conversationId,
    this.language = 'fr',
  });

  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'message': message,
    if (conversationId != null) 'conversation_id': conversationId,
    'language': language,
  };
}

/// Modèle pour le verset dans la réponse de l'assistant
class AssistantVerse {
  final String text;
  final String reference;

  AssistantVerse({required this.text, required this.reference});

  factory AssistantVerse.fromJson(Map<String, dynamic> json) => AssistantVerse(
    text: json['text'] as String,
    reference: json['reference'] as String,
  );
}

/// Modèle pour la réponse de l'assistant
class AssistantResponse {
  final String response;
  final AssistantVerse? verse;
  final String conversationId;
  final List<String> keywords;

  AssistantResponse({
    required this.response,
    this.verse,
    required this.conversationId,
    required this.keywords,
  });

  factory AssistantResponse.fromJson(Map<String, dynamic> json) => AssistantResponse(
    response: json['response'] as String,
    verse: json['verse'] != null
        ? AssistantVerse.fromJson(json['verse'] as Map<String, dynamic>)
        : null,
    conversationId: json['conversation_id'] as String,
    keywords: List<String>.from(json['keywords'] ?? []),
  );
}

/// Service API pour communiquer avec le backend
class ApiService {
  ApiService._();
  static final ApiService instance = ApiService._();

  /// Recherche un verset basé sur le texte de l'utilisateur
  Future<VerseResponse> searchVerse(VerseRequest request) async {
    try {
      final uri = ApiConfig.homeSearchUri();
      final baseUrl = ApiConfig.baseUrl;

      // Log pour le débogage
      print(
        '🔍 Plateforme: ${kIsWeb ? "Web" : defaultTargetPlatform.toString()}',
      );
      print('🔍 URL de base: $baseUrl');
      print('🔍 Tentative de connexion à: $uri');

      final response = await http
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(request.toJson()),
          )
          .timeout(ApiConfig.requestTimeout);

      if (response.statusCode == 200) {
        final jsonData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        return VerseResponse.fromJson(jsonData);
      } else if (response.statusCode == 400) {
        final errorData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        throw ApiException(
          message: errorData['detail'] as String? ?? 'Requête invalide',
          statusCode: response.statusCode,
        );
      } else if (response.statusCode == 404) {
        final errorData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        throw ApiException(
          message: errorData['detail'] as String? ?? 'Aucun verset trouvé',
          statusCode: response.statusCode,
        );
      } else if (response.statusCode == 500) {
        final errorData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        throw ApiException(
          message: errorData['detail'] as String? ?? 'Erreur serveur',
          statusCode: response.statusCode,
        );
      } else {
        throw ApiException(
          message: 'Erreur inattendue: ${response.statusCode}',
          statusCode: response.statusCode,
        );
      }
    } on TimeoutException {
      final uri = ApiConfig.homeSearchUri();
      throw ApiException(
        message:
            'La requête a pris trop de temps.\n\n'
            'Vérifiez que:\n'
            '• Le backend est démarré\n'
            '• Votre connexion internet fonctionne\n'
            '• L\'URL est correcte: $uri',
        statusCode: 0,
      );
    } on FormatException catch (e) {
      throw ApiException(
        message: 'Erreur de format de réponse: ${e.message}',
        statusCode: 0,
      );
    } on http.ClientException catch (e) {
      // Erreur de connexion réseau (serveur inaccessible, DNS, etc.)
      final uri = ApiConfig.homeSearchUri();
      final errorMsg = e.message.toLowerCase();

      String message = 'Impossible de se connecter au serveur.\n\n';
      message += 'Vérifiez que:\n';
      message += '• Le backend est démarré (python backend/app.py)\n';
      message += '• Vous êtes connecté au bon réseau\n';
      message += '• L\'URL est correcte: $uri\n';

      if (errorMsg.contains('failed') || errorMsg.contains('network')) {
        message += '\n⚠️ Erreur réseau détectée.';
      }

      message += '\n\nErreur: ${e.message}';

      throw ApiException(message: message, statusCode: 0);
    } catch (e) {
      if (e is ApiException) {
        rethrow;
      }

      // Erreur générique (peut être "failed to fetch" ou autre)
      final errorMsg = e.toString().toLowerCase();
      final uri = ApiConfig.homeSearchUri();

      if (errorMsg.contains('failed') ||
          errorMsg.contains('network') ||
          errorMsg.contains('connection') ||
          errorMsg.contains('socket') ||
          errorMsg.contains('fetch')) {
        throw ApiException(
          message:
              'Erreur de connexion réseau.\n\n'
              'Vérifiez que:\n'
              '• Le backend est démarré: python backend/app.py\n'
              '• Le backend écoute sur: $uri\n'
              '• Votre connexion internet fonctionne\n'
              '• Si vous êtes sur Android, utilisez http://10.0.2.2:8000\n'
              '• Si vous êtes sur iOS, utilisez http://localhost:8000\n\n'
              'Détails: ${e.toString()}',
          statusCode: 0,
        );
      }

      throw ApiException(
        message: 'Erreur inconnue: ${e.toString()}',
        statusCode: 0,
      );
    }
  }

  /// Envoie un message à l'assistant spirituel
  Future<AssistantResponse> chatWithAssistant(AssistantRequest request) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/api/assistant/chat');

      final response = await http
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(request.toJson()),
          )
          .timeout(ApiConfig.requestTimeout);

      if (response.statusCode == 200) {
        final jsonData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        return AssistantResponse.fromJson(jsonData);
      } else {
        final errorData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        throw ApiException(
          message: errorData['detail'] as String? ?? 'Erreur lors de la communication avec l\'assistant',
          statusCode: response.statusCode,
        );
      }
    } on TimeoutException {
      throw ApiException(
        message:
            'La requête a pris trop de temps.\n\n'
            'Vérifiez que:\n'
            '• Le backend est démarré\n'
            '• Ollama est démarré avec le modèle Mistral 7B\n'
            '• Votre connexion fonctionne',
        statusCode: 0,
      );
    } catch (e) {
      if (e is ApiException) {
        rethrow;
      }
      throw ApiException(
        message: 'Erreur lors de la communication avec l\'assistant: ${e.toString()}',
        statusCode: 0,
      );
    }
  }
}

/// Exception personnalisée pour les erreurs API
class ApiException implements Exception {
  final String message;
  final int statusCode;

  ApiException({required this.message, required this.statusCode});

  @override
  String toString() => message;
}
