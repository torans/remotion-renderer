/**
 * Remotion Cloud Renderer - Express Server
 * Receives TSX code from Motion Graphics Agent and renders MP4 videos
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const { renderVideo } = require('./renderer');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Directories
const TEMP_DIR = path.join(__dirname, 'temp');
const OUTPUT_DIR = path.join(__dirname, 'output');

// Ensure directories exist
async function ensureDirectories() {
  await fs.mkdir(TEMP_DIR, { recursive: true });
  await fs.mkdir(OUTPUT_DIR, { recursive: true });
}

// Health check endpoint
app.get('/', (req, res) => {
  res.json({ 
    status: 'ok',
    message: 'Remotion Cloud Renderer is running',
    version: '1.0.0'
  });
});

// Render endpoint
app.post('/render', async (req, res) => {
  const startTime = Date.now();
  let tsxFilePath = null;
  
  try {
    const { tsx_code, composition_id, duration = 5, width = 1080, height = 1920, fps = 30 } = req.body;

    // Validate input
    if (!tsx_code) {
      return res.status(400).json({ error: 'tsx_code is required' });
    }

    if (!composition_id) {
      return res.status(400).json({ error: 'composition_id is required' });
    }

    console.log(`[${new Date().toISOString()}] Starting render for composition: ${composition_id}`);

    // Generate unique filename
    const timestamp = Date.now();
    const filename = `${composition_id}_${timestamp}`;
    tsxFilePath = path.join(TEMP_DIR, `${filename}.tsx`);
    const outputPath = path.join(OUTPUT_DIR, `${filename}.mp4`);

    // Save TSX file
    await fs.writeFile(tsxFilePath, tsx_code, 'utf-8');
    console.log(`[${new Date().toISOString()}] TSX file saved: ${tsxFilePath}`);

    // Render video
    console.log(`[${new Date().toISOString()}] Starting Remotion render...`);
    await renderVideo({
      tsxFilePath,
      compositionId: composition_id,
      outputPath,
      width,
      height,
      fps,
      durationInFrames: Math.round(duration * fps)
    });

    const renderTime = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`[${new Date().toISOString()}] Render completed in ${renderTime}s`);

    // Get file stats
    const stats = await fs.stat(outputPath);
    const fileSizeMB = (stats.size / (1024 * 1024)).toFixed(2);

    // Return success response
    res.json({
      status: 'success',
      video_path: outputPath,
      filename: `${filename}.mp4`,
      composition_id,
      duration_seconds: duration,
      render_time_seconds: parseFloat(renderTime),
      file_size_mb: parseFloat(fileSizeMB),
      message: `Video rendered successfully in ${renderTime}s`
    });

    // Cleanup TSX file after successful render
    setTimeout(async () => {
      try {
        await fs.unlink(tsxFilePath);
        console.log(`[${new Date().toISOString()}] Cleaned up TSX file: ${tsxFilePath}`);
      } catch (err) {
        console.error(`Failed to cleanup TSX file: ${err.message}`);
      }
    }, 5000);

  } catch (error) {
    console.error(`[${new Date().toISOString()}] Render error:`, error);
    
    // Cleanup on error
    if (tsxFilePath) {
      try {
        await fs.unlink(tsxFilePath);
      } catch (err) {
        // Ignore cleanup errors
      }
    }

    res.status(500).json({
      status: 'error',
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

// Download endpoint (optional - for getting rendered videos)
app.get('/download/:filename', async (req, res) => {
  try {
    const filename = req.params.filename;
    const filepath = path.join(OUTPUT_DIR, filename);

    // Check if file exists
    await fs.access(filepath);

    res.download(filepath, filename, (err) => {
      if (err) {
        console.error('Download error:', err);
        res.status(500).json({ error: 'Download failed' });
      }
    });
  } catch (error) {
    res.status(404).json({ error: 'File not found' });
  }
});

// Start server
async function start() {
  try {
    await ensureDirectories();
    console.log('Directories initialized');

    app.listen(PORT, () => {
      console.log('');
      console.log('╔════════════════════════════════════════════════════════════╗');
      console.log('║                                                            ║');
      console.log('║     🎬 Remotion Cloud Renderer                             ║');
      console.log('║                                                            ║');
      console.log(`║     Server running on port ${PORT}                            ║`);
      console.log('║                                                            ║');
      console.log('╚════════════════════════════════════════════════════════════╝');
      console.log('');
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Handle shutdown gracefully
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  process.exit(0);
});

start();
