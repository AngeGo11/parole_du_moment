import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/firebase_auth_service.dart';

class SMSVerificationScreen extends StatefulWidget {
  final String phoneNumber;

  const SMSVerificationScreen({super.key, required this.phoneNumber});

  @override
  State<SMSVerificationScreen> createState() => _SMSVerificationScreenState();
}

class _SMSVerificationScreenState extends State<SMSVerificationScreen> {
  final _codeController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  bool _codeSent = false;
  String? _verificationId;

  final FirebaseAuthService _authService = FirebaseAuthService();

  @override
  void initState() {
    super.initState();
    _sendVerificationCode();
  }

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  void _sendVerificationCode() async {
    print('🚀 Début de l\'envoi du code SMS');
    print('📱 Numéro de téléphone: ${widget.phoneNumber}');

    setState(() {
      _isLoading = true;
      _codeSent = false;
    });

    try {
      print('⏳ Appel au service Firebase Auth...');
      await _authService.signInWithPhoneNumber(
        widget.phoneNumber,
        (String verificationId, int? resendToken) {
          if (mounted) {
            setState(() {
              _verificationId = verificationId;
              _codeSent = true;
              _isLoading = false;
            });
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Code de vérification envoyé !'),
                backgroundColor: Color(0xFF8D6E63),
              ),
            );
          }
        },
        (FirebaseAuthException e) {
          if (mounted) {
            setState(() {
              _isLoading = false;
            });
            print('Erreur Firebase Auth: ${e.code} - ${e.message}');

            // Message d'erreur personnalisé selon le code d'erreur
            String errorMessage;
            switch (e.code) {
              case 'billing-not-enabled':
                errorMessage =
                    'La facturation Firebase doit être activée pour utiliser l\'authentification SMS.\n'
                    'Veuillez activer la facturation dans la console Firebase (https://console.firebase.google.com).\n'
                    'Note: reCAPTCHA v2 sera utilisé en attendant.';
                break;
              case 'invalid-phone-number':
                errorMessage = 'Numéro de téléphone invalide.';
                break;
              case 'quota-exceeded':
                errorMessage =
                    'Quota SMS dépassé. Veuillez réessayer plus tard.';
                break;
              case 'too-many-requests':
                errorMessage =
                    'Trop de tentatives. Veuillez réessayer plus tard.';
                break;
              default:
                errorMessage = e.message ?? 'Erreur: ${e.code}';
            }

            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(errorMessage),
                backgroundColor: Colors.red,
                duration: const Duration(seconds: 8),
                action: e.code == 'billing-not-enabled'
                    ? SnackBarAction(
                        label: 'OK',
                        textColor: Colors.white,
                        onPressed: () {},
                      )
                    : null,
              ),
            );
          }
        },
        (String e) {
          if (mounted) {
            setState(() {
              _isLoading = false;
            });
            print('Timeout: $e');
          }
        },
      );
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        print('Erreur catch: $e');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    }
  }

  void _verifyCode() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      if (_verificationId == null) {
        throw Exception(
          'Code de vérification non disponible. Veuillez renvoyer le code.',
        );
      }

      final userCredential = await _authService.verifySMSCode(
        _verificationId!,
        _codeController.text.trim(),
      );

      if (userCredential != null && mounted) {
        // La redirection se fera automatiquement via AuthWrapper
        Navigator.of(context).popUntil((route) => route.isFirst);
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Code incorrect: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFFFDFCFB), Color(0xFFF5F5F0), Color(0xFFFFF8E1)],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(height: 48),
                  // Icône
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF8D6E63), Color(0xFF6D4C41)],
                      ),
                      borderRadius: BorderRadius.circular(40),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.2),
                          blurRadius: 12,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: const Icon(
                      Icons.sms_outlined,
                      size: 40,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'Vérification du code',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF5D4037),
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Un code de vérification a été envoyé à\n${widget.phoneNumber}',
                    style: const TextStyle(
                      fontSize: 14,
                      color: Color(0xFF8D6E63),
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 48),
                  // Champ de code
                  TextFormField(
                    controller: _codeController,
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(6),
                    ],
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 8,
                    ),
                    decoration: InputDecoration(
                      hintText: '------',
                      hintStyle: TextStyle(
                        fontSize: 32,
                        letterSpacing: 8,
                        color: Colors.grey.withOpacity(0.3),
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide(
                          color: const Color(0xFF8D6E63).withOpacity(0.2),
                          width: 2,
                        ),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide(
                          color: const Color(0xFF8D6E63).withOpacity(0.2),
                          width: 2,
                        ),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: const BorderSide(
                          color: Color(0xFFD4AF37),
                          width: 2,
                        ),
                      ),
                      filled: true,
                      fillColor: Colors.white,
                      contentPadding: const EdgeInsets.symmetric(
                        vertical: 20,
                        horizontal: 16,
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Veuillez entrer le code';
                      }
                      if (value.length != 6) {
                        return 'Le code doit contenir 6 chiffres';
                      }
                      return null;
                    },
                    onChanged: (value) {
                      if (value.length == 6) {
                        _verifyCode();
                      }
                    },
                  ),
                  const SizedBox(height: 24),
                  // Bouton de vérification
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: _isLoading || !_codeSent ? null : _verifyCode,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF8D6E63),
                        disabledBackgroundColor: const Color(
                          0xFF8D6E63,
                        ).withOpacity(0.5),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                        elevation: 8,
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  Colors.white,
                                ),
                              ),
                            )
                          : const Text(
                              'Vérifier le code',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Colors.white,
                              ),
                            ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  // Bouton renvoyer
                  TextButton(
                    onPressed: _isLoading
                        ? null
                        : () {
                            _codeController.clear();
                            _sendVerificationCode();
                          },
                    child: const Text(
                      'Renvoyer le code',
                      style: TextStyle(fontSize: 14, color: Color(0xFF8D6E63)),
                    ),
                  ),
                  const SizedBox(height: 24),
                  // Bouton retour
                  TextButton.icon(
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.arrow_back, size: 18),
                    label: const Text(
                      'Modifier le numéro',
                      style: TextStyle(fontSize: 14),
                    ),
                    style: TextButton.styleFrom(
                      foregroundColor: const Color(0xFF8D6E63),
                    ),
                  ),
                  const Spacer(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
