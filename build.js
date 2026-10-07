const fs = require('fs');

// Obtener la clave desde las variables de entorno de Render
const apiKey = process.env.DASHSCOPE_API_KEY || '';

if (!apiKey) {
  console.warn('[!] ADVERTENCIA: No se encontró la variable DASHSCOPE_API_KEY en Render.');
} else {
  console.log('[+] DASHSCOPE_API_KEY detectada correctamente.');
}

const appJsPath = 'app.js';
if (fs.existsSync(appJsPath)) {
  let content = fs.readFileSync(appJsPath, 'utf8');
  content = content.replace('__DASHSCOPE_API_KEY__', apiKey);
  fs.writeFileSync(appJsPath, content);
  console.log('[✓] Variable de entorno inyectada con éxito en app.js para producción.');
} else {
  console.error('[-] Error: no se encontró app.js');
  process.exit(1);
}
