// rewrite_page.dart — updated with gradient background and centered layout
import 'dart:convert';
import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:just_audio/just_audio.dart';

class RewritePage extends StatefulWidget {
  const RewritePage({super.key});

  @override
  State<RewritePage> createState() => _RewritePageState();
}

class _RewritePageState extends State<RewritePage> {
  final AudioPlayer _player = AudioPlayer();
  String? _selectedTone;
  String? _originalText;
  String? _rewrittenText;
  String? _audioUrl;
  File? _selectedFile;
  bool _isLoading = false;

  final List<String> _tones = ['confident', 'polite', 'concise'];

  Future<void> _pickAudioFile() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.audio);
    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedFile = File(result.files.single.path!);
      });
    }
  }

  Future<void> _submitRewriteRequest() async {
    if (_selectedFile == null || _selectedTone == null) return;

    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    setState(() => _isLoading = true);

    final uri = Uri.parse('http://127.0.0.1:8000/process/');
    final request = http.MultipartRequest('POST', uri);
    request.fields['tone'] = _selectedTone!;
    request.fields['user_id'] = user.uid;
    request.files.add(await http.MultipartFile.fromPath('file', _selectedFile!.path));

    try {
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _originalText = data['original'];
          _rewrittenText = data['rewritten'];
          _audioUrl = 'http://127.0.0.1:8000${data['audio_url']}';
        });
      } else {
        print('Rewrite request failed: ${response.body}');
      }
    } catch (e) {
      print('Error: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _playAudio() async {
    if (_audioUrl != null) {
      await _player.setUrl(_audioUrl!);
      await _player.play();
    }
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Rewrite My Voice')),
      backgroundColor: const Color(0xFF004d40),
      body: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
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
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: _pickAudioFile,
                  child: Text(_selectedFile == null ? 'Select Audio File' : 'Audio Selected'),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _selectedTone,
                  dropdownColor: Colors.white,
                  decoration: const InputDecoration(
                    labelText: 'Select Tone',
                    fillColor: Colors.white,
                    filled: true,
                  ),
                  items: _tones
                      .map((tone) => DropdownMenuItem(value: tone, child: Text(tone)))
                      .toList(),
                  onChanged: (val) => setState(() => _selectedTone = val),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: _isLoading ? null : _submitRewriteRequest,
                  child: _isLoading ? const CircularProgressIndicator() : const Text('Rewrite Speech'),
                ),
                const SizedBox(height: 20),
                if (_originalText != null && _rewrittenText != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.9),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Original:', style: TextStyle(fontWeight: FontWeight.bold)),
                        Text(_originalText!),
                        const SizedBox(height: 10),
                        const Text('Rewritten:', style: TextStyle(fontWeight: FontWeight.bold)),
                        Text(_rewrittenText!),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: _playAudio,
                    child: const Text('Play Rewritten Audio'),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
