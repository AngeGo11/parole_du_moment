import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:share_plus/share_plus.dart';
import 'package:intl/intl.dart';
import 'package:intl/date_symbol_data_local.dart';

class DailyVerse {
  final String text;
  final String reference;
  final String explanation;
  final String? meditation;
  final String? prayer;

  DailyVerse({
    required this.text,
    required this.reference,
    required this.explanation,
    this.meditation,
    this.prayer,
  });
}

// Fonction pour obtenir le verset du jour (à adapter selon votre logique)
DailyVerse getDailyVerse() {
  return DailyVerse(
    text:
        'Car Dieu a tant aimé le monde qu\'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu\'il ait la vie éternelle.',
    reference: 'Jean 3:16',
    explanation:
        'Ce verset est au cœur de l\'Évangile. Il révèle l\'amour inconditionnel de Dieu pour l\'humanité et son plan de salut à travers Jésus-Christ. C\'est un message d\'espérance qui nous rappelle que la vie éternelle est un don gratuit offert à tous ceux qui croient.',
    meditation:
        'Prenez un moment pour réfléchir à l\'immensité de l\'amour de Dieu. Comment pouvez-vous partager cet amour avec ceux qui vous entourent aujourd\'hui ?',
    prayer:
        'Père céleste, merci pour ton amour infini. Aide-moi à comprendre la profondeur de ton sacrifice et à vivre chaque jour dans la reconnaissance de ce don précieux. Amen.',
  );
}

class DailyVersePage extends StatefulWidget {
  const DailyVersePage({Key? key}) : super(key: key);

  @override
  State<DailyVersePage> createState() => _DailyVersePageState();
}

