import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

// Réutilisation des modèles
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

class FavoriteVerse {
  final Verse verse;
  final DateTime dateAdded;
  final String? note;

  FavoriteVerse({
    required this.verse,
    required this.dateAdded,
    this.note,
  });
}

class FavoritesPage extends StatefulWidget {
  final List<FavoriteVerse> favorites;
  final Function(String) onRemoveFavorite;
  final Function(String, String) onAddNote;

  const FavoritesPage({
    Key? key,
    required this.favorites,
    required this.onRemoveFavorite,
    required this.onAddNote,
  }) : super(key: key);

  @override
  State<FavoritesPage> createState() => _FavoritesPageState();
}

class _FavoritesPageState extends State<FavoritesPage> {
  FavoriteVerse? selectedVerse;
  String searchQuery = '';
  String sortBy = 'date'; // 'date', 'reference'

  // Couleurs de la palette spirituelle
  static const Color marronBible = Color(0xFF8D6E63);
  static const Color orDoux = Color(0xFFD4AF37);
  static const Color marronFonce = Color(0xFF6D4C41);
  static const Color marronTresFonce = Color(0xFF5D4037);
  static const Color beigeClair = Color(0xFFF5F5F0);
  static const Color jauneClairDoux = Color(0xFFFFF8E1);

