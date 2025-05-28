// main.dart
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:voicemask_frontend/pages/rewrite_page.dart';
import 'package:voicemask_frontend/pages/splash_screen.dart';
import 'package:voicemask_frontend/pages/voice_setup_page.dart';

import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  runApp(const VoiceMaskApp());
}

class VoiceMaskApp extends StatelessWidget {
  const VoiceMaskApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VoiceMask',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
      ),
      home: const SplashScreen(),
      routes: {
        '/splash': (context) => const SplashScreen(),
        '/voice-setup': (context) => const VoiceSetupPage(),
        '/rewrite': (context) => const RewritePage(),
      },
    );
  }
}
