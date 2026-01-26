/**
 * Remotion Renderer Module
 * Handles video rendering using Remotion bundler and renderer
 */

const { bundle } = require('@remotion/bundler');
const { renderMedia, selectComposition } = require('@remotion/renderer');
const path = require('path');
const fs = require('fs').promises;

/**
 * Create a temporary Remotion project structure
 */
async function createTempProject(tsxFilePath, compositionId) {
  const projectDir = path.join(path.dirname(tsxFilePath), `project_${Date.now()}`);
  const srcDir = path.join(projectDir, 'src');

  await fs.mkdir(srcDir, { recursive: true });

  // Read the TSX content
  const tsxContent = await fs.readFile(tsxFilePath, 'utf-8');

  // Create index.ts that exports the composition
  const indexContent = `
import React from 'react';
import { Composition } from 'remotion';
import Component, { compositionConfig } from './Video';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id={compositionConfig.id}
        component={Component}
        durationInFrames={Math.round(compositionConfig.durationInSeconds * compositionConfig.fps)}
        fps={compositionConfig.fps}
        width={compositionConfig.width}
        height={compositionConfig.height}
      />
    </>
  );
};
`;

  // Save files
  await fs.writeFile(path.join(srcDir, 'index.ts'), indexContent, 'utf-8');
  await fs.writeFile(path.join(srcDir, 'Video.tsx'), tsxContent, 'utf-8');

  return { projectDir, entryPoint: path.join(srcDir, 'index.ts') };
}

/**
 * Render a video from TSX code
 */
async function renderVideo(options) {
  const {
    tsxFilePath,
    compositionId,
    outputPath,
    width = 1080,
    height = 1920,
    fps = 30,
    durationInFrames = 150
  } = options;

  let projectDir = null;

  try {
    console.log('Creating temporary project...');
    const { projectDir: tempDir, entryPoint } = await createTempProject(tsxFilePath, compositionId);
    projectDir = tempDir;

    console.log('Bundling project...');
    const bundleLocation = await bundle({
      entryPoint,
      onProgress: (progress) => {
        const percent = Math.round(progress * 100);
        if (percent % 10 === 0) {
          console.log(`Bundling: ${percent}%`);
        }
      },
    });

    console.log('Bundle complete, selecting composition...');
    const composition = await selectComposition({
      serveUrl: bundleLocation,
      id: compositionId,
    });

    console.log(`Rendering video: ${compositionId}`);
    await renderMedia({
      composition: {
        ...composition,
        durationInFrames,
        fps,
        width,
        height,
      },
      serveUrl: bundleLocation,
      codec: 'h264',
      outputLocation: outputPath,
      onProgress: ({ progress }) => {
        const percent = Math.round(progress * 100);
        if (percent % 10 === 0) {
          console.log(`Rendering: ${percent}%`);
        }
      },
    });

    console.log('Render complete!');

    // Verify output file exists
    await fs.access(outputPath);

    return outputPath;

  } catch (error) {
    console.error('Render error:', error);
    throw error;
  } finally {
    // Cleanup temporary project directory
    if (projectDir) {
      try {
        await fs.rm(projectDir, { recursive: true, force: true });
        console.log('Cleaned up temporary project directory');
      } catch (err) {
        console.error('Failed to cleanup project directory:', err);
      }
    }
  }
}

module.exports = {
  renderVideo,
};
