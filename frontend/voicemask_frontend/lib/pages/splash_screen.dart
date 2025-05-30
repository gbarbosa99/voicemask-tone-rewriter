// splash_screen.dart (final version: randomized oscillations, double size, larger title)
import 'dart:async';
import 'dart:math';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late Timer _waveformTimer;
  final Random _random = Random();
  List<double> _waveHeights = List.generate(60, (_) => 0);

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(vsync: this, duration: const Duration(seconds: 2));
    _fadeController.forward();
    _startWaveformAnimation();
  }

  void _startWaveformAnimation() {
    _waveformTimer = Timer.periodic(const Duration(milliseconds: 100), (_) {
      setState(() {
        _waveHeights = List.generate(60, (_) => 20 + _random.nextDouble() * 80); // double max height
      });
    });
  }

  Future<void> _signInWithGoogle() async {
    setState(() {});
    try {
      User? user;
      if (kIsWeb) {
        final googleProvider = GoogleAuthProvider();
        final userCredential = await FirebaseAuth.instance.signInWithPopup(googleProvider);
        user = userCredential.user;
      } else {
        final googleUser = await GoogleSignIn().signIn();
        if (googleUser == null) return;
        final googleAuth = await googleUser.authentication;
        final credential = GoogleAuthProvider.credential(
          accessToken: googleAuth.accessToken,
          idToken: googleAuth.idToken,
        );
        final userCredential = await FirebaseAuth.instance.signInWithCredential(credential);
        user = userCredential.user;
      }

      if (user != null) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('user_id', user.uid);
        await _fadeController.reverse();
        await Future.delayed(const Duration(milliseconds: 500));
        Navigator.pushReplacementNamed(context, '/voice-setup');
      }
    } catch (e) {
      print('Google sign-in error: $e');
    } finally {
      setState(() {});
    }
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _waveformTimer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFFa8e6cf), // light mint green
              Color(0xFF56ab91), // medium
              Color(0xFF004d40), // forest green
            ],
          ),
        ),
        child: Stack(
          children: [
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  FadeTransition(
                    opacity: _fadeController,
                    child: const Column(
                      children: [
                        Text(
                          'VoiceMask',
                          style: TextStyle(fontSize: 72, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                        SizedBox(height: 10),
                        Text(
                          'Rewrite how you sound — in your own voice.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 16, color: Colors.white70),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 50),
                  SizedBox(
                    height: 200,
                    child: CustomPaint(
                      size: const Size(double.infinity, 200),
                      painter: WaveformPainter(_waveHeights),
                    ),
                  ),
                ],
              ),
            ),
            Positioned(
              top: 40,
              right: 20,
              child: ElevatedButton(
                onPressed: _signInWithGoogle,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.green.shade900,
                ),
                child: const Text('Sign in with Google'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class WaveformPainter extends CustomPainter {
  final List<double> waveHeights;
  WaveformPainter(this.waveHeights);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.8)
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 2;

    final midY = size.height / 2;
    final spacing = size.width / waveHeights.length;

    for (int i = 0; i < waveHeights.length; i++) {
      final x = spacing * i;
      final height = waveHeights[i];
      canvas.drawLine(
        Offset(x, midY - height / 2),
        Offset(x, midY + height / 2),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
