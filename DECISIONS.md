# Wichtige Entscheidungen - BMAD Lite 2.0

<!-- Neue Entscheidungen oben hinzufügen -->

## 2026-01-14: BMAD Lite 2.0 Einführung

Kontext: Migration von BMAD Full zu Lite-Version für bessere Produktivität und weniger Overhead.
Entscheidung: Implementierung von Cursor-nativen Features statt komplexer Scripts.
Alternativen:
- Vollautomatische Git-Hooks → Verworfen: Zu viel Wartung
- Custom TypeScript-Funktionen → Verworfen: API-Abhängigkeit
Auswirkung:
- Reduzierter Setup von Wochen auf 30 Minuten
- 80%+ Zeit für echtes Coding statt Prozess-Management
- Prompt-Templates statt ausführbarer Scripts