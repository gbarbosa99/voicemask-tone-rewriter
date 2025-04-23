import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:audioplayers/audioplayers.dart';

void main() => runApp(VoiceMaskApp());

class VoiceMaskApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VoiceMask',
      home: VoiceMaskHomePage(),
    );
  }
}

class VoiceMaskHomePage extends StatefulWidget {
  @override
  _VoiceMaskHomePageState createState() => _VoiceMaskHomePageState();
}

class _VoiceMaskHomePageState extends State<VoiceMaskHomePage> {
  String? selectedTone;
  List<String> tones = [];
  String? originalText;
  String? rewrittenText;
  final player = AudioPlayer();
  PlatformFile? pickedFile;

  final String baseUrl = 'http://127.0.0.1:8000'; // ⚠️ Replace with your backend URL

  @override
  void initState() {
    super.initState();
    fetchTones();
  }

  Future<void> fetchTones() async {
    final response = await http.get(Uri.parse('$baseUrl/tones/'));
    if (response.statusCode == 200) {
      final List<dynamic> toneList = json.decode(response.body);
      setState(() => tones = toneList.cast<String>());
    }
  }

  Future<void> pickFile() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.audio);
    if (result != null && result.files.single.path != null) {
      setState(() => pickedFile = result.files.single);
    }
  }

  Future<void> submit() async {
    if (pickedFile == null || selectedTone == null) return;

    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/process/'),
    );
    request.fields['tone'] = selectedTone!;
    request.files.add(await http.MultipartFile.fromPath('file', pickedFile!.path!));

    final response = await request.send();
    final responseBody = await response.stream.bytesToString();

    if (response.statusCode == 200) {
      final result = json.decode(responseBody);
      setState(() {
        originalText = result['original'];
        rewrittenText = result['rewritten'];
      });

      // Play the audio
      await player.play(UrlSource('$baseUrl${result['tts_audio_url']}'));
    } else {
      print("Error: ${response.statusCode} - $responseBody");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('VoiceMask')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            DropdownButton<String>(
              hint: Text('Select Tone'),
              value: selectedTone,
              items: tones.map((tone) {
                return DropdownMenuItem(value: tone, child: Text(tone));
              }).toList(),
              onChanged: (value) => setState(() => selectedTone = value),
            ),
            ElevatedButton(
              onPressed: pickFile,
              child: Text(pickedFile == null ? 'Choose Audio File' : 'Change File'),
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: submit,
              child: Text('Transform Speech'),
            ),
            SizedBox(height: 24),
            if (originalText != null) Text("Original: $originalText"),
            if (rewrittenText != null) Text("Rewritten: $rewrittenText", style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}
