import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

// Modèle de données
class Verse {
  final String id;
  final String reference;
  final String text;
  final String explanation;

  Verse({
    required this.id,
    required this.reference,
    required this.text,
    required this.explanation,
  });
}

class VerseHistory {
  final Verse verse;
  final DateTime date;
  final bool isFavorite;

  VerseHistory({
    required this.verse,
    required this.date,
    required this.isFavorite,
  });
}

class HistoryPage extends StatefulWidget {
  final List<VerseHistory> history;
  final Function(String) onRemove;
  final Function(String) onToggleFavorite;

  const HistoryPage({
    Key? key,
    required this.history,
    required this.onRemove,
    required this.onToggleFavorite,
  }) : super(key: key);

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage>
    with SingleTickerProviderStateMixin {
  String activeTab = 'all';
  VerseHistory? selectedVerse;

  // Couleurs de la palette spirituelle
  static const Color marronBible = Color(0xFF8D6E63);
  static const Color orDoux = Color(0xFFD4AF37);
  static const Color marronFonce = Color(0xFF6D4C41);
  static const Color marronTresFonce = Color(0xFF5D4037);
  static const Color beigeClair = Color(0xFFF5F5F0);
  static const Color jauneClairDoux = Color(0xFFFFF8E1);

  List<VerseHistory> get filteredHistory {
    if (activeTab == 'favorites') {
      return widget.history.where((item) => item.isFavorite).toList();
    }
    return widget.history;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: beigeClair,
      body: Column(
        children: [
          // Header avec tabs
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(
                bottom: BorderSide(
                  color: marronBible.withOpacity(0.1),
                  width: 1,
                ),
              ),
            ),
            padding: const EdgeInsets.all(16),
            child: SafeArea(
              bottom: false,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Historique & Favoris',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: marronTresFonce,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: _buildTabButton(
                          label: 'Tous',
                          isActive: activeTab == 'all',
                          onTap: () => setState(() => activeTab = 'all'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _buildTabButton(
                          label: 'Favoris',
                          icon: Icons.favorite,
                          isActive: activeTab == 'favorites',
                          onTap: () => setState(() => activeTab = 'favorites'),
                          isFavoriteTab: true,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // Liste des versets
          Expanded(
            child: filteredHistory.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: filteredHistory.length,
              itemBuilder: (context, index) {
                return _buildVerseCard(filteredHistory[index], index);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabButton({
    required String label,
    IconData? icon,
    required bool isActive,
    required VoidCallback onTap,
    bool isFavoriteTab = false,
  }) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            decoration: BoxDecoration(
              gradient: isActive
                  ? LinearGradient(
                colors: isFavoriteTab
                    ? [orDoux, marronBible]
                    : [marronBible, marronFonce],
              )
                  : null,
              color: isActive ? null : beigeClair,
              borderRadius: BorderRadius.circular(12),
              boxShadow: isActive
                  ? [
                BoxShadow(
                  color: marronBible.withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                )
              ]
                  : null,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (icon != null) ...[
                  Icon(
                    icon,
                    size: 16,
                    color: isActive ? Colors.white : marronBible,
                  ),
                  const SizedBox(width: 4),
                ],
                Text(
                  label,
                  style: TextStyle(
                    color: isActive ? Colors.white : marronBible,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: beigeClair,
                borderRadius: BorderRadius.circular(32),
              ),
              child: Icon(
                activeTab == 'favorites' ? Icons.favorite : Icons.history,
                size: 32,
                color: marronBible,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              activeTab == 'favorites'
                  ? 'Aucun verset favori pour le moment'
                  : 'Aucun historique pour le moment',
              style: const TextStyle(
                color: marronFonce,
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              activeTab == 'favorites'
                  ? 'Marquez vos versets préférés avec ❤️'
                  : 'Recherchez des versets pour commencer',
              style: TextStyle(
                color: marronBible,
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVerseCard(VerseHistory item, int index) {
    return TweenAnimationBuilder<double>(
      duration: Duration(milliseconds: 300 + (index * 50)),
      tween: Tween(begin: 0.0, end: 1.0),
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
        margin: const EdgeInsets.only(bottom: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: marronBible.withOpacity(0.1),
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: marronBible.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () => setState(() => selectedVerse = item),
            borderRadius: BorderRadius.circular(16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            if (item.isFavorite)
                              const Padding(
                                padding: EdgeInsets.only(right: 8),
                                child: Icon(
                                  Icons.favorite,
                                  size: 16,
                                  color: orDoux,
                                ),
                              ),
                            Text(
                              item.verse.reference,
                              style: const TextStyle(
                                color: orDoux,
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '"${item.verse.text}"',
                          style: const TextStyle(
                            color: marronTresFonce,
                            fontSize: 14,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          DateFormat('d MMMM yyyy • HH:mm', 'fr_FR')
                              .format(item.date),
                          style: TextStyle(
                            color: marronBible,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  Column(
                    children: [
                      IconButton(
                        onPressed: () => setState(() => selectedVerse = item),
                        icon: const Icon(Icons.menu_book),
                        color: marronBible,
                        padding: const EdgeInsets.all(8),
                        constraints: const BoxConstraints(),
                        style: IconButton.styleFrom(
                          backgroundColor: jauneClairDoux,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      IconButton(
                        onPressed: () => widget.onRemove(item.verse.id),
                        icon: const Icon(Icons.delete_outline),
                        color: Colors.red,
                        padding: const EdgeInsets.all(8),
                        constraints: const BoxConstraints(),
                        style: IconButton.styleFrom(
                          backgroundColor: Colors.red.withOpacity(0.1),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  // Modal de détail du verset
  void _showVerseDetail(VerseHistory item) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: Colors.transparent,
        child: TweenAnimationBuilder<double>(
          duration: const Duration(milliseconds: 200),
          tween: Tween(begin: 0.0, end: 1.0),
          builder: (context, value, child) {
            return Transform.scale(
              scale: 0.9 + (0.1 * value),
              child: Opacity(
                opacity: value,
                child: child,
              ),
            );
          },
          child: Container(
            constraints: const BoxConstraints(maxWidth: 500),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(
                color: marronBible.withOpacity(0.1),
                width: 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '"${item.verse.text}"',
                      style: const TextStyle(
                        color: marronTresFonce,
                        fontSize: 16,
                        height: 1.6,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      '— ${item.verse.reference}',
                      style: const TextStyle(
                        color: orDoux,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 24),
                    Container(
                      padding: const EdgeInsets.only(top: 16),
                      decoration: BoxDecoration(
                        border: Border(
                          top: BorderSide(
                            color: marronBible.withOpacity(0.1),
                            width: 1,
                          ),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            '💡 Explication',
                            style: TextStyle(
                              color: marronTresFonce,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            item.verse.explanation,
                            style: TextStyle(
                              color: marronFonce,
                              fontSize: 14,
                              height: 1.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          backgroundColor: marronBible,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          elevation: 0,
                        ),
                        child: const Text(
                          'Fermer',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  void didUpdateWidget(HistoryPage oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Fermer le modal si le verset sélectionné est supprimé
    if (selectedVerse != null &&
        !widget.history.any((h) => h.verse.id == selectedVerse!.verse.id)) {
      setState(() => selectedVerse = null);
    }
  }
}