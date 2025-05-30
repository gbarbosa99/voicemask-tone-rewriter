// voice_setup_page.dart — updated for centered UI, background consistency, and better readability
import 'dart:convert';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';

class VoiceSetupPage extends StatefulWidget {
  const VoiceSetupPage({super.key});

  @override
  State<VoiceSetupPage> createState() => _VoiceSetupPageState();
}

class _VoiceSetupPageState extends State<VoiceSetupPage> {
  final List<String> prompts = [
    "Hello, my name is {name} and this is my voice.",
    "I enjoy learning new things and working on creative projects.",
    "Flutter and FastAPI make building apps fun and efficient."
  ];

  final Record _recorder = Record();
  final AudioPlayer _player = AudioPlayer();

  int _currentPromptIndex = 0;
  bool _isRecording = false;
  bool _isUploading = false;
  bool _hasConsented = false;
  bool _hasRespondedToConsent = false;
  bool _previewReady = false;
  String? _recordedFilePath;
  final String _baseUrl = 'http://127.0.0.1:8000';

  String get currentPrompt {
    final name = FirebaseAuth.instance.currentUser?.displayName ?? "your name";
    return prompts[_currentPromptIndex].replaceAll("{name}", name);
  }

  @override
  void initState() {
    super.initState();
    _checkIfSetupAlreadyDone();
  }

  Future<void> _checkIfSetupAlreadyDone() async {
    final userId = FirebaseAuth.instance.currentUser?.uid;
    if (userId == null) return;

    final response = await http.get(Uri.parse('$_baseUrl/has-setup?user_id=$userId'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['has_voice_setup'] == true) {
        Navigator.pushReplacementNamed(context, '/rewrite');
      }
    }
  }

  Future<void> _submitConsent(bool consented) async {
    setState(() {
      _hasRespondedToConsent = true;
      _hasConsented = consented;
    });

    if (consented) {
      final userId = FirebaseAuth.instance.currentUser?.uid;
      if (userId == null) return;

      final response = await http.post(
        Uri.parse('$_baseUrl/consent'),
        body: {
          'user_id': userId,
          'consent': 'true',
        },
      );

      if (response.statusCode != 200) {
        print("Consent submission failed");
      }
    }
  }

  Future<void> _startRecording() async {
    if (await _recorder.hasPermission()) {
      final directory = await getApplicationDocumentsDirectory();
      final path = '${directory.path}/prompt_${_currentPromptIndex + 1}.wav';
      await _recorder.start(
        encoder: AudioEncoder.wav,
        path: path,
      );
      setState(() {
        _isRecording = true;
        _recordedFilePath = path;
      });
    }
  }

  Future<void> _stopRecording() async {
    final path = await _recorder.stop();
    setState(() {
      _isRecording = false;
      _recordedFilePath = path;
    });
  }

  Future<void> _playRecording() async {
    if (_recordedFilePath != null) {
      await _player.setFilePath(_recordedFilePath!);
      await _player.play();
    }
  }

  Future<void> _uploadRecording() async {
    if (_recordedFilePath == null) return;
    setState(() => _isUploading = true);

    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    final uri = Uri.parse('$_baseUrl/voice');
    final request = http.MultipartRequest('POST', uri);
    request.fields['user_id'] = user.uid;
    request.fields['prompt_id'] = 'prompt${_currentPromptIndex + 1}';
    request.files.add(await http.MultipartFile.fromPath('file', _recordedFilePath!));

    try {
      final response = await request.send();
      if (response.statusCode == 200) {
        setState(() {
          _recordedFilePath = null;
          _currentPromptIndex += 1;
        });
      }
    } catch (e) {
      print("Upload error: $e");
    } finally {
      setState(() => _isUploading = false);
    }
  }

  Future<void> _retryCurrentPrompt() async {
    setState(() {
      _recordedFilePath = null;
    });
  }

  Future<void> _finalizeSetup() async {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    final uri = Uri.parse('$_baseUrl/complete');
    final request = http.MultipartRequest('POST', uri);
    request.fields['user_id'] = user.uid;
    request.fields['consent'] = _hasConsented ? 'true' : 'false';

    try {
      final response = await request.send();
      if (response.statusCode == 200) {
        setState(() => _previewReady = true);
      }
    } catch (e) {
      print("Finalize error: $e");
    }
  }

  Future<void> _playPreview(String userId) async {
    try {
      final url = '$_baseUrl/preview/$userId';
      await _player.setUrl(url);
      await _player.play();
    } catch (e) {
      print("Preview play error: $e");
    }
  }

  @override
  void dispose() {
    _recorder.dispose();
    _player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isLastPrompt = _currentPromptIndex >= prompts.length;
    final userId = FirebaseAuth.instance.currentUser?.uid;

    return Scaffold(
      backgroundColor: const Color(0xFF004d40),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFFa8e6cf),
              Color(0xFF56ab91),
              Color(0xFF004d40),
            ],
          ),
        ),
        padding: const EdgeInsets.all(20),
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                if (!_hasRespondedToConsent) ...[
                  const Text(
                    "We’d love your help in improving our AI voice models. Do you consent to your recordings being saved for future research and training of a personalized speech coach?",
                    style: TextStyle(fontSize: 18, color: Colors.white),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => _submitConsent(true),
                    child: const Text("Yes, I Consent"),
                  ),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () => _submitConsent(false),
                    child: const Text("No, Continue Without Consenting"),
                  ),
                ] else if (isLastPrompt && !_previewReady) ...[
                  const Text(
                    "You're all set! Tap below to complete setup.",
                    style: TextStyle(fontSize: 18, color: Colors.white),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: _finalizeSetup,
                    child: const Text("Complete Setup"),
                  ),
                ] else if (_previewReady) ...[
                  const Text("Here’s a preview of your cloned voice:", style: TextStyle(color: Colors.white)),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: () => _playPreview(userId!),
                    child: const Text("Play Preview"),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: () => Navigator.pushReplacementNamed(context, '/rewrite'),
                    child: const Text("Continue to Rewrite Page"),
                  ),
                ] else ...[
                  Text(
                    "Prompt ${_currentPromptIndex + 1} of ${prompts.length}",
                    style: const TextStyle(color: Colors.white, fontSize: 20),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    currentPrompt,
                    style: const TextStyle(fontSize: 18, color: Colors.white70),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: _isRecording ? _stopRecording : _startRecording,
                    child: Text(_isRecording ? "Stop Recording" : "Start Recording"),
                  ),
                  if (_recordedFilePath != null && !_isRecording) ...[
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: _playRecording,
                      child: const Text("Play Back Recording"),
                    ),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: _isUploading ? null : _uploadRecording,
                      child: _isUploading
                          ? const CircularProgressIndicator()
                          : const Text("Upload Recording"),
                    ),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: _retryCurrentPrompt,
                      child: const Text("Retry This Prompt"),
                    )
                  ]
                ]
              ],
            ),
          ),
        ),
      ),
    );
  }
}
