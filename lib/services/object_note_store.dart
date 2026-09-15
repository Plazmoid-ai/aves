// ignore_for_file: unnecessary_type_name_in_constructor

import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ObjectNote {
  final String entryKey;
  final double x;
  final double y;
  final String text;
  final int created;

  const ObjectNote({
    required this.entryKey,
    required this.x,
    required this.y,
    required this.text,
    required this.created,
  });

  Map<String, dynamic> toJson() => {
        'entryKey': entryKey,
        'x': x,
        'y': y,
        'text': text,
        'created': created,
      };

  factory ObjectNote.fromJson(Map<String, dynamic> json) => ObjectNote(
        entryKey: json['entryKey'] as String,
        x: (json['x'] as num).toDouble(),
        y: (json['y'] as num).toDouble(),
        text: json['text'] as String,
        created: json['created'] as int,
      );
}

class ObjectNoteStore {
  static const _key = 'object_notes_mvp_v1';

  Future<List<ObjectNote>> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null || raw.isEmpty) return [];

    final decoded = jsonDecode(raw);
    if (decoded is! List) return [];

    return decoded
        .whereType<Map>()
        .map((item) => ObjectNote.fromJson(Map<String, dynamic>.from(item)))
        .toList();
  }

  Future<List<ObjectNote>> getForEntry(String entryKey) async {
    final notes = await load();
    return notes.where((note) => note.entryKey == entryKey).toList();
  }

  Future<void> add(ObjectNote note) async {
    final notes = await load();
    notes.add(note);
    await _save(notes);
  }

  Future<void> _save(List<ObjectNote> notes) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _key,
      jsonEncode(notes.map((note) => note.toJson()).toList()),
    );
  }
}

final objectNoteStore = ObjectNoteStore();

/// When true, a long-press in the viewer is interpreted as adding an object note.
/// The mode is intentionally one-shot and is not persisted.
final objectNoteModeNotifier = ValueNotifier<bool>(false);

// MVP build trigger: release arm64 verification.
