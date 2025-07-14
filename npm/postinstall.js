/**
 * Post-install script for Zoho MCP Server
 * 
 * Downloads the appropriate platform-specific binary from GitHub releases.
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const REPO = 'kkeeling/zoho-mcp';
const VERSION = require('./package.json').version;

// Get platform-specific binary name
function getBinaryName() {
  const platform = process.platform;
  const arch = process.arch;
  
  let platformName;
  switch (platform) {
    case 'darwin':
      platformName = 'macos';
      break;
    case 'linux':
      platformName = 'linux';
      break;
    case 'win32':
      platformName = 'win';
      break;
    default:
      console.error(`Unsupported platform: ${platform}`);
      process.exit(1);
  }
  
  let archName;
  switch (arch) {
    case 'x64':
      archName = 'x64';
      break;
    case 'arm64':
      archName = 'arm64';
      break;
    default:
      console.error(`Unsupported architecture: ${arch}`);
      process.exit(1);
  }
  
  const binaryName = `zoho-mcp-server-${platformName}-${archName}`;
  return platform === 'win32' ? `${binaryName}.exe` : binaryName;
}

// Download file from URL
function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    
    https.get(url, (response) => {
      // Handle redirects
      if (response.statusCode === 302 || response.statusCode === 301) {
        const redirectUrl = response.headers.location;
        downloadFile(redirectUrl, dest).then(resolve).catch(reject);
        return;
      }
      
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }
      
      response.pipe(file);
      
      file.on('finish', () => {
        file.close();
        resolve();
      });
      
      file.on('error', (err) => {
        fs.unlink(dest, () => {}); // Delete the file on error
        reject(err);
      });
    }).on('error', reject);
  });
}

// Main installation function
async function install() {
  console.log('Installing Zoho MCP Server binary...');
  
  // Create bin directory
  const binDir = path.join(__dirname, 'bin');
  if (!fs.existsSync(binDir)) {
    fs.mkdirSync(binDir, { recursive: true });
  }
  
  // Determine binary name and download URL
  const binaryName = getBinaryName();
  const downloadUrl = `https://github.com/${REPO}/releases/download/v${VERSION}/${binaryName}`;
  const binaryPath = path.join(binDir, binaryName);
  
  // Skip if binary already exists
  if (fs.existsSync(binaryPath)) {
    console.log(`Binary already exists: ${binaryPath}`);
    return;
  }
  
  console.log(`Downloading ${binaryName} from GitHub releases...`);
  console.log(`URL: ${downloadUrl}`);
  
  try {
    await downloadFile(downloadUrl, binaryPath);
    
    // Make binary executable on Unix-like systems
    if (process.platform !== 'win32') {
      fs.chmodSync(binaryPath, 0o755);
    }
    
    console.log('✓ Zoho MCP Server binary installed successfully!');
  } catch (err) {
    console.error('Failed to download binary:', err.message);
    console.error('\nPlease check:');
    console.error(`1. Release v${VERSION} exists at https://github.com/${REPO}/releases`);
    console.error(`2. Binary ${binaryName} is available in the release`);
    console.error('\nYou can also download manually and place it in:');
    console.error(binaryPath);
    process.exit(1);
  }
}

// Skip in development or if NO_INSTALL is set
if (process.env.NODE_ENV === 'development' || process.env.NO_INSTALL) {
  console.log('Skipping binary installation (development mode)');
  process.exit(0);
}

// Run installation
install().catch((err) => {
  console.error('Installation failed:', err);
  process.exit(1);
});