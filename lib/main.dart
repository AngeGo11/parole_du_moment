import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:provider/provider.dart';
import 'firebase_options.dart';
import 'services/firebase_auth_service.dart';
import 'providers/theme_provider.dart';
import 'screens/Welcome.dart';
import 'screens/SignIn.dart';
import 'screens/SignUp.dart';
import 'screens/Home.dart';
import 'screens/DailyVerse.dart';
import 'screens/Assistant.dart';
import 'screens/Community.dart';
import 'screens/Profile.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
    print('✅ Firebase initialisé avec succès');
  } catch (e) {
    print('❌ Erreur lors de l\'initialisation de Firebase: $e');
  }

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => ThemeProvider(),
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, _) {
          return MaterialApp(
            title: 'Parole du moment',
            debugShowCheckedModeBanner: false,
            theme: ThemeData(
              colorScheme: ColorScheme.fromSeed(
                seedColor: const Color(0xFF8D6E63),
                brightness: Brightness.light,
              ),
              useMaterial3: true,
            ),
            darkTheme: ThemeData(
              colorScheme: ColorScheme.dark(
                primary: const Color(0xFF8D6E63),
                secondary: const Color(0xFF6D4C41),
                surface: const Color(0xFF2D2D2D),
                background: const Color(0xFF1E1E1E),
                onPrimary: Colors.white,
                onSecondary: Colors.white,
                onSurface: const Color(0xFFEFEFEF),
                onBackground: const Color(0xFFEFEFEF),
                error: Colors.red,
                onError: Colors.white,
                brightness: Brightness.dark,
              ),
              scaffoldBackgroundColor: const Color(0xFF1E1E1E),
              cardColor: const Color(0xFF2D2D2D),
              dividerColor: const Color(0xFF3C2F2F),
              textTheme: const TextTheme(
                displayLarge: TextStyle(color: Color(0xFFEFEFEF)),
                displayMedium: TextStyle(color: Color(0xFFEFEFEF)),
                displaySmall: TextStyle(color: Color(0xFFEFEFEF)),
                headlineLarge: TextStyle(color: Color(0xFFD4AF37)),
                headlineMedium: TextStyle(color: Color(0xFFD4AF37)),
                headlineSmall: TextStyle(color: Color(0xFFD4AF37)),
                titleLarge: TextStyle(color: Color(0xFFEFEFEF)),
                titleMedium: TextStyle(color: Color(0xFFEFEFEF)),
                titleSmall: TextStyle(color: Color(0xFFEFEFEF)),
                bodyLarge: TextStyle(color: Color(0xFFEFEFEF)),
                bodyMedium: TextStyle(color: Color(0xFFEFEFEF)),
                bodySmall: TextStyle(color: Color(0xFFBCAAA4)),
                labelLarge: TextStyle(color: Color(0xFFEFEFEF)),
                labelMedium: TextStyle(color: Color(0xFFBCAAA4)),
                labelSmall: TextStyle(color: Color(0xFFBCAAA4)),
              ),
              useMaterial3: true,
            ),
            themeMode: themeProvider.isDarkMode 
                ? ThemeMode.dark 
                : ThemeMode.light,
            // Point d'entrée avec contrôle d'authentification
            home: const AuthWrapper(),
            routes: {
              '/welcome': (context) => const WelcomePage(),
              '/signin': (context) => const SigninPage(),
              '/signup': (context) => const SignupPage(),
              '/home': (context) => const Scaffold(
                body: HomePage(onAddToHistory: _dummyHistoryCallback),
              ),
            },
          );
        },
      ),
    );
  }

  // Callback temporaire pour HomePage
  static void _dummyHistoryCallback(verse, isFavorite) {}
}

