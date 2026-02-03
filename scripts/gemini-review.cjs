#!/usr/bin/env node

/**
 * Gemini Review Script für BMAD Lite
 * Ruft Gemini API auf, um das System zu validieren
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Konfiguration
const BMA_DIR = path.join(__dirname, '..', '.bmad-lite');
const REVIEW_PROMPT_FILE = path.join(BMA_DIR, 'GEMINI-REVIEW-PROMPT.md');
const RESPONSE_FILE = path.join(BMA_DIR, 'GEMINI-REVIEW-RESPONSE.md');

async function loadReviewPrompt() {
  console.log('📖 Lade Review-Prompt...');

  if (!fs.existsSync(REVIEW_PROMPT_FILE)) {
    throw new Error(`Review-Prompt nicht gefunden: ${REVIEW_PROMPT_FILE}`);
  }

  return fs.readFileSync(REVIEW_PROMPT_FILE, 'utf8');
}

async function loadContextFiles() {
  console.log('📚 Lade Kontext-Dateien...');

  const contextFiles = [
    'README.md',
    'ZUSAMMENFASSUNG.md',
    path.join('..', 'PROJECT_GOALS.md'),
    path.join('..', 'CURRENT-STATUS.md'),
    'DECISIONS.md',
    'QUICK-THINK-TEMPLATE.md',
    'WEEKLY-REVIEW.md'
  ];

  let context = '';

  for (const file of contextFiles) {
    const filePath = path.join(BMA_DIR, file);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      context += `\n---\n${file}:\n${content}\n`;
    }
  }

  return context;
}

async function callGeminiAPI(prompt, context) {
  console.log('🤖 Sende Request an Gemini...');

  // API Key laden
  require('dotenv').config();
  const apiKey = process.env.GEMINI_API_KEY;

  if (!apiKey || apiKey === 'your_gemini_api_key_here') {
    throw new Error('GEMINI_API_KEY nicht konfiguriert. Hole Key von https://makersuite.google.com/app/apikey');
  }

  const fullPrompt = `Du bist ein Senior Software Architect. Analysiere das folgende BMAD Lite System kritisch.

${prompt}

KONTEXT:
${context}

Bitte gib eine detaillierte Analyse mit konkreten Empfehlungen.`;

  const requestData = {
    contents: [{
      parts: [{
        text: fullPrompt
      }]
    }]
  };

  const postData = JSON.stringify(requestData);

  const options = {
    hostname: 'generativelanguage.googleapis.com',
    port: 443,
    path: `/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(postData)
    }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          if (res.statusCode === 200) {
            const response = JSON.parse(data);
            const text = response.candidates?.[0]?.content?.parts?.[0]?.text;

            if (text) {
              resolve(text);
            } else {
              reject(new Error('Leere Antwort von Gemini API'));
            }
          } else if (res.statusCode === 429) {
            console.log('\n⚠️ TOKEN/QUOTA LIMIT ERREICHT (HTTP 429)');
            console.log('Das System wird jetzt ohne automatisierte Validierung fortfahren.');
            console.log('Bitte führe die Validierung manuell in Cursor durch.\n');
            resolve('### ⚠️ AUTOMATISCHE VALIDIERUNG FEHLGESCHLAGEN\n\nGrund: API-Kontingent (Tokens/Anfragen) überschritten. Bitte validiere den Ansatz manuell.');
          } else if (res.statusCode === 400 && data.includes('context window')) {
            console.log('\n⚠️ KONTEXT-FENSTER ÜBERSCHRITTEN (HTTP 400)');
            console.log('Die Anfrage ist zu groß. Versuche, die Kontext-Dateien zu reduzieren.\n');
            resolve('### ⚠️ AUTOMATISCHE VALIDIERUNG FEHLGESCHLAGEN\n\nGrund: Kontext-Fenster überschritten. Die Anfrage ist zu groß.');
          } else {
            reject(new Error(`API Fehler: HTTP ${res.statusCode} - ${data}`));
          }
        } catch (error) {
          reject(new Error(`Parse Fehler: ${error.message}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(new Error(`Netzwerk Fehler: ${error.message}`));
    });

    req.write(postData);
    req.end();
  });
}

async function saveResponse(response) {
  console.log('💾 Speichere Antwort...');

  const timestamp = new Date().toISOString().split('T')[0];
  const header = `# Gemini Review Response - ${timestamp}

Generiert am: ${new Date().toISOString()}

## Analyse

`;

  const fullContent = header + response;
  fs.writeFileSync(RESPONSE_FILE, fullContent, 'utf8');

  console.log(`✅ Review gespeichert in: ${RESPONSE_FILE}`);
}

async function main() {
  try {
    console.log('🚀 Starte Gemini Review für BMAD Lite...\n');

    // 1. Prompt laden
    const prompt = await loadReviewPrompt();

    // 2. Kontext laden
    const context = await loadContextFiles();

    // 3. Gemini API aufrufen
    console.log('📡 Rufe Gemini API auf...');
    const response = await callGeminiAPI(prompt, context);

    // 4. Antwort speichern
    await saveResponse(response);

    // 5. Preview anzeigen
    console.log('\n✅ Review erfolgreich abgeschlossen!');
    console.log(`📄 Antwort gespeichert in: ${RESPONSE_FILE}`);
    console.log('\n📋 Preview (erste 500 Zeichen):');
    console.log('─'.repeat(60));
    console.log(response.substring(0, 500) + (response.length > 500 ? '...' : ''));

  } catch (error) {
    console.error('\n❌ Fehler bei Gemini Review:', error.message);
    process.exit(1);
  }
}

// Script ausführen wenn direkt aufgerufen
if (require.main === module) {
  main();
}

module.exports = { main };