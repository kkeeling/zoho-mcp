#!/usr/bin/env node
/**
 * Zoho MCP Server npm wrapper
 * 
 * This script runs the platform-specific binary for the Zoho MCP Server.
 * The binary is downloaded during npm install via the postinstall script.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Determine the platform-specific binary name
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
      throw new Error(`Unsupported platform: ${platform}`);
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
      throw new Error(`Unsupported architecture: ${arch}`);
  }
  
  const binaryName = `zoho-mcp-server-${platformName}-${archName}`;
  return platform === 'win32' ? `${binaryName}.exe` : binaryName;
}

// Get the path to the binary
function getBinaryPath() {
  const binaryName = getBinaryName();
  const binaryPath = path.join(__dirname, 'bin', binaryName);
  
  if (!fs.existsSync(binaryPath)) {
    console.error(`Binary not found: ${binaryPath}`);
    console.error('Please run: npm install');
    process.exit(1);
  }
  
  return binaryPath;
}

// Main execution
function main() {
  try {
    const binaryPath = getBinaryPath();
    
    // Make sure the binary is executable (Unix-like systems)
    if (process.platform !== 'win32') {
      try {
        fs.chmodSync(binaryPath, 0o755);
      } catch (err) {
        // Ignore chmod errors on Windows
      }
    }
    
    // Spawn the binary with all arguments passed through
    const args = process.argv.slice(2);
    const child = spawn(binaryPath, args, {
      stdio: 'inherit',
      env: process.env
    });
    
    // Handle exit
    child.on('exit', (code) => {
      process.exit(code || 0);
    });
    
    // Handle errors
    child.on('error', (err) => {
      console.error('Failed to start Zoho MCP Server:', err.message);
      process.exit(1);
    });
    
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}