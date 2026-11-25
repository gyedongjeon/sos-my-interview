import type en from './en'

// The texts of the pages in German; the keys are those of `en.ts`. The user is addressed
// as "du". A follow-up question is a "Nachfrage".
const de: Record<keyof typeof en, string> = {
  'models.speech-to-text': 'Spracherkennung',
  'models.voice': 'Stimme des Interviewers',
  'voice.American': 'amerikanisch',
  'voice.British': 'britisch',
  'voice.female': 'weiblich',
  'voice.male': 'männlich',
  'voice.soft': 'sanft',

  'common.delete': 'Löschen',
  'common.cancel': 'Abbrechen',
  'common.save': 'Speichern',
  'common.edit': 'Bearbeiten',
  'common.remove': 'Entfernen',
  'common.stop': 'Stopp',
  'common.hearIt': 'Anhören',
  'common.tryAgain': 'Noch einmal versuchen',
  'common.language': 'Sprache',
  'common.loading': 'Wird geladen',
  'common.backToInterviews': '← Interviews',
  'common.commonQuestions': 'Häufige Fragen',
  'common.pastedText': 'Eingefügter Text',
  'common.title': 'Titel',
  'common.postingText': 'Text der Anzeige',
  'common.optional': '(optional)',
  'common.added': 'Hinzugefügt am {date}',

  'nav.interviews': 'Interviews',
  'nav.history': 'Verlauf',
  'nav.resume': 'Lebenslauf',
  'nav.settings': 'Einstellungen',
  'app.needModel':
    'Füge ein KI-Modell und einen API-Schlüssel hinzu, um passende Fragen, Nachfragen und Feedback zu bekommen.',
  'app.openSettings': 'Einstellungen öffnen',

  'downloads.title': 'Spracherkennung und Stimme werden heruntergeladen',
  'downloads.body':
    'Das passiert nur einmal. Du kannst die App weiter nutzen: Bis der Download fertig ist, werden die Fragen mit der Systemstimme vorgelesen, und deine erste Antwort wartet auf die Spracherkennung.',
  'downloads.of': 'Download: {name}',
  'downloads.failed': 'Ein Modell konnte nicht heruntergeladen werden',

  'device.microphone.notFound': 'Es wurde kein Mikrofon gefunden.',
  'device.microphone.notAllowed':
    'Der Zugriff auf das Mikrofon ist ausgeschaltet. Erlaube ihn für diese App in den Datenschutzeinstellungen deines Systems.',
  'device.microphone.notReadable':
    'Das Mikrofon konnte nicht gestartet werden. Schließ andere Apps, die es verwenden.',
  'device.microphone.unavailableNamed': 'Das Mikrofon ist nicht verfügbar ({name}).',
  'device.microphone.unavailable': 'Das Mikrofon ist nicht verfügbar.',
  'device.camera.notFound': 'Es wurde keine Kamera gefunden.',
  'device.camera.notAllowed':
    'Der Zugriff auf die Kamera ist ausgeschaltet. Erlaube ihn für diese App in den Datenschutzeinstellungen deines Systems.',
  'device.camera.notReadable': 'Die Kamera konnte nicht gestartet werden. Schließ andere Apps, die sie verwenden.',
  'device.camera.unavailableNamed': 'Die Kamera ist nicht verfügbar ({name}).',
  'device.camera.unavailable': 'Die Kamera ist nicht verfügbar.',
  'device.voiceOnly': 'Es wird nur deine Stimme aufgenommen.',
  'device.cannotRecord':
    'Antworten können erst aufgenommen werden, wenn das behoben ist; öffne diese Seite danach noch einmal.',

  'home.headline1': 'Vorstellungsgespräch in Sicht?',
  'home.headline2': 'Hilfe ist unterwegs.',
  'home.intro': 'Wähle das Unternehmen, auf das du dich vorbereitest, oder wärm dich mit häufigen Fragen auf.',
  'home.addPosting': 'Stellenanzeige hinzufügen',
  'home.commonNote': 'Fragen, die in jedem Vorstellungsgespräch kommen',
  'home.answered': '{answered} / {total} Fragen beantwortet',

  'commonView.intro': 'Fragen, die in fast jedem Vorstellungsgespräch vorkommen.',

  'questions.title': 'Fragen',
  'questions.forPosting': 'Fragen zu dieser Anzeige',
  'questions.none': 'Noch keine Fragen.',
  'questions.attempts': '{n} Versuch | {n} Versuche',
  'questions.retry': 'Noch einmal',
  'questions.answer': 'Antworten',

  'postingNew.intro':
    'Die Interviewfragen werden für diese Anzeige geschrieben, und auch Nachfragen und Feedback berücksichtigen sie.',
  'postingNew.link': 'Link',
  'postingNew.linkHelp':
    'Der Text der Anzeige wird aus der Seite ausgelesen. Lässt sich eine Seite nicht lesen (zum Beispiel, weil sie eine Anmeldung verlangt), füge den Text stattdessen unten ein.',
  'postingNew.orPaste': 'oder Text einfügen',
  'postingNew.titlePlaceholder': 'Senior-Backend-Entwickler bei Acme',
  'postingNew.adding': 'Wird hinzugefügt, Fragen werden geschrieben…',
  'postingNew.add': 'Anzeige hinzufügen',

  'difficulty.label': 'Schwierigkeit der Fragen',
  'difficulty.easy': 'Leicht: kurze Fragen zum Aufwärmen',
  'difficulty.standard': 'Standard: ein Erstgespräch',
  'difficulty.hard': 'Schwer: eine anspruchsvolle Endrunde',

  'posting.documentSaved': 'Gespeichert. Lass die Fragen neu schreiben, damit sie es berücksichtigen.',
  'posting.confirmCommonResume':
    'Den für diese Anzeige geschriebenen Lebenslauf entfernen und deinen allgemeinen Lebenslauf verwenden?',
  'posting.confirmRewriteAnswered':
    'Diese Fragen durch neue ersetzen? Bereits aufgenommene Antworten bleiben im Verlauf.',
  'posting.confirmRewrite': 'Diese Fragen durch neue ersetzen?',
  'posting.confirmDelete':
    'Diese Anzeige und ihre Fragen löschen? Bereits aufgenommene Antworten bleiben im Verlauf.',
  'posting.open': 'Anzeige öffnen',
  'posting.application': 'Deine Bewerbung',
  'posting.applicationBody':
    'Was du an dieses Unternehmen geschickt hast. Fragen, Nachfragen und Feedback zu dieser Anzeige stützen sich darauf.',
  'posting.useCommon': 'Meinen allgemeinen Lebenslauf verwenden',
  'posting.view': '(ansehen)',
  'posting.useOwn': 'Einen für diese Anzeige geschriebenen Lebenslauf verwenden',
  'posting.coverLetter': 'Anschreiben',
  'posting.rewrite': 'Fragen neu schreiben',
  'posting.write': 'Fragen schreiben',

  'document.upload': 'PDF-, .txt- oder .md-Datei hochladen',
  'document.placeholder': 'Lade oben eine PDF-, .txt- oder .md-Datei hoch oder füge den Text hier ein.',

  'resume.title': 'Lebenslauf',
  'resume.intro':
    'Mit deinem Lebenslauf werden Fragen zu deiner Erfahrung geschrieben und deine Antworten daran gemessen. Er wird auf diesem Computer gespeichert; sein Text wird an das KI-Modell gesendet, wenn Fragen und Feedback geschrieben werden.',
  'resume.saved': 'Lebenslauf gespeichert.',
  'resume.upload': 'Datei hochladen (PDF, .txt oder .md)',
  'resume.extracted': 'Ausgelesener Text (korrigiere ihn, falls beim Auslesen etwas schiefgegangen ist)',
  'resume.orPaste': 'Oder Text einfügen',
  'resume.savedOn': ' · gespeichert am {date}',
  'resume.confirmDelete': 'Deinen Lebenslauf löschen?',

  'history.none': 'Noch keine Antworten. Beantworte eine Frage, dann erscheint sie hier.',
  'history.pick': 'Frage wählen',
  'history.notScored': 'Nicht bewertet',
  'history.review': 'Ansehen',
  'history.back': '← Verlauf',

  'attempt.confirmDelete':
    'Diesen Versuch und seine Aufnahmen löschen? Das lässt sich nicht rückgängig machen.',
  'attempt.deleteFailed': 'Löschen fehlgeschlagen: {error}',
  'attempt.loadFailed': 'Dieser Versuch konnte nicht geladen werden: {error}',
  'attempt.retry': 'Diese Frage noch einmal beantworten',
  'attempt.notScored': 'Dieser Versuch wurde nicht bewertet.',

  'score.english': 'Englisch',
  'score.content': 'Inhalt',
  'score.of': 'Bewertung: {title}',
  'score.change': '{change} gegenüber dem letzten Mal',
  'score.pronunciation': 'Aussprache',
  'score.intonation': 'Intonation',
  'score.stress': 'Betonung',
  'score.grammar': 'Grammatik',
  'score.vocabulary': 'Wortschatz',
  'score.naturalness': 'Natürlichkeit',
  'score.relevance': 'Relevanz',
  'score.structure': 'Aufbau',
  'score.specificity': 'Konkretheit',

  'feedback.speaking': 'Sprechen',
  'feedback.sentences': 'Sätze',
  'feedback.strengths': 'Stärken',
  'feedback.improvements': 'Das kannst du verbessern',
  'feedback.better': 'Eine stärkere Fassung deiner ersten Antwort',
  'feedback.listen': 'Anhören',

  'turns.noSpeech': '(keine Sprache erkannt)',
  'turns.clarity': 'Deutlichkeit {n}',
  'turns.pace': '{n} Wörter/Min.',
  'turns.unclear': 'Undeutlich:',
  'turns.watch': 'Aufnahme ansehen',
  'turns.download': 'Herunterladen',

  'interview.micUnavailable':
    'Das Mikrofon ist nicht verfügbar, deshalb kann die Antwort nicht aufgenommen werden.',
  'interview.usingCaption': '{error}. Stattdessen wird die Live-Mitschrift verwendet.',
  'interview.notSaved': 'Diese Antwort konnte nicht im Verlauf gespeichert werden: {error}',
  'interview.noSpeech':
    'Es wurde keine Sprache erkannt, deshalb gibt es keine Nachfrage. Versuch, noch einmal zu antworten.',
  'interview.followUpFailed': 'Es kam keine Nachfrage: {error}',
  'interview.noAudio': 'es wurde kein Ton aufgenommen',
  'interview.speakingNotScored': 'Intonation und Betonung wurden nicht bewertet: {error}',
  'interview.feedbackFailed': 'Es kam kein Feedback: {error}',
  'interview.notFound': 'Diese Frage gibt es nicht.',
  'interview.backToQuestions': 'Zurück zu den Fragen',
  'interview.back': '← Fragen',
  'interview.followUp': 'Nachfrage {n} / {total}',
  'interview.main': 'Hauptfrage',
  'interview.interviewer': 'Interviewer',
  'interview.you': 'Du',
  'interview.listenFirst': 'Hör dir die Frage an oder blende ihren Text ein, wenn du ihn brauchst.',
  'interview.hide': 'Frage ausblenden',
  'interview.show': 'Frage einblenden',
  'interview.listening': 'Hört zu…',
  'interview.downloadingRecognition':
    'Das Modell für die Spracherkennung wird heruntergeladen (nur beim ersten Mal){percent}… Sobald es fertig ist, wird deine Antwort in Text umgewandelt.',
  'interview.transcribing': 'Deine Antwort wird in Text umgewandelt…',
  'interview.preparing': 'Eine Nachfrage wird vorbereitet…',
  'interview.done': 'Das war alles zu dieser Frage. Deine Antworten sind im Verlauf gespeichert.',
  'interview.pickAnother': 'Andere Frage wählen',
  'interview.stopVoice': 'Stimme stoppen',
  'interview.replay': 'Frage noch einmal anhören',
  'interview.scoring': 'Wird bewertet…',
  'interview.getFeedback': 'Feedback holen',
  'interview.stopAnswer': 'Antwort beenden',
  'interview.startAnswer': 'Antwort starten',

  'store.questionsFailed': 'Die Fragen konnten nicht geladen werden: {error}',
  'store.historyFailed': 'Der Verlauf konnte nicht geladen werden: {error}',

  'settings.welcome': 'Willkommen – richten wir kurz alles ein',
  'settings.welcomeBody':
    'Zwei Dinge vor deinem ersten Interview: deine Sprache und ein KI-Modell. Beides kannst du jederzeit unter „Einstellungen“ ändern.',
  'settings.skip': 'Vorerst überspringen',
  'settings.yourLanguage': 'Deine Sprache',
  'settings.yourLanguageBody':
    'In dieser Sprache werden die Seiten angezeigt und dein Feedback erklärt. Fragen und Musterantworten bleiben auf Englisch.',
  'settings.yourLanguageNote':
    'Voreingestellt ist die Sprache deines Browsers. Deine Auswahl wird sofort gespeichert. Die meisten Sprachen der Seiten wurden von einer KI übersetzt und nicht von Muttersprachlern geprüft, manches kann daher etwas ungewohnt klingen.',
  'settings.voiceTitle': 'Stimme des Interviewers',
  'settings.voiceBody':
    'Die Stimme, mit der dein Interviewer spricht, amerikanisch oder britisch. Alle Stimmen laufen auf diesem Computer und sind im Stimmen-Download enthalten; ein Wechsel lädt also nichts weiter herunter.',
  'settings.voice': 'Stimme',
  'settings.ai': 'KI-Modell',
  'settings.aiBody':
    'Passende Fragen, Nachfragen und Feedback schreibt ein KI-Modell, für das du deinen eigenen API-Schlüssel mitbringst. Der Schlüssel wird nur auf diesem Computer gespeichert und nur an den Anbieter gesendet, den du auswählst.',
  'settings.current': 'Aktuell:',
  'settings.keyEnding': ' · Schlüssel endet auf {hint}',
  'settings.fromEnv':
    ' · aus der Umgebungsvariable LLM_MODEL. Wenn du hier speicherst, gilt stattdessen diese Einstellung.',
  'settings.noModel': 'Es ist noch kein Modell eingerichtet.',
  'settings.provider': 'Anbieter',
  'settings.otherProvider': 'Anderer (LiteLLM)',
  'settings.model': 'Modell',
  'settings.example': 'z. B. {example}',
  'settings.otherHelp': 'Schreib es als provider/model, so wie LiteLLM es benennt.',
  'settings.modelHelp':
    'Der Modellname, wie der Anbieter ihn angibt. Feedback zu Aussprache, Intonation und Betonung braucht ein Modell, das Audio annimmt, etwa Gemini.',
  'settings.apiKey': 'API-Schlüssel',
  'settings.keepKey': 'Leer lassen, um den gespeicherten Schlüssel zu behalten',
  'settings.pasteKey': 'Füge deinen API-Schlüssel ein',
  'settings.getKey': 'API-Schlüssel von {provider} holen',
  'settings.saveTest': 'Speichern und testen',
  'settings.saveFailed': 'Speichern fehlgeschlagen: {error}',
  'settings.saved': 'Gespeichert. Das Modell hat auf eine Testanfrage geantwortet, alles ist bereit.',
  'settings.testFailed': 'Gespeichert, aber die Testanfrage ist fehlgeschlagen. {error}',
  'settings.removeFailed': 'Entfernen fehlgeschlagen: {error}',
  'settings.openSource': 'Open Source',
  'settings.openSourceBody':
    'SOS My Interview ist Open Source unter der MIT-Lizenz. Die App baut auf den folgenden Projekten auf.',
  'settings.licenses': 'Vollständige Lizenztexte',
  'settings.voiceFailed': 'Die Stimme konnte nicht gewechselt werden: {error}',
  'settings.yourLanguageFailed': 'Die Sprache konnte nicht gespeichert werden: {error}',
}

export default de