// Widget qui vérifie l'état d'authentification
class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    final authService = FirebaseAuthService();

    return StreamBuilder<User?>(
      stream: authService.authStateChanges,
      builder: (context, snapshot) {
        print('🔍 AuthWrapper - ConnectionState: ${snapshot.connectionState}');
        print('🔍 AuthWrapper - hasData: ${snapshot.hasData}');
        print('🔍 AuthWrapper - User: ${snapshot.data?.email}');

        // Attendre que la connexion soit établie
        if (snapshot.connectionState == ConnectionState.waiting) {
          print('⏳ En attente de la connexion...');
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        // Si l'utilisateur est connecté, rediriger vers MainNavigation
        if (snapshot.hasData && snapshot.data != null) {
          print('✅ Utilisateur connecté, redirection vers Home');
          return const MainNavigation();
        }

        // Sinon, afficher la page d'accueil (Welcome)
        print('❌ Utilisateur non connecté, affichage de Welcome');
        return const WelcomePage();
      },
    );
  }
}

// Callback temporaire pour HomePage
void _dummyHomeHistoryCallback(verse, isFavorite) {}

// Navigation principale avec bottom navigation bar
class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _selectedIndex = 0;
  String? _assistantInitialMessage; // Message initial pour l'assistant
  int _assistantKeyCounter = 0; // Compteur pour forcer la recréation de AssistantPage

  List<Widget> get _pages => [
        HomePage(
          onAddToHistory: _dummyHomeHistoryCallback,
          onNavigateToAssistant: _navigateToAssistantWithMessage,
        ),
        const DailyVersePage(),
        AssistantPage(
          key: ValueKey('assistant_$_assistantKeyCounter'),
          initialUserMessage: _assistantInitialMessage,
        ),
        const CommunityPage(),
        const ProfilePage(),
      ];

  void _navigateToAssistantWithMessage(String message) {
    setState(() {
      _assistantInitialMessage = message;
      _assistantKeyCounter++; // Incrémenter pour forcer la recréation
      _selectedIndex = 2; // Index de l'Assistant
    });
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
      // Réinitialiser le message initial si on quitte la page Assistant
      // pour permettre d'envoyer un nouveau message lors de la prochaine navigation
      if (index != 2) {
        _assistantInitialMessage = null;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: _pages,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(24),
            topRight: Radius.circular(24),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(24),
            topRight: Radius.circular(24),
          ),
          child: BottomNavigationBar(
            currentIndex: _selectedIndex,
            onTap: _onItemTapped,
            backgroundColor: Colors.white,
            selectedItemColor: const Color(0xFF8D6E63),
            unselectedItemColor: const Color(0xFFBCAAA4),
            type: BottomNavigationBarType.fixed,
            elevation: 0,
            selectedLabelStyle: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
            unselectedLabelStyle: const TextStyle(fontSize: 12),
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.mood),
                label: 'État émotionnel',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.wb_sunny),
                label: 'Verset du jour',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.auto_awesome),
                label: 'Assistant Spirituel',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.people),
                label: 'Communauté',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.person),
                label: 'Profil',
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      // This call to setState tells the Flutter framework that something has
      // changed in this State, which causes it to rerun the build method below
      // so that the display can reflect the updated values. If we changed
      // _counter without calling setState(), then the build method would not be
      // called again, and so nothing would appear to happen.
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.

    //Initialisation de la base de données
    // final FirebaseFirestore db = FirebaseFirestore.instance;

    return Scaffold(
      appBar: AppBar(
        // TRY THIS: Try changing the color here to a specific color (to
        // Colors.amber, perhaps?) and trigger a hot reload to see the AppBar
        // change color while the other colors stay the same.
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: Text(widget.title),
      ),
      body: Center(
        // Center is a layout widget. It takes a single child and positions it
        // in the middle of the parent.
        child: Column(
          // Column is also a layout widget. It takes a list of children and
          // arranges them vertically. By default, it sizes itself to fit its
          // children horizontally, and tries to be as tall as its parent.
          //
          // Column has various properties to control how it sizes itself and
          // how it positions its children. Here we use mainAxisAlignment to
          // center the children vertically; the main axis here is the vertical
          // axis because Columns are vertical (the cross axis would be
          // horizontal).
          //
          // TRY THIS: Invoke "debug painting" (choose the "Toggle Debug Paint"
          // action in the IDE, or press "p" in the console), to see the
          // wireframe for each widget.
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text('You have pushed the button this many times:'),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
