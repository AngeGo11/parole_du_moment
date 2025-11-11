import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

/// Modèle pour les préférences utilisateur
class ProfilePreferences {
  final bool notificationsEnabled;
  final String notificationTime;
  final bool darkMode;
  final String language;
  final String translationId;
  final bool autoPlay;

  ProfilePreferences({
    this.notificationsEnabled = true,
    this.notificationTime = '08:00',
    this.darkMode = false,
    this.language = 'fr',
    this.translationId = 'lsg',
    this.autoPlay = false,
  });

  factory ProfilePreferences.fromJson(Map<String, dynamic> json) {
    return ProfilePreferences(
      notificationsEnabled: json['notifications_enabled'] ?? true,
      notificationTime: json['notification_time'] ?? '08:00',
      darkMode: json['dark_mode'] ?? false,
      language: json['language'] ?? 'fr',
      translationId: json['translation_id'] ?? 'lsg',
      autoPlay: json['auto_play'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'notifications_enabled': notificationsEnabled,
      'notification_time': notificationTime,
      'dark_mode': darkMode,
      'language': language,
      'translation_id': translationId,
      'auto_play': autoPlay,
    };
  }
}

/// Modèle pour les statistiques utilisateur
class ProfileStats {
  final int versesRead;
  final int favorites;
  final int consecutiveDays;

  ProfileStats({
    this.versesRead = 0,
    this.favorites = 0,
    this.consecutiveDays = 0,
  });

  factory ProfileStats.fromJson(Map<String, dynamic> json) {
    return ProfileStats(
      versesRead: json['verses_read'] ?? 0,
      favorites: json['favorites'] ?? 0,
      consecutiveDays: json['consecutive_days'] ?? 0,
    );
  }
}

/// Modèle pour le profil complet
class Profile {
  final String userId;
  final ProfilePreferences preferences;
  final ProfileStats stats;

  Profile({
    required this.userId,
    required this.preferences,
    required this.stats,
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      userId: json['user_id'] ?? '',
      preferences: ProfilePreferences.fromJson(json['preferences'] ?? {}),
      stats: ProfileStats.fromJson(json['stats'] ?? {}),
    );
  }
}

/// Modèle pour une langue disponible
class Language {
  final String code;
  final String name;

  Language({required this.code, required this.name});

  factory Language.fromJson(Map<String, dynamic> json) {
    return Language(
      code: json['code'] ?? '',
      name: json['name'] ?? '',
    );
  }
}

/// Modèle pour une version biblique
class BibleVersion {
  final String id;
  final String name;
  final String abreviation;

  BibleVersion({
    required this.id,
    required this.name,
    required this.abreviation,
  });

  factory BibleVersion.fromJson(Map<String, dynamic> json) {
    return BibleVersion(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      abreviation: json['abreviation'] ?? '',
    );
  }
}

/// Service pour gérer le profil utilisateur
class ProfileService {
  ProfileService._();
  static final ProfileService instance = ProfileService._();

  /// Récupère le profil complet d'un utilisateur
  Future<Profile> getProfile(String userId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/api/profile/$userId');
      final response = await http
          .get(uri)
          .timeout(ApiConfig.requestTimeout);

      if (response.statusCode == 200) {
        final jsonData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        return Profile.fromJson(jsonData);
      } else {
        final errorData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        throw Exception(
          errorData['detail'] ?? 'Erreur lors de la récupération du profil',
        );
      }
    } catch (e) {
      throw Exception('Erreur lors de la récupération du profil: $e');
    }
  }

  /// Met à jour les préférences d'un utilisateur
  Future<Profile> updateProfile(
    String userId,
    ProfilePreferences preferences,
  ) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/api/profile/$userId');
      final response = await http
          .put(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(preferences.toJson()),
          )
          .timeout(ApiConfig.requestTimeout);

      if (response.statusCode == 200) {
        final jsonData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        return Profile.fromJson(jsonData);
      } else {
        final errorData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        throw Exception(
          errorData['detail'] ?? 'Erreur lors de la mise à jour du profil',
        );
      }
    } catch (e) {
      throw Exception('Erreur lors de la mise à jour du profil: $e');
    }
  }

  /// Récupère les langues disponibles
  Future<List<Language>> getLanguages() async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/api/profile/languages');
      final response = await http
          .get(uri)
          .timeout(ApiConfig.requestTimeout);

      if (response.statusCode == 200) {
        final jsonData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        final languagesList = jsonData['languages'] as List;
        return languagesList
            .map((lang) => Language.fromJson(lang as Map<String, dynamic>))
            .toList();
      } else {
        throw Exception('Erreur lors de la récupération des langues');
      }
    } catch (e) {
      throw Exception('Erreur lors de la récupération des langues: $e');
    }
  }

  /// Récupère les versions bibliques disponibles
  Future<List<BibleVersion>> getBibleVersions({String? language}) async {
    try {
      final uri = language != null
          ? Uri.parse(
              '${ApiConfig.baseUrl}/api/profile/bible-versions?language=$language',
            )
          : Uri.parse('${ApiConfig.baseUrl}/api/profile/bible-versions');
      final response = await http
          .get(uri)
          .timeout(ApiConfig.requestTimeout);

      if (response.statusCode == 200) {
        final jsonData =
            jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        final versionsList = jsonData['versions'] as List;
        return versionsList
            .map(
              (version) =>
                  BibleVersion.fromJson(version as Map<String, dynamic>),
            )
            .toList();
      } else {
        throw Exception('Erreur lors de la récupération des versions bibliques');
      }
    } catch (e) {
      throw Exception(
        'Erreur lors de la récupération des versions bibliques: $e',
      );
    }
  }
}

