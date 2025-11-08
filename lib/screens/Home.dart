import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_auth/firebase_auth.dart';

import '../services/api_service.dart';

/// Modèle Verse compatible avec l'API et l'UI existante
class Verse {
  final String text;
  final String reference;
  final String explanation;
  final String? meditation;
  final String? prayer;
  final List<String> keywords;

  Verse({
    required this.text,
    required this.reference,
    required this.explanation,
    this.meditation,
    this.prayer,
    required this.keywords,
  });

  /// Convertit VerseResponse de l'API en Verse pour l'UI
  factory Verse.fromApiResponse(VerseResponse response) {
    return Verse(
      text: response.text,
      reference: response.reference,
      explanation: response.explanation,
      meditation: response.meditation,
      prayer: response.prayer,
      keywords: response.keywords,
    );
  }
}

class HomePage extends StatefulWidget {
  final Function(Verse, bool) onAddToHistory;

  const HomePage({Key? key, required this.onAddToHistory}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>
    with SingleTickerProviderStateMixin {
  final _inputController = TextEditingController();
  Verse? _currentVerse;
  bool _isLoading = false;
  bool _isFavorite = false;
  bool _isPlaying = false;

  late AnimationController _animationController;

  final List<String> _examplePrompts = [
    "Je me sens seul",
    "Je suis fatigué de tout",
    "J'ai peur de l'avenir",
    "Je doute de moi",
    "J'ai besoin de paix",
  ];

  final ApiService _apiService = ApiService.instance;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _inputController.dispose();
    super.dispose();
  }

  Future<void> _searchVerse(String text) async {
    if (text.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
      _isFavorite = false;
    });

    try {
      // Obtenir l'ID utilisateur Firebase si disponible
      final userId = FirebaseAuth.instance.currentUser?.uid;

      // Créer la requête pour l'API
      final request = VerseRequest(
        text: text.trim(),
        userId: userId,
        language: 'fr',
        includeAnalysis: true,
      );

      // Appeler l'API
      final response = await _apiService.searchVerse(request);

      // Convertir la réponse en Verse pour l'UI
      final verse = Verse.fromApiResponse(response);

      if (mounted) {
        setState(() {
          _currentVerse = verse;
          _isLoading = false;
        });

        widget.onAddToHistory(verse, false);
        _inputController.clear();
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });

        // Si le message est long (erreur de connexion), utiliser une dialog
        if (e.message.contains('\n') || e.message.length > 100) {
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text(
                'Erreur de connexion',
                style: TextStyle(color: Color(0xFF5D4037)),
              ),
              content: SingleChildScrollView(
                child: Text(e.message, style: const TextStyle(fontSize: 14)),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text(
                    'OK',
                    style: TextStyle(color: Color(0xFF8D6E63)),
                  ),
                ),
              ],
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(e.message),
              backgroundColor: Colors.red.shade700,
              duration: const Duration(seconds: 5),
              action: SnackBarAction(
                label: 'OK',
                textColor: Colors.white,
                onPressed: () {},
              ),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });

        // Message d'erreur plus convivial selon le type d'erreur
        String errorMessage;
        if (e.toString().contains('TimeoutException') ||
            e.toString().contains('timeout') ||
            e.toString().contains('temps')) {
          errorMessage =
              'La recherche prend plus de temps que prévu. '
              'Veuillez réessayer dans quelques instants.';
        } else {
          errorMessage = 'Erreur lors de la recherche: ${e.toString()}';
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
            backgroundColor: Colors.red.shade700,
            duration: const Duration(seconds: 5),
            action: SnackBarAction(
              label: 'OK',
              textColor: Colors.white,
              onPressed: () {},
            ),
          ),
        );
      }
    }
  }

  Future<void> _handleSubmit() async {
    if (_inputController.text.trim().isNotEmpty) {
      await _searchVerse(_inputController.text.trim());
    }
  }

  void _handleExampleClick(String example) {
    _searchVerse(example);
  }

  void _handleReset() {
    setState(() {
      _currentVerse = null;
      _isFavorite = false;
    });
  }

  void _toggleFavorite() {
    setState(() {
      _isFavorite = !_isFavorite;
    });
    if (_currentVerse != null) {
      widget.onAddToHistory(_currentVerse!, _isFavorite);
    }
  }

  void _handlePlay() {
    setState(() {
      _isPlaying = !_isPlaying;
    });

    if (_isPlaying) {
      Future.delayed(const Duration(seconds: 3), () {
        if (mounted) {
          setState(() {
            _isPlaying = false;
          });
        }
      });
    }
  }

  Future<void> _handleShare() async {
    if (_currentVerse != null) {
      final shareText =
          '"${_currentVerse!.text}"\n\n— ${_currentVerse!.reference}\n\nVia l\'app Parole du Moment';
      await Clipboard.setData(ClipboardData(text: shareText));

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Verset copié dans le presse-papier !'),
            backgroundColor: Color(0xFF8D6E63),
            duration: Duration(seconds: 2),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        child: _currentVerse == null ? _buildInputView() : _buildVerseView(),
      ),
    );
  }

  Widget _buildInputView() {
    return Container(
      key: const ValueKey('input'),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFFDFCFB), Color(0xFFF5F5F0), Color(0xFFFFF8E1)],
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              const SizedBox(height: 24),
              // Icône en haut
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  size: 32,
                  color: Color(0xFF8D6E63),
                ),
              ),
              const Spacer(),
              // Titre
              const Text(
                "Comment vous sentez-vous aujourd'hui ?",
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF5D4037),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              const Text(
                'Décrivez votre situation et recevez une parole inspirée',
                style: TextStyle(fontSize: 16, color: Color(0xFF8D6E63)),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              // Input
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: const Color(0xFF8D6E63).withOpacity(0.1),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Stack(
                  children: [
                    TextField(
                      controller: _inputController,
                      maxLines: 5,
                      enabled: !_isLoading,
                      decoration: const InputDecoration(
                        hintText: "Ex: Je me sens découragé aujourd'hui...",
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.fromLTRB(24, 24, 70, 24),
                      ),
                      onSubmitted: (_) => _handleSubmit(),
                    ),
                    Positioned(
                      bottom: 24,
                      right: 24,
                      child: ValueListenableBuilder<TextEditingValue>(
                        valueListenable: _inputController,
                        builder: (context, value, child) {
                          final isEmpty = value.text.trim().isEmpty;
                          return Container(
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [Color(0xFF8D6E63), Color(0xFF6D4C41)],
                              ),
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.2),
                                  blurRadius: 8,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            child: IconButton(
                              onPressed: isEmpty || _isLoading
                                  ? null
                                  : _handleSubmit,
                              icon: _isLoading
                                  ? AnimatedBuilder(
                                      animation: _animationController,
                                      builder: (context, child) {
                                        return Transform.rotate(
                                          angle:
                                              _animationController.value *
                                              2 *
                                              3.14159,
                                          child: const Icon(
                                            Icons.auto_awesome,
                                            color: Colors.white,
                                          ),
                                        );
                                      },
                                    )
                                  : const Icon(Icons.send, color: Colors.white),
                              padding: const EdgeInsets.all(12),
                              constraints: const BoxConstraints(),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              // Suggestions
              const Align(
                alignment: Alignment.centerLeft,
                child: Padding(
                  padding: EdgeInsets.only(left: 8),
                  child: Text(
                    'Suggestions :',
                    style: TextStyle(fontSize: 14, color: Color(0xFF8D6E63)),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _examplePrompts.asMap().entries.map((entry) {
                  return TweenAnimationBuilder<double>(
                    duration: Duration(milliseconds: 100 * entry.key),
                    tween: Tween(begin: 0.0, end: 1.0),
                    builder: (context, value, child) {
                      return Opacity(
                        opacity: value,
                        child: Transform.scale(
                          scale: 0.9 + (0.1 * value),
                          child: child,
                        ),
                      );
                    },
                    child: InkWell(
                      onTap: _isLoading
                          ? null
                          : () => _handleExampleClick(entry.value),
                      borderRadius: BorderRadius.circular(20),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: const Color(0xFF8D6E63).withOpacity(0.1),
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.05),
                              blurRadius: 4,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Text(
                          entry.value,
                          style: const TextStyle(
                            fontSize: 14,
                            color: Color(0xFF5D4037),
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const Spacer(),
              // Message d'analyse
              if (_isLoading)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(
                      color: const Color(0xFF8D6E63).withOpacity(0.1),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 8,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      AnimatedBuilder(
                        animation: _animationController,
                        builder: (context, child) {
                          return Transform.scale(
                            scale:
                                1.0 +
                                (0.2 *
                                    (0.5 -
                                        (_animationController.value - 0.5)
                                            .abs())),
                            child: Container(
                              width: 8,
                              height: 8,
                              decoration: const BoxDecoration(
                                color: Color(0xFFD4AF37),
                                shape: BoxShape.circle,
                              ),
                            ),
                          );
                        },
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        'Recherche de votre verset...',
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF5D4037),
                        ),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildVerseView() {
    if (_currentVerse == null) return const SizedBox.shrink();

    return Container(
      key: const ValueKey('verse'),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const SizedBox(height: 32),
            // Carte du verset
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: const Color(0xFF8D6E63).withOpacity(0.1),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Text(
                    '"${_currentVerse!.text}"',
                    style: const TextStyle(
                      fontSize: 18,
                      color: Color(0xFF5D4037),
                      height: 1.5,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '— ${_currentVerse!.reference}',
                    style: const TextStyle(
                      fontSize: 16,
                      color: Color(0xFFD4AF37),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Container(
                    height: 1,
                    color: const Color(0xFF8D6E63).withOpacity(0.1),
                  ),
                  const SizedBox(height: 16),
                  // Actions
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildActionButton(
                        icon: Icons.volume_up,
                        label: _isPlaying ? 'Lecture...' : 'Écouter',
                        onTap: _handlePlay,
                        isActive: _isPlaying,
                      ),
                      _buildActionButton(
                        icon: Icons.favorite,
                        label: 'Favori',
                        onTap: _toggleFavorite,
                        isActive: _isFavorite,
                        isFilled: _isFavorite,
                      ),
                      _buildActionButton(
                        icon: Icons.share,
                        label: 'Partager',
                        onTap: _handleShare,
                      ),
                      _buildActionButton(
                        icon: Icons.bookmark_add,
                        label: 'Sauver',
                        onTap: () {},
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            // Explication
            _buildInfoCard(
              emoji: '💡',
              title: 'Explication',
              content: _currentVerse!.explanation,
              gradient: null,
            ),
            if (_currentVerse!.meditation != null) ...[
              const SizedBox(height: 16),
              _buildInfoCard(
                emoji: '🧘',
                title: 'Méditation du jour',
                content: _currentVerse!.meditation!,
                gradient: const LinearGradient(
                  colors: [Color(0xFFFFF8E1), Color(0xFFF5F5F0)],
                ),
              ),
            ],
            if (_currentVerse!.prayer != null) ...[
              const SizedBox(height: 16),
              _buildInfoCard(
                emoji: '🙏',
                title: 'Prière suggérée',
                content: _currentVerse!.prayer!,
                gradient: const LinearGradient(
                  colors: [Color(0xFFF5F5F0), Color(0xFFEFEBE9)],
                ),
                isItalic: true,
              ),
            ],
            const SizedBox(height: 16),
            // Bouton retour
            SizedBox(
              width: double.infinity,
              height: 56,
              child: OutlinedButton(
                onPressed: _handleReset,
                style: OutlinedButton.styleFrom(
                  side: BorderSide(
                    color: const Color(0xFF8D6E63).withOpacity(0.1),
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  backgroundColor: Colors.white,
                ),
                child: const Text(
                  'Chercher une nouvelle parole',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF8D6E63),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    bool isActive = false,
    bool isFilled = false,
  }) {
    return InkWell(
      onTap: onTap,
      child: Column(
        children: [
          Icon(
            icon,
            size: 20,
            color: isActive ? const Color(0xFFD4AF37) : const Color(0xFF8D6E63),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: isActive
                  ? const Color(0xFFD4AF37)
                  : const Color(0xFF8D6E63),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard({
    required String emoji,
    required String title,
    required String content,
    Gradient? gradient,
    bool isItalic = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: gradient,
        color: gradient == null ? Colors.white : null,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: gradient != null
              ? const Color(0xFFD4AF37).withOpacity(0.2)
              : const Color(0xFF8D6E63).withOpacity(0.1),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$emoji $title',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF5D4037),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            content,
            style: TextStyle(
              fontSize: 14,
              color: const Color(0xFF6D4C41),
              height: 1.5,
              fontStyle: isItalic ? FontStyle.italic : FontStyle.normal,
            ),
          ),
        ],
      ),
    );
  }
}
