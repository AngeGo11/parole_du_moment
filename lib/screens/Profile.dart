import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/firebase_auth_service.dart';
import '../services/profile_service.dart';
import '../providers/theme_provider.dart';
import '../constants/app_colors.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({Key? key}) : super(key: key);

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final FirebaseAuthService _authService = FirebaseAuthService();
  final ProfileService _profileService = ProfileService.instance;

  bool _isLoading = true;
  bool _isSaving = false;

  // Données du profil
  Profile? _profile;
  List<Language> _languages = [];
  List<BibleVersion> _bibleVersions = [];

  // États locaux des préférences
  bool _notificationsEnabled = true;
  String _notificationTime = '08:00';
  bool _darkMode = false;
  String _selectedLanguageCode = 'fr';
  String _selectedBibleVersionId = 'lsg';
  bool _autoPlay = false;

  // Statistiques
  int _versesRead = 0;
  int _favorites = 0;
  int _consecutiveDays = 0;

  @override
  void initState() {
    super.initState();
    _loadProfileData();
  }

  Future<void> _loadProfileData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final user = _authService.currentUser;
      if (user == null) return;

      // Charger le profil
      final profile = await _profileService.getProfile(user.uid);

      // Charger les langues disponibles
      final languages = await _profileService.getLanguages();

      // Charger les versions bibliques
      final bibleVersions = await _profileService.getBibleVersions(
        language: profile.preferences.language,
      );

      // Charger le thème depuis le provider
      final themeProvider = Provider.of<ThemeProvider>(context, listen: false);

      setState(() {
        _profile = profile;
        _languages = languages;
        _bibleVersions = bibleVersions;

        // Mettre à jour les états locaux
        _notificationsEnabled = profile.preferences.notificationsEnabled;
        _notificationTime = profile.preferences.notificationTime;
        _darkMode = profile.preferences.darkMode;
        _selectedLanguageCode = profile.preferences.language;
        _selectedBibleVersionId = profile.preferences.translationId;
        _autoPlay = profile.preferences.autoPlay;

        // Statistiques
        _versesRead = profile.stats.versesRead;
        _favorites = profile.stats.favorites;
        _consecutiveDays = profile.stats.consecutiveDays;

        // Synchroniser le thème avec le provider
        if (themeProvider.isDarkMode != _darkMode) {
          themeProvider.setDarkMode(_darkMode);
        }

        _isLoading = false;
      });
    } catch (e) {
      print('Erreur lors du chargement du profil: $e');
      setState(() {
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur lors du chargement: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _applyChanges() async {
    setState(() {
      _isSaving = true;
    });

    try {
      final user = _authService.currentUser;
      if (user == null) return;

      // Créer les préférences mises à jour
      final preferences = ProfilePreferences(
        notificationsEnabled: _notificationsEnabled,
        notificationTime: _notificationTime,
        darkMode: _darkMode,
        language: _selectedLanguageCode,
        translationId: _selectedBibleVersionId,
        autoPlay: _autoPlay,
      );

      // Mettre à jour le profil via l'API
      final updatedProfile = await _profileService.updateProfile(
        user.uid,
        preferences,
      );

      // Mettre à jour le thème dans le provider
      final themeProvider = Provider.of<ThemeProvider>(context, listen: false);
      await themeProvider.setDarkMode(_darkMode);

      // Recharger les versions bibliques si la langue a changé
      if (updatedProfile.preferences.language != _selectedLanguageCode) {
        final bibleVersions = await _profileService.getBibleVersions(
          language: updatedProfile.preferences.language,
        );
        setState(() {
          _bibleVersions = bibleVersions;
        });
      }

      // Synchroniser tous les états locaux avec le profil mis à jour
      setState(() {
        _profile = updatedProfile;

        // Mettre à jour les états locaux avec les valeurs du serveur
        _notificationsEnabled = updatedProfile.preferences.notificationsEnabled;
        _notificationTime = updatedProfile.preferences.notificationTime;
        _darkMode = updatedProfile.preferences.darkMode;
        _selectedLanguageCode = updatedProfile.preferences.language;
        _selectedBibleVersionId = updatedProfile.preferences.translationId;
        _autoPlay = updatedProfile.preferences.autoPlay;

        // Statistiques
        _versesRead = updatedProfile.stats.versesRead;
        _favorites = updatedProfile.stats.favorites;
        _consecutiveDays = updatedProfile.stats.consecutiveDays;

        _isSaving = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Préférences mises à jour avec succès'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      print('Erreur lors de la sauvegarde: $e');
      setState(() {
        _isSaving = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur lors de la sauvegarde: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _onLanguageChanged(String? languageCode) async {
    if (languageCode == null || languageCode == _selectedLanguageCode) return;

    setState(() {
      _selectedLanguageCode = languageCode;
    });

    // Recharger les versions bibliques pour la nouvelle langue
    try {
      final bibleVersions = await _profileService.getBibleVersions(
        language: languageCode,
      );

      setState(() {
        _bibleVersions = bibleVersions;
        // Réinitialiser la version sélectionnée si elle n'existe plus
        if (!_bibleVersions.any((v) => v.id == _selectedBibleVersionId)) {
          _selectedBibleVersionId = _bibleVersions.isNotEmpty
              ? _bibleVersions.first.id
              : 'lsg';
        }
      });
    } catch (e) {
      print('Erreur lors du chargement des versions: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = _authService.currentUser;
    final themeProvider = Provider.of<ThemeProvider>(context);

    if (_isLoading) {
      return Scaffold(
        body: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: themeProvider.isDarkMode
                  ? AppColors.darkGradient
                  : AppColors.lightGradient,
            ),
          ),
          child: const Center(child: CircularProgressIndicator()),
        ),
      );
    }

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: themeProvider.isDarkMode
                ? AppColors.darkGradient
                : AppColors.lightGradient,
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 16),
                // Header avec profil
                Container(
                  padding: const EdgeInsets.only(
                    top: 40,
                    bottom: 40,
                    left: 24,
                    right: 24,
                  ),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [Color(0xFF8D6E63), Color(0xFF6D4C41)],
                    ),
                    borderRadius: const BorderRadius.all(Radius.circular(30)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.15),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      // Avatar
                      Container(
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 3),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.2),
                              blurRadius: 12,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: CircleAvatar(
                          radius: 50,
                          backgroundColor: Colors.white,
                          child: Text(
                            user?.displayName?.substring(0, 1).toUpperCase() ??
                                user?.email?.substring(0, 1).toUpperCase() ??
                                'U',
                            style: const TextStyle(
                              fontSize: 36,
                              color: Color(0xFF8D6E63),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                      // Nom de l'utilisateur
                      Text(
                        user?.displayName ?? 'Utilisateur',
                        style: const TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      // Email
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(
                              Icons.email_outlined,
                              color: Colors.white,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              user?.email ?? '',
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.white.withOpacity(0.95),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                      // Sous-titre
                      Text(
                        'Personnalisez votre expérience',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white.withOpacity(0.85),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Statistiques
                _buildStatsSection(),
                const SizedBox(height: 16),
                // Notifications
                _buildNotificationsSection(),
                const SizedBox(height: 16),
                // Apparence
                _buildAppearanceSection(),
                const SizedBox(height: 16),
                // Langue et Version
                _buildLanguageSection(),
                const SizedBox(height: 16),
                // Lecture audio
                _buildAudioSection(),
                const SizedBox(height: 16),
                // Plan de lecture
                _buildReadingPlanSection(),
                const SizedBox(height: 16),
                // Bouton pour appliquer les changements
                _buildApplyButton(),
                const SizedBox(height: 24),
                // Déconnexion
                _buildLogoutSection(),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildApplyButton() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: SizedBox(
        width: double.infinity,
        height: 56,
        child: ElevatedButton(
          onPressed: _isSaving ? null : _applyChanges,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF8D6E63),
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            elevation: 8,
          ),
          child: _isSaving
              ? const SizedBox(
                  height: 24,
                  width: 24,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                  ),
                )
              : const Text(
                  'Appliquer les changements',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
        ),
      ),
    );
  }

  Widget _buildStatsSection() {
    final themeProvider = Provider.of<ThemeProvider>(context);
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: themeProvider.isDarkMode ? AppColors.darkCard : Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '📊 Mes statistiques',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: themeProvider.isDarkMode
                  ? AppColors.darkTextAccent
                  : AppColors.textDark,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  _versesRead.toString(),
                  'Versets lus',
                  Colors.amber,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  _favorites.toString(),
                  'Favoris',
                  Colors.red,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  _consecutiveDays.toString(),
                  'Jours de suite',
                  Colors.purple,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String value, String label, Color color) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: themeProvider.isDarkMode
                  ? AppColors.darkTextSecondary
                  : AppColors.primary,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationsSection() {
    final themeProvider = Provider.of<ThemeProvider>(context);
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: themeProvider.isDarkMode ? AppColors.darkCard : Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.notifications, color: AppColors.primary, size: 20),
              const SizedBox(width: 8),
              Text(
                'Notifications',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: themeProvider.isDarkMode
                      ? AppColors.darkTextPrimary
                      : AppColors.textDark,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Verset quotidien',
                      style: TextStyle(
                        fontSize: 14,
                        color: themeProvider.isDarkMode
                            ? AppColors.darkTextPrimary
                            : AppColors.textDark,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Recevez votre verset chaque jour',
                      style: TextStyle(
                        fontSize: 12,
                        color: themeProvider.isDarkMode
                            ? AppColors.darkTextSecondary
                            : AppColors.primary,
                      ),
                    ),
                  ],
                ),
              ),
              Switch(
                value: _notificationsEnabled,
                onChanged: (value) {
                  setState(() {
                    _notificationsEnabled = value;
                  });
                },
                activeColor: AppColors.primary,
              ),
            ],
          ),
          if (_notificationsEnabled) ...[
            const SizedBox(height: 16),
            TextField(
              decoration: InputDecoration(
                labelText: 'Heure de notification',
                hintText: _notificationTime,
                labelStyle: TextStyle(
                  color: themeProvider.isDarkMode
                      ? AppColors.darkTextSecondary
                      : null,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: themeProvider.isDarkMode,
                fillColor: themeProvider.isDarkMode
                    ? AppColors.darkCardElevated
                    : null,
              ),
              style: TextStyle(
                color: themeProvider.isDarkMode
                    ? AppColors.darkTextPrimary
                    : null,
              ),
              onChanged: (value) {
                setState(() {
                  _notificationTime = value;
                });
              },
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAppearanceSection() {
    final themeProvider = Provider.of<ThemeProvider>(context);
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: themeProvider.isDarkMode ? AppColors.darkCard : Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(
            _darkMode ? Icons.dark_mode : Icons.light_mode,
            color: AppColors.primary,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Thème sombre',
                  style: TextStyle(
                    fontSize: 14,
                    color: themeProvider.isDarkMode
                        ? Colors.white
                        : const Color(0xFF5D4037),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Mode nuit pour vos yeux',
                  style: TextStyle(
                    fontSize: 12,
                    color: themeProvider.isDarkMode
                        ? Colors.white70
                        : const Color(0xFF8D6E63),
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: _darkMode,
            onChanged: (value) {
              setState(() {
                _darkMode = value;
              });
            },
            activeColor: const Color(0xFF8D6E63),
          ),
        ],
      ),
    );
  }

  Widget _buildLanguageSection() {
    final themeProvider = Provider.of<ThemeProvider>(context);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: themeProvider.isDarkMode ? AppColors.darkCard : Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.language, color: AppColors.primary, size: 20),
              const SizedBox(width: 8),
              Text(
                'Langue & Version',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: themeProvider.isDarkMode
                      ? AppColors.darkTextPrimary
                      : AppColors.textDark,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            decoration: InputDecoration(
              labelText: 'Langue de l\'application',
              labelStyle: TextStyle(
                color: themeProvider.isDarkMode ? Colors.white70 : null,
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: themeProvider.isDarkMode,
              fillColor: themeProvider.isDarkMode
                  ? const Color(0xFF1E1E1E)
                  : null,
            ),
            value: _selectedLanguageCode,
            dropdownColor: themeProvider.isDarkMode ? AppColors.darkCard : null,
            style: TextStyle(
              color: themeProvider.isDarkMode
                  ? AppColors.darkTextPrimary
                  : null,
            ),
            items: _languages.map((language) {
              return DropdownMenuItem<String>(
                value: language.code,
                child: Text(language.name),
              );
            }).toList(),
            onChanged: _onLanguageChanged,
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            decoration: InputDecoration(
              labelText: 'Version de la Bible',
              labelStyle: TextStyle(
                color: themeProvider.isDarkMode ? Colors.white70 : null,
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: themeProvider.isDarkMode,
              fillColor: themeProvider.isDarkMode
                  ? const Color(0xFF1E1E1E)
                  : null,
            ),
            value: _selectedBibleVersionId,
            dropdownColor: themeProvider.isDarkMode ? AppColors.darkCard : null,
            style: TextStyle(
              color: themeProvider.isDarkMode
                  ? AppColors.darkTextPrimary
                  : null,
            ),
            items: _bibleVersions.map((version) {
              return DropdownMenuItem<String>(
                value: version.id,
                child: Text(version.name),
              );
            }).toList(),
            onChanged: (value) {
              if (value != null) {
                setState(() {
                  _selectedBibleVersionId = value;
                });
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAudioSection() {
    final themeProvider = Provider.of<ThemeProvider>(context);
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: themeProvider.isDarkMode ? AppColors.darkCard : Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(Icons.volume_up, color: AppColors.primary, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Lecture automatique',
                  style: TextStyle(
                    fontSize: 14,
                    color: themeProvider.isDarkMode
                        ? Colors.white
                        : const Color(0xFF5D4037),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Écouter les versets automatiquement',
                  style: TextStyle(
                    fontSize: 12,
                    color: themeProvider.isDarkMode
                        ? Colors.white70
                        : const Color(0xFF8D6E63),
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: _autoPlay,
            onChanged: (value) {
              setState(() {
                _autoPlay = value;
              });
            },
            activeColor: const Color(0xFF8D6E63),
          ),
        ],
      ),
    );
  }

  Widget _buildReadingPlanSection() {
    final themeProvider = Provider.of<ThemeProvider>(context);
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: themeProvider.isDarkMode
            ? LinearGradient(
                colors: [AppColors.darkCardElevated, AppColors.darkCard],
              )
            : LinearGradient(
                colors: [Colors.purple.shade50, Colors.pink.shade50],
              ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.menu_book,
                color: themeProvider.isDarkMode
                    ? AppColors.darkTextAccent
                    : AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Plan de lecture',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: themeProvider.isDarkMode
                      ? AppColors.darkTextAccent
                      : AppColors.textDark,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Suivez un parcours spirituel guidé par thème',
            style: TextStyle(
              fontSize: 14,
              color: themeProvider.isDarkMode
                  ? AppColors.darkTextSecondary
                  : AppColors.primaryDark,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF8D6E63),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 8,
              ),
              child: const Text(
                'Découvrir les plans',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLogoutSection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: SizedBox(
        width: double.infinity,
        height: 56,
        child: OutlinedButton.icon(
          onPressed: () async {
            await _authService.signOut();
          },
          style: OutlinedButton.styleFrom(
            side: const BorderSide(color: Colors.red, width: 2),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
          ),
          icon: const Icon(Icons.logout, color: Colors.red),
          label: const Text(
            'Se déconnecter',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: Colors.red,
            ),
          ),
        ),
      ),
    );
  }
}
