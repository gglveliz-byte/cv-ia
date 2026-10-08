const fs = require('fs');

/**
 * build.js - Script de compilación segura para Render
 * 
 * INVARIANTE DE SEGURIDAD:
 * Las API Keys privadas NUNCA deben inyectarse en archivos JavaScript descargables por el cliente (app.js).
 * El backend (server.py) se encarga de gestionar la clave de forma segura en el servidor.
 */

console.log('[+] Ejecutando compilación segura de CV-IA...');

const appJsPath = 'app.js';
if (fs.existsSync(appJsPath)) {
  let content = fs.readFileSync(appJsPath, 'utf8');

  // Asegurar que el marcador de clave quede vacío en el cliente para máxima seguridad
  content = content.replace('__DASHSCOPE_API_KEY__', '');
  
  // Configurar el endpoint de evaluación segura hacia el proxy local /api/evaluate
  content = content.replace(
    'baseUrl: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"',
    'baseUrl: "/api"'
  );

  fs.writeFileSync(appJsPath, content);
  console.log('[✓] app.js configurado en modo seguro (Credenciales blindadas en backend).');
} else {
  console.error('[-] Error: no se encontró app.js');
  process.exit(1);
}
