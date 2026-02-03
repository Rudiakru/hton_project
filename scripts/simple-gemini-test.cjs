#!/usr/bin/env node

/**
 * Einfacher Gemini API Test - korrigiertes Modell
 */

const https = require('https');
const fs = require('fs');

// API Key direkt aus .env lesen
const envContent = fs.readFileSync('.env', 'utf8');
const apiKeyMatch = envContent.match(/GEMINI_API_KEY=(.+)/);
const apiKey = apiKeyMatch ? apiKeyMatch[1].trim() : null;

if (!apiKey) {
  console.log('❌ Kein GEMINI_API_KEY gefunden in .env');
  process.exit(1);
}

console.log('✅ API Key gefunden:', apiKey.substring(0, 10) + '...');
console.log('🧪 Teste Gemini API mit gemini-1.5-flash...');

const testPrompt = {
  contents: [{
    parts: [{
      text: "Sag einfach nur 'Hallo, BMAD Lite funktioniert!' zurück."
    }]
  }]
};

const postData = JSON.stringify(testPrompt);

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

const req = https.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    console.log('📡 HTTP Status:', res.statusCode);

    if (res.statusCode === 200) {
      try {
        const response = JSON.parse(data);
        const text = response.candidates?.[0]?.content?.parts?.[0]?.text;
        console.log('✅ Gemini API funktioniert!');
        console.log('📝 Antwort:', text);
        console.log('🎉 BMAD Lite 2.0 ist bereit für echte AI-Integration!');
      } catch (error) {
        console.log('❌ Parse Fehler:', error.message);
        console.log('📄 Rohdaten:', data);
      }
    } else {
      console.log('❌ API Fehler:', data);
    }
  });
});

req.on('error', (error) => {
  console.log('❌ Netzwerk Fehler:', error.message);
});

req.write(postData);
req.end();