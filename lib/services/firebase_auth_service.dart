import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter_facebook_auth/flutter_facebook_auth.dart';

class FirebaseAuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    clientId:
        '942144436665-9koamu0jfrm3mi7lg0ociguglbtq0brp.apps.googleusercontent.com',
    scopes: ['email'],
  );
  final FacebookAuth _facebookAuth = FacebookAuth.instance;

  // Stream pour écouter les changements d'état d'authentification
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  // Getter pour l'utilisateur actuel
  User? get currentUser => _auth.currentUser;

  // Connexion avec Email et Mot de passe
  Future<UserCredential?> signInWithEmailAndPassword(
    String email,
    String password,
  ) async {
    try {
      final userCredential = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      return userCredential;
    } on FirebaseAuthException catch (e) {
      throw _handleAuthException(e);
    }
  }

  // Inscription avec Email et Mot de passe
  Future<UserCredential?> signUpWithEmailAndPassword(
    String email,
    String password,
  ) async {
    try {
      final userCredential = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      return userCredential;
    } on FirebaseAuthException catch (e) {
      throw _handleAuthException(e);
    }
  }

  // Connexion avec Google
  Future<UserCredential?> signInWithGoogle() async {
    try {
      // Déclencher le flux d'authentification Google
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();

      if (googleUser == null) {
        // L'utilisateur a annulé la connexion
        return null;
      }

      // Obtenir les détails d'authentification de la demande
      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;

      // Créer un nouveau credential
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // Une fois connecté, renvoyer l'utilisateur Google connecté avec timeout
      final userCredential = await _auth
          .signInWithCredential(credential)
          .timeout(
            const Duration(seconds: 30),
            onTimeout: () {
              throw Exception('Timeout lors de la connexion Google');
            },
          );
      return userCredential;
    } catch (e) {
      throw Exception('Erreur lors de la connexion Google: $e');
    }
  }

  // Connexion avec Facebook
  Future<UserCredential?> signInWithFacebook() async {
    try {
      // Déclencher le flux d'authentification Facebook
      final LoginResult loginResult = await _facebookAuth.login();

      if (loginResult.status == LoginStatus.success) {
        // Créer un nouveau credential
        final OAuthCredential facebookAuthCredential =
            FacebookAuthProvider.credential(
              loginResult.accessToken!.tokenString,
            );

        // Une fois connecté, renvoyer l'utilisateur Facebook connecté
        final userCredential = await _auth.signInWithCredential(
          facebookAuthCredential,
        );
        return userCredential;
      } else if (loginResult.status == LoginStatus.cancelled) {
        throw Exception('Connexion Facebook annulée');
      } else {
        throw Exception('Erreur lors de la connexion Facebook');
      }
    } catch (e) {
      throw Exception('Erreur lors de la connexion Facebook: $e');
    }
  }

  // Connexion avec numéro de téléphone (SMS)
  Future<void> signInWithPhoneNumber(
    String phoneNumber,
    Function(String verificationId, int? resendToken) codeSent,
    Function(FirebaseAuthException e) verificationFailed,
    Function(String e) codeAutoRetrievalTimeout,
  ) async {
    try {
      await _auth.verifyPhoneNumber(
        phoneNumber: phoneNumber,
        timeout: const Duration(seconds: 60),
        verificationCompleted: (PhoneAuthCredential credential) async {
          await _auth.signInWithCredential(credential);
        },
        verificationFailed: (FirebaseAuthException e) {
          // Gérer spécifiquement l'erreur billing-not-enabled
          if (e.code == 'billing-not-enabled') {
            verificationFailed(
              FirebaseAuthException(
                code: e.code,
                message: 'La facturation Firebase doit être activée pour utiliser l\'authentification SMS. '
                    'Veuillez activer la facturation dans la console Firebase ou utiliser reCAPTCHA v2.',
              ),
            );
          } else {
            verificationFailed(e);
          }
        },
        codeSent: (String verificationId, int? resendToken) {
          codeSent(verificationId, resendToken);
        },
        codeAutoRetrievalTimeout: (String verificationId) {
          codeAutoRetrievalTimeout(verificationId);
        },
      );
    } catch (e) {
      if (e is FirebaseAuthException) {
        if (e.code == 'billing-not-enabled') {
          throw FirebaseAuthException(
            code: e.code,
            message: 'La facturation Firebase doit être activée pour utiliser l\'authentification SMS. '
                'Veuillez activer la facturation dans la console Firebase ou utiliser reCAPTCHA v2.',
          );
        }
        throw e;
      }
      throw Exception('Erreur lors de la vérification du numéro: $e');
    }
  }

  // Vérifier le code SMS
  Future<UserCredential?> verifySMSCode(
    String verificationId,
    String smsCode,
  ) async {
    try {
      final PhoneAuthCredential credential = PhoneAuthProvider.credential(
        verificationId: verificationId,
        smsCode: smsCode,
      );
      final userCredential = await _auth.signInWithCredential(credential);
      return userCredential;
    } catch (e) {
      throw Exception('Erreur lors de la vérification du code SMS: $e');
    }
  }

  // Déconnexion
  Future<void> signOut() async {
    try {
      await _googleSignIn.signOut();
      await _facebookAuth.logOut();
      await _auth.signOut();
    } catch (e) {
      throw Exception('Erreur lors de la déconnexion: $e');
    }
  }

  // Réinitialisation du mot de passe
  Future<void> sendPasswordResetEmail(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email);
    } on FirebaseAuthException catch (e) {
      throw _handleAuthException(e);
    }
  }

  // Envoyer un email de vérification
  Future<void> sendEmailVerification() async {
    try {
      await currentUser?.sendEmailVerification();
    } catch (e) {
      throw Exception(
        'Erreur lors de l\'envoi de l\'email de vérification: $e',
      );
    }
  }

  // Mettre à jour le profil utilisateur
  Future<void> updateUserProfile({
    String? displayName,
    String? photoURL,
  }) async {
    try {
      await currentUser?.updateDisplayName(displayName);
      await currentUser?.updatePhotoURL(photoURL);
      await currentUser?.reload();
    } catch (e) {
      throw Exception('Erreur lors de la mise à jour du profil: $e');
    }
  }

  // Supprimer le compte
  Future<void> deleteAccount() async {
    try {
      await currentUser?.delete();
    } on FirebaseAuthException catch (e) {
      throw _handleAuthException(e);
    }
  }

  // Gérer les exceptions Firebase Auth
  String _handleAuthException(FirebaseAuthException e) {
    switch (e.code) {
      case 'weak-password':
        return 'Le mot de passe est trop faible.';
      case 'email-already-in-use':
        return 'Un compte existe déjà pour cet email.';
      case 'user-not-found':
        return 'Aucun utilisateur trouvé pour cet email.';
      case 'wrong-password':
        return 'Mot de passe incorrect.';
      case 'invalid-email':
        return 'Adresse email invalide.';
      case 'user-disabled':
        return 'Ce compte utilisateur a été désactivé.';
      case 'too-many-requests':
        return 'Trop de tentatives. Veuillez réessayer plus tard.';
      case 'operation-not-allowed':
        return 'Cette opération n\'est pas autorisée.';
      case 'network-request-failed':
        return 'Erreur de connexion réseau. Vérifiez votre connexion internet.';
      case 'billing-not-enabled':
        return 'La facturation Firebase doit être activée pour utiliser l\'authentification SMS. '
            'Veuillez activer la facturation dans la console Firebase.';
      case 'invalid-phone-number':
        return 'Numéro de téléphone invalide.';
      case 'missing-phone-number':
        return 'Le numéro de téléphone est requis.';
      case 'quota-exceeded':
        return 'Quota SMS dépassé. Veuillez réessayer plus tard.';
      case 'invalid-verification-code':
        return 'Code de vérification invalide.';
      case 'invalid-verification-id':
        return 'ID de vérification invalide. Veuillez renvoyer le code.';
      case 'session-expired':
        return 'La session a expiré. Veuillez renvoyer le code.';
      default:
        return e.message ?? 'Une erreur est survenue.';
    }
  }
}