class _DailyVersePageState extends State<DailyVersePage>
    with SingleTickerProviderStateMixin {
  late DailyVerse dailyVerse;
  bool isFavorite = false;
  bool isPlaying = false;
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _initializeLocale();
    dailyVerse = getDailyVerse();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _animationController.forward();
  }

  Future<void> _initializeLocale() async {
    await initializeDateFormatting('fr_FR', null);
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void handlePlay() {
    setState(() {
      isPlaying = !isPlaying;
    });
    if (isPlaying) {
      Future.delayed(const Duration(seconds: 3), () {
        if (mounted) {
          setState(() {
            isPlaying = false;
          });
        }
      });
    }
  }

  Future<void> handleShare() async {
    final shareText =
        'Verset du jour:\n\n"${dailyVerse.text}"\n\n— ${dailyVerse.reference}\n\nVia l\'app Parole du Moment';

    try {
      await Share.share(shareText, subject: 'Verset du Jour');
    } catch (e) {
      // Fallback: copier dans le presse-papier
      await Clipboard.setData(ClipboardData(text: shareText));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Verset copié dans le presse-papier !'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    }
  }

  String getFormattedDate() {
    final now = DateTime.now();
    return DateFormat('EEEE d MMMM yyyy', 'fr_FR').format(now);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 700),
            child: Column(
              children: [
                const SizedBox(height: 24),
                _buildHeader(),
                const SizedBox(height: 32),
                _buildMainCard(),
                const SizedBox(height: 24),
                _buildExplanation(),
                if (dailyVerse.meditation != null) ...[
                  const SizedBox(height: 16),
                  _buildMeditation(),
                ],
                if (dailyVerse.prayer != null) ...[
                  const SizedBox(height: 16),
                  _buildPrayer(),
                ],
                const SizedBox(height: 16),
                _buildNotificationInfo(),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return FadeTransition(
      opacity: _animationController,
      child: SlideTransition(
        position: Tween<Offset>(begin: const Offset(0, -0.5), end: Offset.zero)
            .animate(
              CurvedAnimation(
                parent: _animationController,
                curve: Curves.easeOut,
              ),
            ),
        child: Column(
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFFd4af37), Color(0xFF8d6e63)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.wb_sunny, color: Colors.white, size: 32),
            ),
            const SizedBox(height: 16),
            const Text(
              'Verset du Jour',
              style: TextStyle(
                color: Color(0xFF5d4037),
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.calendar_today,
                  color: Color(0xFF8d6e63),
                  size: 16,
                ),
                const SizedBox(width: 8),
                Text(
                  getFormattedDate(),
                  style: const TextStyle(
                    color: Color(0xFF8d6e63),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMainCard() {
    return TweenAnimationBuilder<double>(
      duration: const Duration(milliseconds: 600),
      tween: Tween(begin: 0.0, end: 1.0),
      curve: Curves.easeOut,
      builder: (context, value, child) {
        return Opacity(
          opacity: value,
          child: Transform.translate(
            offset: Offset(0, 20 * (1 - value)),
            child: child,
          ),
        );
      },
      child: Container(
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF8d6e63), Color(0xFF6d4c41)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        padding: const EdgeInsets.all(32),
        child: Column(
          children: [
            Text(
              '"${dailyVerse.text}"',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                height: 1.6,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              '— ${dailyVerse.reference}',
              style: const TextStyle(color: Color(0xFFf5deb3), fontSize: 16),
            ),
            const SizedBox(height: 24),
            Container(
              decoration: BoxDecoration(
                border: Border(
                  top: BorderSide(color: Colors.white.withOpacity(0.2)),
                ),
              ),
              padding: const EdgeInsets.only(top: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildActionButton(
                    icon: Icons.volume_up,
                    label: isPlaying ? 'Lecture...' : 'Écouter',
                    onTap: handlePlay,
                    isActive: isPlaying,
                  ),
                  _buildActionButton(
                    icon: isFavorite ? Icons.favorite : Icons.favorite_border,
                    label: 'Favori',
                    onTap: () {
                      setState(() {
                        isFavorite = !isFavorite;
                      });
                    },
                    isActive: isFavorite,
                    activeColor: const Color(0xFFd4af37),
                  ),
                  _buildActionButton(
                    icon: Icons.share,
                    label: 'Partager',
                    onTap: handleShare,
                  ),
                ],
              ),
            ),
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
    Color? activeColor,
  }) {
    final color = isActive
        ? (activeColor ?? Colors.white)
        : Colors.white.withOpacity(0.8);

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 4),
            Text(label, style: TextStyle(color: color, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _buildExplanation() {
    return _buildAnimatedCard(
      delay: 300,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFF8d6e63).withOpacity(0.1)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 15,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '💡 Réflexion',
              style: TextStyle(
                color: Color(0xFF5d4037),
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              dailyVerse.explanation,
              style: const TextStyle(
                color: Color(0xFF6d4c41),
                fontSize: 15,
                height: 1.6,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMeditation() {
    return _buildAnimatedCard(
      delay: 400,
      child: Container(
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFFfff8e1), Color(0xFFf5f5f0)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFFd4af37).withOpacity(0.2)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 15,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '🧘 Pour méditer aujourd\'hui',
              style: TextStyle(
                color: Color(0xFF5d4037),
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              dailyVerse.meditation!,
              style: const TextStyle(
                color: Color(0xFF6d4c41),
                fontSize: 15,
                height: 1.6,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPrayer() {
    return _buildAnimatedCard(
      delay: 500,
      child: Container(
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFFf5f5f0), Color(0xFFefebe9)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFF8d6e63).withOpacity(0.1)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 15,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '🙏 Prière du jour',
              style: TextStyle(
                color: Color(0xFF5d4037),
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              dailyVerse.prayer!,
              style: const TextStyle(
                color: Color(0xFF6d4c41),
                fontSize: 15,
                height: 1.6,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationInfo() {
    return _buildAnimatedCard(
      delay: 600,
      child: Container(
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFFfff8e1), Color(0xFFf5f5f0)],
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFd4af37).withOpacity(0.2)),
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              '💌 Recevez votre verset quotidien',
              style: TextStyle(
                color: Color(0xFF5d4037),
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              'Activez les notifications dans les paramètres',
              style: TextStyle(color: const Color(0xFF8d6e63), fontSize: 12),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnimatedCard({required int delay, required Widget child}) {
    return TweenAnimationBuilder<double>(
      duration: Duration(milliseconds: 600 + delay),
      tween: Tween(begin: 0.0, end: 1.0),
      curve: Curves.easeOut,
      builder: (context, value, childWidget) {
        return Opacity(
          opacity: value,
          child: Transform.translate(
            offset: Offset(0, 20 * (1 - value)),
            child: childWidget,
          ),
        );
      },
      child: child,
    );
  }
}
