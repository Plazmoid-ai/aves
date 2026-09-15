import 'package:flutter/foundation.dart';

/// Global state for the one-shot object-note capture mode.
///
/// The viewer UI toggles this notifier. EntryPageView consumes it when a
/// coordinate-aware long press is received.
final objectNoteModeNotifier = ValueNotifier<bool>(false);

void toggleObjectNoteMode() {
  objectNoteModeNotifier.value = !objectNoteModeNotifier.value;
}

void stopObjectNoteMode() {
  if (objectNoteModeNotifier.value) {
    objectNoteModeNotifier.value = false;
  }
}
