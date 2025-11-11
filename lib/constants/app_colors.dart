import 'package:flutter/material.dart';

/// Couleurs globales de l'application
class AppColors {
  AppColors._();

  // === THÈME CLAIR ===
  
  // Couleurs principales
  static const Color primary = Color(0xFF8D6E63);
  static const Color primaryDark = Color(0xFF6D4C41);
  static const Color primaryLight = Color(0xFFBCAAA4);
  static const Color textDark = Color(0xFF5D4037);
  static const Color accentGold = Color(0xFFD4AF37);

  // Fond clair
  static const Color backgroundLight1 = Color(0xFFFDFCFB);
  static const Color backgroundLight2 = Color(0xFFF5F5F0);
  static const Color backgroundLight3 = Color(0xFFFFF8E1);
  static const Color backgroundLight4 = Color(0xFFEFEBE9);

  // === THÈME SOMBRE ===
  
  // Fond sombre
  static const Color darkBackground = Color(0xFF1E1E1E); // Fond principal
  static const Color darkCard = Color(0xFF2D2D2D); // Fond secondaire / cartes
  static const Color darkCardElevated = Color(0xFF252525); // Fond de carte / bloc
  
  // Texte sombre
  static const Color darkTextPrimary = Color(0xFFEFEFEF); // Texte principal
  static const Color darkTextSecondary = Color(0xFFBCAAA4); // Texte secondaire
  static const Color darkTextAccent = Color(0xFFD4AF37); // Texte accentué / titre
  
  // Bordures et séparateurs sombres
  static const Color darkBorder = Color(0xFF3C2F2F); // Bordures / séparateurs
  
  // Éléments désactivés sombres
  static Color darkDisabled = const Color(0xFF5D4037).withOpacity(0.4);
  
  // Survol (hover) sombre
  static Color darkHover = const Color(0xFFD4AF37).withOpacity(0.2);
  
  // Gradients sombres
  static List<Color> get darkGradient => [
    darkBackground,
    darkCard,
    darkCardElevated,
  ];
  
  // Gradients clairs
  static List<Color> get lightGradient => [
    backgroundLight1,
    backgroundLight2,
    backgroundLight3,
  ];
}

