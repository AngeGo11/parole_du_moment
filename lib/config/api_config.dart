class ApiConfig {
  ApiConfig._();

  /// Base URL du backend. Peut être surchargé via les variables de compilation.
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static const Duration requestTimeout = Duration(seconds: 20);

  static Uri homeSearchUri() => Uri.parse('$baseUrl/api/home/search');
}

