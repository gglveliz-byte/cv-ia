const fs = require('fs');

// Obtener la clave y configuración desde las variables de entorno de Render
const apiKey = process.env.QWEN_API_KEY || process.env.DASHSCOPE_API_KEY || '';
const baseUrl = process.env.QWEN_BASE_URL || '';
const model = process.env.QWEN_MODEL || '';

if (!apiKey) {
  console.warn('[!] ADVERTENCIA: No se encontró QWEN_API_KEY ni DASHSCOPE_API_KEY en Render.');
} else {
  console.log('[+] QWEN_API_KEY / DASHSCOPE_API_KEY detectada correctamente.');
}

const appJsPath = 'app.js';
if (fs.existsSync(appJsPath)) {
  let content = fs.readFileSync(appJsPath, 'utf8');
  content = content.replace('__DASHSCOPE_API_KEY__', apiKey);
  if (baseUrl) {
    content = content.replace('https://dashscope-intl.aliyuncs.com/compatible-mode/v1', baseUrl);
  }
  if (model) {
    content = content.replace('qwen3.8-flash', model);
  }
  fs.writeFileSync(appJsPath, content);
  console.log('[✓] Variables de entorno inyectadas con éxito en app.js para producción.');
} else {
  console.error('[-] Error: no se encontró app.js');
  process.exit(1);
}
