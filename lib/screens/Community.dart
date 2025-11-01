import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:intl/date_symbol_data_local.dart';

class CommunityPost {
  final String id;
  final String username;
  final String verse;
  final String reference;
  final String testimony;
  final int likes;
  final int comments;
  final DateTime date;

  CommunityPost({
    required this.id,
    required this.username,
    required this.verse,
    required this.reference,
    required this.testimony,
    required this.likes,
    required this.comments,
    required this.date,
  });
}

class CommunityPage extends StatefulWidget {
  const CommunityPage({Key? key}) : super(key: key);

  @override
  State<CommunityPage> createState() => _CommunityPageState();
}

class _CommunityPageState extends State<CommunityPage> {
  @override
  void initState() {
    super.initState();
    _initializeLocale();
  }

  Future<void> _initializeLocale() async {
    await initializeDateFormatting('fr_FR', null);
  }

  final List<CommunityPost> posts = [
    CommunityPost(
      id: '1',
      username: 'Marie L.',
      verse: 'Je puis tout par celui qui me fortifie.',
      reference: 'Philippiens 4:13',
      testimony:
          'Ce verset m\'a donné la force de surmonter une période difficile au travail. Dieu est fidèle ! 🙏',
      likes: 24,
      comments: 5,
      date: DateTime(2025, 10, 18),
    ),
    CommunityPost(
      id: '2',
      username: 'David K.',
      verse: 'L\'Éternel est près de ceux qui ont le cœur brisé.',
      reference: 'Psaume 34:19',
      testimony:
          'Dans ma solitude, ce verset a été une lumière. Je me sens moins seul maintenant.',
      likes: 18,
      comments: 3,
      date: DateTime(2025, 10, 17),
    ),
    CommunityPost(
      id: '3',
      username: 'Sarah M.',
      verse: 'Venez à moi, vous tous qui êtes fatigués et chargés.',
      reference: 'Matthieu 11:28',
      testimony:
          'Après des semaines d\'épuisement, j\'ai trouvé le repos en Jésus. Alléluia !',
      likes: 32,
      comments: 7,
      date: DateTime(2025, 10, 16),
    ),
  ];

  final Set<String> likedPosts = {};

  void toggleLike(String postId) {
    setState(() {
      if (likedPosts.contains(postId)) {
        likedPosts.remove(postId);
      } else {
        likedPosts.add(postId);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Header
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Color(0xFF8d6e63), Color(0xFF6d4c41)],
              ),
            ),
            padding: const EdgeInsets.fromLTRB(16, 48, 16, 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.people, color: Colors.white, size: 32),
                    const SizedBox(width: 12),
                    const Text(
                      'Communauté',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Partagez comment la Parole transforme votre vie',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),

          // Stats
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(
                bottom: BorderSide(
                  color: const Color(0xFF8d6e63).withOpacity(0.1),
                ),
              ),
            ),
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem(Icons.trending_up, '2.4K', 'Membres actifs'),
                _buildStatItem(Icons.message, '156', 'Témoignages'),
                _buildStatItem(Icons.favorite, '1.2K', 'Encouragements'),
              ],
            ),
          ),

          // Feed
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: posts.length + 1,
              itemBuilder: (context, index) {
                if (index < posts.length) {
                  return _buildPostCard(posts[index], index);
                } else {
                  return _buildShareCTA();
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(IconData icon, String value, String label) {
    return Column(
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: const Color(0xFFd4af37), size: 16),
            const SizedBox(width: 4),
            Text(
              value,
              style: const TextStyle(
                color: Color(0xFFd4af37),
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Color(0xFF8d6e63)),
        ),
      ],
    );
  }

  Widget _buildPostCard(CommunityPost post, int index) {
    final isLiked = likedPosts.contains(post.id);
    final likesCount = post.likes + (isLiked ? 1 : 0);

    return TweenAnimationBuilder<double>(
      duration: Duration(milliseconds: 300 + (index * 100)),
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
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF8d6e63).withOpacity(0.1)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header du post
            Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Color(0xFFd4af37), Color(0xFF8d6e63)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      post.username[0],
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        post.username,
                        style: const TextStyle(
                          color: Color(0xFF5d4037),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        DateFormat('d MMM', 'fr_FR').format(post.date),
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color(0xFF8d6e63),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Verset
            Container(
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFfff8e1), Color(0xFFf5f5f0)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: const Color(0xFFd4af37).withOpacity(0.2),
                ),
              ),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '"${post.verse}"',
                    style: const TextStyle(
                      color: Color(0xFF5d4037),
                      fontSize: 14,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '— ${post.reference}',
                    style: const TextStyle(
                      fontSize: 12,
                      color: Color(0xFFd4af37),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Témoignage
            Text(
              post.testimony,
              style: const TextStyle(color: Color(0xFF6d4c41), fontSize: 14),
            ),
            const SizedBox(height: 12),

            // Actions
            Container(
              decoration: BoxDecoration(
                border: Border(
                  top: BorderSide(
                    color: const Color(0xFF8d6e63).withOpacity(0.1),
                  ),
                ),
              ),
              padding: const EdgeInsets.only(top: 12),
              child: Row(
                children: [
                  InkWell(
                    onTap: () => toggleLike(post.id),
                    child: Row(
                      children: [
                        Icon(
                          isLiked ? Icons.favorite : Icons.favorite_border,
                          color: isLiked
                              ? const Color(0xFFd4af37)
                              : const Color(0xFF8d6e63),
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '$likesCount',
                          style: TextStyle(
                            fontSize: 14,
                            color: isLiked
                                ? const Color(0xFFd4af37)
                                : const Color(0xFF8d6e63),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 24),
                  Row(
                    children: [
                      const Icon(
                        Icons.chat_bubble_outline,
                        color: Color(0xFF8d6e63),
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${post.comments}',
                        style: const TextStyle(
                          fontSize: 14,
                          color: Color(0xFF8d6e63),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildShareCTA() {
    return TweenAnimationBuilder<double>(
      duration: const Duration(milliseconds: 700),
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
          gradient: const LinearGradient(
            colors: [Color(0xFFfff8e1), Color(0xFFf5f5f0)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFd4af37).withOpacity(0.3)),
        ),
        padding: const EdgeInsets.all(24),
        margin: const EdgeInsets.only(top: 8),
        child: Column(
          children: [
            const Icon(Icons.send, color: Color(0xFF8d6e63), size: 48),
            const SizedBox(height: 12),
            const Text(
              'Partagez votre témoignage',
              style: TextStyle(
                color: Color(0xFF5d4037),
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Comment la Parole de Dieu a-t-elle touché votre cœur aujourd\'hui ?',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Color(0xFF6d4c41)),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                // Action pour écrire un témoignage
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF8d6e63),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 12,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 4,
              ),
              child: const Text(
                'Écrire un témoignage',
                style: TextStyle(fontSize: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