  List<FavoriteVerse> get filteredFavorites {
    var filtered = widget.favorites;

    // Filtrage par recherche
    if (searchQuery.isNotEmpty) {
      filtered = filtered.where((fav) {
        return fav.verse.text.toLowerCase().contains(searchQuery.toLowerCase()) ||
            fav.verse.reference
                .toLowerCase()
                .contains(searchQuery.toLowerCase()) ||
            (fav.note?.toLowerCase().contains(searchQuery.toLowerCase()) ?? false);
      }).toList();
    }

    // Tri
    if (sortBy == 'date') {
      filtered.sort((a, b) => b.dateAdded.compareTo(a.dateAdded));
    } else if (sortBy == 'reference') {
      filtered.sort((a, b) => a.verse.reference.compareTo(b.verse.reference));
    }

    return filtered;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: beigeClair,
      body: Column(
        children: [
          // Header avec recherche
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [orDoux, marronBible],
              ),
              boxShadow: [
                BoxShadow(
                  color: marronBible.withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: SafeArea(
              bottom: false,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(
                          Icons.favorite,
                          color: Colors.white,
                          size: 28,
                        ),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Text(
                            'Mes Favoris',
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            '${widget.favorites.length}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    // Barre de recherche
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: TextField(
                        onChanged: (value) => setState(() => searchQuery = value),
                        style: const TextStyle(color: marronTresFonce),
                        decoration: InputDecoration(
                          hintText: 'Rechercher dans vos favoris...',
                          hintStyle: TextStyle(color: marronBible.withOpacity(0.5)),
                          prefixIcon: const Icon(Icons.search, color: marronBible),
                          suffixIcon: searchQuery.isNotEmpty
                              ? IconButton(
                            icon: const Icon(Icons.clear, color: marronBible),
                            onPressed: () =>
                                setState(() => searchQuery = ''),
                          )
                              : null,
                          border: InputBorder.none,
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 12,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    // Options de tri
                    Row(
                      children: [
                        const Text(
                          'Trier par:',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(width: 8),
                        _buildSortButton('Date', 'date'),
                        const SizedBox(width: 8),
                        _buildSortButton('Référence', 'reference'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Liste des favoris
          Expanded(
            child: filteredFavorites.isEmpty
                ? _buildEmptyState()
                : GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 1,
                mainAxisSpacing: 12,
                childAspectRatio: 1.8,
              ),
              itemCount: filteredFavorites.length,
              itemBuilder: (context, index) {
                return _buildFavoriteCard(filteredFavorites[index], index);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSortButton(String label, String value) {
    final isActive = sortBy == value;
    return InkWell(
      onTap: () => setState(() => sortBy = value),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isActive ? Colors.white : Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isActive ? marronBible : Colors.white,
            fontSize: 12,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
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
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [orDoux.withOpacity(0.3), marronBible.withOpacity(0.3)],
                ),
                borderRadius: BorderRadius.circular(40),
              ),
              child: const Icon(
                Icons.favorite_border,
                size: 40,
                color: marronBible,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              searchQuery.isNotEmpty
                  ? 'Aucun résultat trouvé'
                  : 'Aucun verset favori',
              style: const TextStyle(
                color: marronTresFonce,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              searchQuery.isNotEmpty
                  ? 'Essayez une autre recherche'
                  : 'Commencez à marquer vos versets préférés\navec le bouton ❤️',
              style: TextStyle(
                color: marronBible,
                fontSize: 14,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFavoriteCard(FavoriteVerse favorite, int index) {
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
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white,
              jauneClairDoux,
            ],
          ),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: orDoux.withOpacity(0.3),
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: marronBible.withOpacity(0.15),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () => _showVerseDetail(favorite),
            borderRadius: BorderRadius.circular(20),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [orDoux, marronBible],
                          ),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          Icons.favorite,
                          color: Colors.white,
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              favorite.verse.reference,
                              style: const TextStyle(
                                color: orDoux,
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              DateFormat('d MMM yyyy', 'fr_FR')
                                  .format(favorite.dateAdded),
                              style: TextStyle(
                                color: marronBible.withOpacity(0.7),
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                      ),
                      PopupMenuButton(
                        icon: Icon(Icons.more_vert, color: marronBible),
                        itemBuilder: (context) => [
                          PopupMenuItem(
                            child: Row(
                              children: const [
                                Icon(Icons.note_add, size: 20),
                                SizedBox(width: 8),
                                Text('Ajouter une note'),
                              ],
                            ),
                            onTap: () => _showAddNoteDialog(favorite),
                          ),
                          PopupMenuItem(
                            child: Row(
                              children: const [
                                Icon(Icons.share, size: 20),
                                SizedBox(width: 8),
                                Text('Partager'),
                              ],
                            ),
                          ),
                          PopupMenuItem(
                            child: Row(
                              children: const [
                                Icon(Icons.delete, size: 20, color: Colors.red),
                                SizedBox(width: 8),
                                Text('Retirer des favoris',
                                    style: TextStyle(color: Colors.red)),
                              ],
                            ),
                            onTap: () =>
                                widget.onRemoveFavorite(favorite.verse.id),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Expanded(
                    child: SingleChildScrollView(
                      child: Text(
                        '"${favorite.verse.text}"',
                        style: const TextStyle(
                          color: marronTresFonce,
                          fontSize: 15,
                          height: 1.6,
                          fontStyle: FontStyle.italic,
                        ),
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ),
                  if (favorite.note != null) ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.7),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                          color: orDoux.withOpacity(0.3),
                          width: 1,
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.note,
                            size: 16,
                            color: marronBible,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              favorite.note!,
                              style: TextStyle(
                                color: marronFonce,
                                fontSize: 12,
                                fontStyle: FontStyle.italic,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _showVerseDetail(FavoriteVerse favorite) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: Colors.transparent,
        child: TweenAnimationBuilder<double>(
          duration: const Duration(milliseconds: 250),
          tween: Tween(begin: 0.0, end: 1.0),
          builder: (context, value, child) {
            return Transform.scale(
              scale: 0.8 + (0.2 * value),
              child: Opacity(
                opacity: value,
                child: child,
              ),
            );
          },
          child: Container(
            constraints: const BoxConstraints(maxWidth: 500, maxHeight: 600),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Colors.white, jauneClairDoux],
              ),
              borderRadius: BorderRadius.circular(28),
              border: Border.all(
                color: orDoux.withOpacity(0.5),
                width: 2,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.3),
                  blurRadius: 30,
                  offset: const Offset(0, 15),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Header avec gradient
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [orDoux, marronBible],
                    ),
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(26),
                      topRight: Radius.circular(26),
                    ),
                  ),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.favorite,
                        color: Colors.white,
                        size: 24,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              favorite.verse.reference,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              'Ajouté le ${DateFormat('d MMMM yyyy', 'fr_FR').format(favorite.dateAdded)}',
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.9),
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        onPressed: () => Navigator.of(context).pop(),
                        icon: const Icon(Icons.close, color: Colors.white),
                      ),
                    ],
                  ),
                ),
                // Contenu scrollable
                Flexible(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Verset
                        Container(
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(
                              color: orDoux.withOpacity(0.3),
                              width: 1,
                            ),
                          ),
                          child: Text(
                            '"${favorite.verse.text}"',
                            style: const TextStyle(
                              color: marronTresFonce,
                              fontSize: 17,
                              height: 1.7,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),
                        // Explication
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: jauneClairDoux,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: const [
                                  Text(
                                    '💡',
                                    style: TextStyle(fontSize: 20),
                                  ),
                                  SizedBox(width: 8),
                                  Text(
                                    'Explication',
                                    style: TextStyle(
                                      color: marronTresFonce,
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Text(
                                favorite.verse.explanation,
                                style: TextStyle(
                                  color: marronFonce,
                                  fontSize: 14,
                                  height: 1.6,
                                ),
                              ),
                            ],
                          ),
                        ),
                        // Note personnelle
                        if (favorite.note != null) ...[
                          const SizedBox(height: 20),
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: marronBible.withOpacity(0.2),
                                width: 1,
                              ),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: const [
                                    Icon(
                                      Icons.note,
                                      color: marronBible,
                                      size: 20,
                                    ),
                                    SizedBox(width: 8),
                                    Text(
                                      'Ma note personnelle',
                                      style: TextStyle(
                                        color: marronTresFonce,
                                        fontSize: 14,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  favorite.note!,
                                  style: TextStyle(
                                    color: marronFonce,
                                    fontSize: 14,
                                    height: 1.5,
                                    fontStyle: FontStyle.italic,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                        const SizedBox(height: 24),
                        // Boutons d'action
                        Row(
                          children: [
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: () {
                                  Navigator.of(context).pop();
                                  _showAddNoteDialog(favorite);
                                },
                                icon: Icon(
                                  favorite.note != null
                                      ? Icons.edit_note
                                      : Icons.note_add,
                                  size: 20,
                                ),
                                label: Text(
                                  favorite.note != null
                                      ? 'Modifier la note'
                                      : 'Ajouter une note',
                                ),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: jauneClairDoux,
                                  foregroundColor: marronBible,
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  elevation: 0,
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: () {
                                  // Partager le verset
                                },
                                icon: const Icon(Icons.share, size: 20),
                                label: const Text('Partager'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: marronBible,
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  elevation: 0,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showAddNoteDialog(FavoriteVerse favorite) {
    final noteController = TextEditingController(text: favorite.note ?? '');

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: Row(
          children: const [
            Icon(Icons.note_add, color: marronBible),
            SizedBox(width: 12),
            Text(
              'Note personnelle',
              style: TextStyle(color: marronTresFonce),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              favorite.verse.reference,
              style: const TextStyle(
                color: orDoux,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: noteController,
              maxLines: 4,
              maxLength: 200,
              style: const TextStyle(color: marronTresFonce),
              decoration: InputDecoration(
                hintText: 'Ajoutez vos réflexions personnelles...',
                hintStyle: TextStyle(color: marronBible.withOpacity(0.5)),
                filled: true,
                fillColor: beigeClair,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: orDoux, width: 2),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              'Annuler',
              style: TextStyle(color: marronBible),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              widget.onAddNote(favorite.verse.id, noteController.text);
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('Note enregistrée'),
                  backgroundColor: marronBible,
                  behavior: SnackBarBehavior.floating,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: marronBible,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            child: const Text('Enregistrer'),
          ),
        ],
      ),
    );
  }
}