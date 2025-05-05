import 'dart:convert';
import 'dart:typed_data';
import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:just_audio/just_audio.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';

void main() {
  runApp(const VoiceMaskApp());
}

class VoiceMaskApp extends StatelessWidget {
  const VoiceMaskApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VoiceMask',
      home: const VoiceMaskHomePage(),
    );
  }
}

class VoiceMaskHomePage extends StatefulWidget {
  const VoiceMaskHomePage({super.key});

  @override
  State<VoiceMaskHomePage> createState() => _VoiceMaskHomePageState();
}

class _VoiceMaskHomePageState extends State<VoiceMaskHomePage> {
  Uint8List? selectedFileBytes;
  String? selectedFileName;
  List<String> tones = [];
  String? selectedTone;
  String? originalText;
  String? rewrittenText;
  String? audioUrl;
  bool isLoading = false;
  bool isRecording = false;
  String? recordedFilePath;

  final String baseUrl = 'http://127.0.0.1:8000';
  final player = AudioPlayer();
  final _recorder = AudioRecorder();

  @override
  void initState() {
    super.initState();
    fetchTones();
  }

  Future<void> fetchTones() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/tones'));
      if (response.statusCode == 200) {
        final List<dynamic> toneList = json.decode(response.body);
        setState(() {
          tones = toneList.cast<String>();
        });
      }
    } catch (e) {
      print('Error fetching tones: $e');
    }
  }

  Future<void> pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['m4a', 'wav', 'mp3'],
    );
    if (result != null && result.files.isNotEmpty) {
      setState(() {
        selectedFileBytes = result.files.first.bytes;
        selectedFileName = result.files.first.name;
        recordedFilePath = null;
      });
    }
  }

  Future<void> toggleRecording() async {
    if (!isRecording) {
      final hasPermission = await _recorder.hasPermission();
      if (!hasPermission) {
        print("Microphone permission denied");
        return;
      }

      final dir = await getApplicationDocumentsDirectory();
      final filePath = '${dir.path}/recorded.m4a';

      await _recorder.start(
        const RecordConfig(encoder: AudioEncoder.aacHe),
        path: filePath,
      );

      setState(() {
        isRecording = true;
        recordedFilePath = filePath;
        selectedFileBytes = null;
      });
    } else {
      final path = await _recorder.stop();
      final fileBytes = await File(path!).readAsBytes();

      setState(() {
        isRecording = false;
        selectedFileBytes = fileBytes;
        selectedFileName = path.split('/').last;
        recordedFilePath = path;
      });
    }
  }

  Future<void> playRecordedAudio() async {
    if (recordedFilePath != null) {
      try {
        await player.setFilePath(recordedFilePath!);
        await player.play();
      } catch (e) {
        print("Playback error: $e");
      }
    }
  }

  Future<void> processAudio() async {
    if (selectedFileBytes == null || selectedTone == null) return;

    setState(() {
      isLoading = true;
      originalText = null;
      rewrittenText = null;
      audioUrl = null;
    });

    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/process/'));
    request.fields['tone'] = selectedTone!;
    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        selectedFileBytes!,
        filename: selectedFileName ?? 'audio.m4a',
      ),
    );

    try {
      final response = await request.send();
      if (response.statusCode == 200) {
        final respStr = await response.stream.bytesToString();
        final respJson = json.decode(respStr);
        setState(() {
          originalText = respJson['original'];
          rewrittenText = respJson['rewritten'];
          audioUrl = baseUrl + respJson['audio_url'];
        });
      } else {
        print('Failed to process audio. Status: ${response.statusCode}');
      }
    } catch (e) {
      print('Error sending audio: $e');
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  Future<void> playAudio() async {
    if (audioUrl != null) {
      try {
        await player.setUrl(audioUrl!);
        await player.play();
      } catch (e) {
        print("Audio playback error: $e");
      }
    }
  }

  @override
  void dispose() {
    player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('VoiceMask')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            ElevatedButton(
              onPressed: pickFile,
              child: const Text('Select Audio File'),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: toggleRecording,
              child: Text(isRecording ? 'Stop Recording' : 'Start Recording'),
            ),
            const SizedBox(height: 16),
            if (selectedFileName != null)
              Text('Selected File: $selectedFileName'),
            if (recordedFilePath != null && !isRecording)
              ElevatedButton(
                onPressed: playRecordedAudio,
                child: const Text("Play Your Recording"),
              ),
            const SizedBox(height: 16),
            if (tones.isNotEmpty)
              DropdownButton<String>(
                value: selectedTone,
                hint: const Text('Select a Tone'),
                items: tones.map((tone) {
                  return DropdownMenuItem<String>(
                    value: tone,
                    child: Text(tone),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    selectedTone = value;
                  });
                },
              )
            else
              const Text('Loading tone options...'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: isLoading ? null : processAudio,
              child: isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text('Transform Speech'),
            ),
            const SizedBox(height: 32),
            if (originalText != null) ...[
              const Text('Original Text:', style: TextStyle(fontWeight: FontWeight.bold)),
              Text(originalText!),
              const SizedBox(height: 16),
            ],
            if (rewrittenText != null) ...[
              const Text('Rewritten Text:', style: TextStyle(fontWeight: FontWeight.bold)),
              Text(rewrittenText!),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: playAudio,
                child: const Text('Play Rewritten Voice'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
qq