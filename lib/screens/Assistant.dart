import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class Message {
  final String id;
  final String role;
  final String content;
  final Verse? verse;
  final DateTime timestamp;

  Message({
    required this.id,
    required this.role,
    required this.content,
    this.verse,
    required this.timestamp,
  });
}

class Verse {
  final String text;
  final String reference;

  Verse({required this.text, required this.reference});
}

class AIResponse {
  final List<String> keywords;
  final String response;
  final Verse verse;

  AIResponse({
    required this.keywords,
    required this.response,
    required this.verse,
  });
}

class AssistantPage extends StatefulWidget {
  const AssistantPage({Key? key}) : super(key: key);

  @override
  State<AssistantPage> createState() => _AssistantPageState();
}

class _AssistantPageState extends State<AssistantPage>
    with SingleTickerProviderStateMixin {
  final _inputController = TextEditingController();
  final _scrollController = ScrollController();
  final List<Message> _messages = [];
  bool _isTyping = false;
  String? _copiedId;

  late AnimationController _typingAnimationController;

  final List<String> _suggestedPrompts = [
    "Comment puis-je renforcer ma foi ?",
    "J'ai du mal à pardonner quelqu'un",
    "Que dit la Bible sur l'anxiété ?",
    "Comment prier efficacement ?",
    "J'ai besoin de courage aujourd'hui",
    "Comment trouver la paix intérieure ?",
    "Quelle direction prendre dans ma vie ?",
    "Comment gérer mes relations ?",
  ];

  final List<AIResponse> _aiResponses = [
    AIResponse(
      keywords: ['foi', 'renforcer', 'croire'],
      response:
          "La foi se renforce par la lecture régulière de la Parole de Dieu, la prière constante et la communion avec d'autres croyants. L'apôtre Paul nous rappelle que la foi vient de ce qu'on entend, et ce qu'on entend vient de la parole de Christ.",
      verse: Verse(
        text:
            "Ainsi la foi vient de ce qu'on entend, et ce qu'on entend vient de la parole de Christ.",
        reference: "Romains 10:17",
      ),
    ),
    AIResponse(
      keywords: ['pardon', 'pardonner', 'rancune', 'rancœur'],
      response:
          "Le pardon est au cœur de l'enseignement chrétien. Jésus nous demande de pardonner comme nous avons été pardonnés. C'est un processus qui peut prendre du temps, mais qui libère notre cœur du ressentiment et nous rapproche de Dieu.",
      verse: Verse(
        text:
            "Supportez-vous les uns les autres, et, si l'un a sujet de se plaindre de l'autre, pardonnez-vous réciproquement. De même que Christ vous a pardonné, pardonnez-vous aussi.",
        reference: "Colossiens 3:13",
      ),
    ),
    AIResponse(
      keywords: ['anxiété', 'anxieux', 'inquiet', 'stress', 'peur', 'crainte'],
      response:
          "L'anxiété est une épreuve commune, mais Dieu nous invite à déposer nos fardeaux à Ses pieds. La Bible nous encourage à ne pas nous inquiéter mais à présenter nos demandes à Dieu par la prière avec des actions de grâces.",
      verse: Verse(
        text:
            "Ne vous inquiétez de rien; mais en toute chose faites connaître vos besoins à Dieu par des prières et des supplications, avec des actions de grâces.",
        reference: "Philippiens 4:6",
      ),
    ),
    AIResponse(
      keywords: ['prier', 'prière', 'prie'],
      response:
          "La prière efficace vient d'un cœur sincère et humble. Il ne s'agit pas de la longueur ou de l'éloquence, mais de l'authenticité de notre relation avec Dieu. Jésus nous enseigne à prier avec foi et persévérance.",
      verse: Verse(
        text:
            "Et tout ce que vous demanderez en mon nom, je le ferai, afin que le Père soit glorifié dans le Fils.",
        reference: "Jean 14:13",
      ),
    ),
    AIResponse(
      keywords: ['triste', 'tristesse', 'déprimé', 'seul', 'solitude'],
      response:
          "Dans les moments de tristesse et de solitude, souvenez-vous que Dieu est proche de ceux qui ont le cœur brisé. Il ne vous abandonne jamais et désire vous consoler et vous fortifier.",
      verse: Verse(
        text:
            "L'Éternel est près de ceux qui ont le cœur brisé, Et il sauve ceux qui ont l'esprit dans l'abattement.",
        reference: "Psaume 34:19",
      ),
    ),
    AIResponse(
      keywords: ['courage', 'force', 'faiblesse', 'faible'],
      response:
          "Dans votre faiblesse, la force de Dieu se manifeste pleinement. Ne vous découragez pas car c'est lorsque nous sommes faibles que nous sommes vraiment forts en Christ. Sa grâce vous suffit.",
      verse: Verse(
        text: "Je puis tout par celui qui me fortifie.",
        reference: "Philippiens 4:13",
      ),
    ),
    AIResponse(
      keywords: ['paix', 'calme', 'tranquillité'],
      response:
          "La paix de Dieu dépasse toute intelligence. Ce n'est pas l'absence de problèmes, mais la présence de Dieu au milieu des tempêtes. Jésus vous offre Sa paix, différente de celle que le monde donne.",
      verse: Verse(
        text:
            "Je vous laisse la paix, je vous donne ma paix. Je ne vous donne pas comme le monde donne. Que votre cœur ne se trouble point, et ne s'alarme point.",
        reference: "Jean 14:27",
      ),
    ),
    AIResponse(
      keywords: ['sagesse', 'décision', 'choix', 'direction'],
      response:
          "Lorsque vous manquez de sagesse pour une décision, demandez-la à Dieu qui donne à tous libéralement et sans reproche. Il promet de guider vos pas si vous Le cherchez de tout votre cœur.",
      verse: Verse(
        text:
            "Si quelqu'un d'entre vous manque de sagesse, qu'il la demande à Dieu, qui donne à tous simplement et sans reproche, et elle lui sera donnée.",
        reference: "Jacques 1:5",
      ),
    ),
  ];

  @override
  void initState() {
    super.initState();
    _typingAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    )..repeat();

    _messages.add(
      Message(
        id: '1',
        role: 'assistant',
        content:
            "Bonjour ! 🙏 Je suis votre assistant spirituel guidé par la Parole de Dieu. Je suis là pour vous accompagner dans votre marche spirituelle, répondre à vos questions et vous encourager avec les Écritures. Comment puis-je vous aider aujourd'hui ?",
        timestamp: DateTime.now(),
      ),
    );
  }

  @override
  void dispose() {
    _typingAnimationController.dispose();
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Message _getAIResponse(String userMessage) {
    final lowerMessage = userMessage.toLowerCase();

    for (final response in _aiResponses) {
      if (response.keywords.any((keyword) => lowerMessage.contains(keyword))) {
        return Message(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          role: 'assistant',
          content: response.response,
          verse: response.verse,
          timestamp: DateTime.now(),
        );
      }
    }

    return Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      role: 'assistant',
      content:
          "Je comprends votre préoccupation. La Bible contient de nombreuses sagesses pour guider nos vies. Pourriez-vous préciser davantage votre situation ou votre question spirituelle ?",
      timestamp: DateTime.now(),
    );
  }

  Future<void> _handleSend() async {
    if (_inputController.text.trim().isEmpty) return;

    final userMessage = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      role: 'user',
      content: _inputController.text.trim(),
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(userMessage);
      _isTyping = true;
    });

    _inputController.clear();
    _scrollToBottom();

    await Future.delayed(const Duration(milliseconds: 1500));

    final aiMessage = _getAIResponse(userMessage.content);
    setState(() {
      _messages.add(aiMessage);
      _isTyping = false;
    });

    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _handleCopy(String content, String messageId) {
    Clipboard.setData(ClipboardData(text: content));
    setState(() => _copiedId = messageId);
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) setState(() => _copiedId = null);
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Texte copié'),
        duration: Duration(seconds: 1),
        backgroundColor: Color(0xFF8D6E63),
      ),
    );
  }

  void _handleNewConversation() {
    setState(() {
      _messages.clear();
      _messages.add(
        Message(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          role: 'assistant',
          content:
              "Nouvelle conversation démarrée. Comment puis-je vous accompagner dans votre parcours spirituel aujourd'hui ?",
          timestamp: DateTime.now(),
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.white, Color(0xFFF5F5F5)],
          ),
        ),
        child: Column(
          children: [
            _buildHeader(),
            Expanded(child: _buildMessages()),
            if (_messages.length == 1) _buildSuggestions(),
            _buildInput(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 48, 16, 16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(
          bottom: BorderSide(color: const Color(0xFF8D6E63).withOpacity(0.1)),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF8D6E63), Color(0xFF6D4C41)],
              ),
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: const Icon(
              Icons.auto_awesome,
              size: 20,
              color: Colors.white,
            ),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Votre Assistant Spirituel',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF5D4037),
                  ),
                ),
                Text(
                  'Guidé par la Parole de Dieu',
                  style: TextStyle(fontSize: 12, color: Color(0xFF8D6E63)),
                ),
              ],
            ),
          ),
          if (_messages.length > 1)
            TextButton.icon(
              onPressed: _handleNewConversation,
              icon: const Icon(Icons.refresh, size: 16),
              label: const Text('Nouveau'),
              style: TextButton.styleFrom(
                foregroundColor: const Color(0xFF8D6E63),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildMessages() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: _messages.length + (_isTyping ? 1 : 0),
      itemBuilder: (context, index) {
        if (index == _messages.length && _isTyping) {
          return _buildTypingIndicator();
        }

        final message = _messages[index];
        final isUser = message.role == 'user';

        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Align(
            alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.85,
              ),
              child: Column(
                crossAxisAlignment: isUser
                    ? CrossAxisAlignment.end
                    : CrossAxisAlignment.start,
                children: [
                  if (!isUser)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 28,
                            height: 28,
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [Color(0xFF8D6E63), Color(0xFF6D4C41)],
                              ),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(
                              Icons.auto_awesome,
                              size: 16,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(width: 8),
                          const Text(
                            'Assistant',
                            style: TextStyle(
                              fontSize: 12,
                              color: Color(0xFF8D6E63),
                            ),
                          ),
                        ],
                      ),
                    ),
                  _buildMessageBubble(message, isUser),
                  if (message.verse != null) ...[
                    const SizedBox(height: 8),
                    _buildVerseCard(message.verse!),
                  ],
                  if (isUser)
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(
                        '${message.timestamp.hour.toString().padLeft(2, '0')}:${message.timestamp.minute.toString().padLeft(2, '0')}',
                        style: const TextStyle(
                          fontSize: 10,
                          color: Color(0xFFBCAAA4),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildMessageBubble(Message message, bool isUser) {
    return Stack(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            gradient: isUser
                ? const LinearGradient(
                    colors: [Color(0xFF8D6E63), Color(0xFF6D4C41)],
                  )
                : null,
            color: isUser ? null : Colors.white,
            border: isUser
                ? null
                : Border.all(color: const Color(0xFF8D6E63).withOpacity(0.1)),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Text(
            message.content,
            style: TextStyle(
              fontSize: 14,
              height: 1.5,
              color: isUser ? Colors.white : const Color(0xFF5D4037),
            ),
          ),
        ),
        if (!isUser)
          Positioned(
            top: 8,
            right: 8,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildActionButton(
                  icon: _copiedId == message.id
                      ? Icons.favorite
                      : Icons.content_copy,
                  onTap: () => _handleCopy(message.content, message.id),
                ),
                const SizedBox(width: 4),
                _buildActionButton(icon: Icons.bookmark_border, onTap: () {}),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(6),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.9),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFF8D6E63).withOpacity(0.2)),
        ),
        child: Icon(
          icon,
          size: 14,
          color: icon == Icons.favorite
              ? const Color(0xFFD4AF37)
              : const Color(0xFF8D6E63),
        ),
      ),
    );
  }

  Widget _buildVerseCard(Verse verse) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFFFF8E1), Color(0xFFF5F5F0)],
        ),
        border: Border.all(color: const Color(0xFFD4AF37).withOpacity(0.3)),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.menu_book, size: 16, color: Color(0xFFD4AF37)),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '"${verse.text}"',
                  style: const TextStyle(
                    fontSize: 14,
                    fontStyle: FontStyle.italic,
                    color: Color(0xFF5D4037),
                    height: 1.5,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.only(left: 24),
            child: Text(
              '— ${verse.reference}',
              style: const TextStyle(fontSize: 12, color: Color(0xFF8D6E63)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFF8D6E63).withOpacity(0.1)),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildDot(0),
            const SizedBox(width: 4),
            _buildDot(1),
            const SizedBox(width: 4),
            _buildDot(2),
            const SizedBox(width: 8),
            const Text(
              'En train d\'écrire...',
              style: TextStyle(fontSize: 12, color: Color(0xFF8D6E63)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDot(int index) {
    return AnimatedBuilder(
      animation: _typingAnimationController,
      builder: (context, child) {
        final value = (_typingAnimationController.value + index * 0.2) % 1.0;
        final scale = 1.0 + (0.2 * (value < 0.5 ? value * 2 : (1 - value) * 2));
        return Transform.scale(
          scale: scale,
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
    );
  }

  Widget _buildSuggestions() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(bottom: 12),
            child: Text(
              '💡 Questions fréquentes :',
              style: TextStyle(fontSize: 12, color: Color(0xFF8D6E63)),
            ),
          ),
          SizedBox(
            height: 180,
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 3,
                crossAxisSpacing: 8,
                mainAxisSpacing: 8,
              ),
              itemCount: _suggestedPrompts.length,
              itemBuilder: (context, index) {
                return InkWell(
                  onTap: () {
                    _inputController.text = _suggestedPrompts[index];
                  },
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      border: Border.all(
                        color: const Color(0xFF8D6E63).withOpacity(0.2),
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.lightbulb_outline,
                          size: 12,
                          color: Color(0xFFD4AF37),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            _suggestedPrompts[index],
                            style: const TextStyle(
                              fontSize: 11,
                              color: Color(0xFF5D4037),
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInput() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(
          top: BorderSide(color: const Color(0xFF8D6E63).withOpacity(0.1)),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _inputController,
              maxLines: null,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _handleSend(),
              decoration: InputDecoration(
                hintText: 'Posez votre question spirituelle...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: const Color(0xFF8D6E63).withOpacity(0.2),
                  ),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: const Color(0xFF8D6E63).withOpacity(0.2),
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(
                    color: Color(0xFFD4AF37),
                    width: 2,
                  ),
                ),
                filled: true,
                fillColor: Colors.white,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF8D6E63), Color(0xFF6D4C41)],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              onPressed: _inputController.text.trim().isEmpty || _isTyping
                  ? null
                  : _handleSend,
              icon: const Icon(Icons.send, color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }
}
