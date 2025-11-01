import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

import '../config/api_config.dart';

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

  final List<Verse> _verses = [
    Verse(
      text:
          "L'Éternel est près de ceux qui ont le cœur brisé, Et il sauve ceux qui ont l'esprit dans l'abattement.",
      reference: "Psaume 34:19",
      explanation:
          "Ce verset nous rappelle que dans nos moments de solitude et de tristesse, Dieu est particulièrement proche. Il n'est pas distant face à notre douleur, mais il s'en approche avec compassion.",
      meditation:
          "Prenez un moment pour réaliser que vous n'êtes jamais vraiment seul. La présence de Dieu est constante, même quand vous ne la ressentez pas. Il connaît chaque larme et chaque soupir.",
      prayer:
          "Seigneur, dans ma solitude, aide-moi à sentir Ta présence. Console mon cœur brisé et restaure mon esprit. Merci d'être toujours là pour moi.",
      keywords: ['seul', 'solitude', 'triste', 'tristesse', 'isolé'],
    ),
    Verse(
      text:
          "Venez à moi, vous tous qui êtes fatigués et chargés, et je vous donnerai du repos.",
      reference: "Matthieu 11:28",
      explanation:
          "Jésus nous invite à venir à lui avec nos fardeaux. Il ne nous juge pas pour notre fatigue, mais nous offre un lieu de repos et de réconfort.",
      meditation:
          "La fatigue que vous ressentez est réelle et valide. Jésus vous invite à déposer vos fardeaux à ses pieds. Vous n'avez pas à tout porter seul.",
      prayer:
          "Jésus, je suis fatigué et je porte tant de choses. Je viens à Toi pour trouver le repos dont mon âme a besoin. Prends mes fardeaux et renouvelle mes forces.",
      keywords: ['fatigué', 'fatigue', 'épuisé', 'lourd', 'fardeau'],
    ),
    Verse(
      text:
          "Ne crains rien, car je suis avec toi; Ne promène pas des regards inquiets, car je suis ton Dieu; Je te fortifie, je viens à ton secours.",
      reference: "Ésaïe 41:10",
      explanation:
          "Dieu nous assure de Sa présence constante et nous encourage à ne pas avoir peur. Il promet non seulement d'être avec nous, mais aussi de nous fortifier activement.",
      meditation:
          "L'avenir peut sembler incertain et effrayant. Mais rappelez-vous que Dieu marche déjà dans votre futur, préparant le chemin et vous fortifiant pour chaque étape.",
      prayer:
          "Père céleste, quand l'avenir m'effraie, rappelle-moi que Tu es déjà là-bas. Fortifie-moi et aide-moi à marcher avec confiance, sachant que Tu me soutiens.",
      keywords: ['peur', 'avenir', 'inquiet', 'anxieux', 'crainte', 'futur'],
    ),
    Verse(
      text: "Je puis tout par celui qui me fortifie.",
      reference: "Philippiens 4:13",
      explanation:
          "Ce verset nous rappelle que notre force ne vient pas de nous-mêmes, mais de Christ qui vit en nous. Avec Lui, nous pouvons surmonter tous les obstacles.",
      meditation:
          "Vos doutes sont normaux, mais ils ne définissent pas votre capacité. En Christ, vous avez accès à une force qui dépasse vos propres limites.",
      prayer:
          "Seigneur, dans mes moments de doute, rappelle-moi que ma force vient de Toi. Aide-moi à avoir confiance en Ta puissance qui agit en moi.",
      keywords: ['doute', 'confiance', 'capacité', 'force', 'capable'],
    ),
    Verse(
      text:
          "Je vous laisse la paix, je vous donne ma paix. Je ne vous donne pas comme le monde donne. Que votre cœur ne se trouble point, et ne s'alarme point.",
      reference: "Jean 14:27",
      explanation:
          "Jésus offre une paix qui est différente de celle du monde. Cette paix n'est pas l'absence de problèmes, mais la présence de Dieu au milieu des tempêtes.",
      meditation:
          "La paix de Christ n'est pas conditionnée par vos circonstances. Elle est un don permanent qui peut remplir votre cœur même dans les situations les plus difficiles.",
      prayer:
          "Seigneur Jésus, remplis mon cœur de Ta paix qui surpasse toute intelligence. Que cette paix garde mon esprit et calme mes inquiétudes.",
      keywords: ['paix', 'calme', 'tranquillité', 'sérénité', 'repos'],
    ),
  ];

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

  Verse _findMatchingVerse(String text) {
    final lowerText = text.toLowerCase();

    for (final verse in _verses) {
      if (verse.keywords.any((keyword) => lowerText.contains(keyword))) {
        return verse;
      }
    }

    // Verset par défaut
    return _verses[4]; // Paix
  }

  Future<void> _searchVerse(String text) async {
    setState(() {
      _isLoading = true;
      _isFavorite = false;
    });

    // Simuler un délai pour l'analyse AI
    await Future.delayed(const Duration(milliseconds: 1500));

    final verse = _findMatchingVerse(text);
    setState(() {
      _currentVerse = verse;
      _isLoading = false;
    });

    widget.onAddToHistory(verse, false);
    _inputController.clear();
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
                      child: Container(
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
                          onPressed:
                              _inputController.text.trim().isEmpty || _isLoading
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
