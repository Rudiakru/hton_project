#!/usr/bin/env node

/**
 * Update Gemini API Key in .env file
 */

const fs = require('fs');

if (process.argv.length < 3) {
  console.log('💡 Verwendung: node scripts/update-api-key.cjs <neuer_api_key>');
  console.log('📝 Beispiel: node scripts/update-api-key.cjs AIzaSyD...');
  process.exit(1);
}

const newApiKey = process.argv[2];

if (!newApiKey.startsWith('AIza')) {
  console.log('❌ API Key scheint ungültig (sollte mit AIza beginnen)');
  process.exit(1);
}

const envContent = `# Environment Configuration Template
# Copy this file to .env and fill in your actual values

# Google Gemini AI API Key
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=${newApiKey}
`;

fs.writeFileSync('.env', envContent, 'utf8');

console.log('✅ API Key aktualisiert!');
console.log('🔑 Neuer Key:', newApiKey.substring(0, 20) + '...');
console.log('🧪 Teste mit: node scripts/simple-gemini-test.cjs');