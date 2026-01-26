"""
CrewAI Tools for Motion Graphics Agent - CLOUD VERSION
Updated to use cloud-based Remotion renderer
"""

import os
import re
import requests
from pathlib import Path
from typing import Type, Dict, Any, ClassVar
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from openai import OpenAI

from model_motion import (
    MotionGraphicInput,
    CodeGenerationResult,
    PreviewResult,
    RenderResult
)

# CLOUD RENDERER URL - UPDATE THIS AFTER DEPLOYMENT!
RENDERER_URL = os.getenv("RENDERER_URL", "http://localhost:3000/render")

# =============================================================================
# TOOL 1: GENERATE MOTION GRAPHIC CODE
# =============================================================================

class GenerateCodeInput(BaseModel):
    """Input for generate_motion_graphic_code tool"""
    instruction: str = Field(description="What to create")
    duration: int = Field(description="Duration in seconds")
    format: str = Field(description="Video format: 16:9, 9:16, or 1:1")
    assets: Dict[str, str] = Field(description="Assets with paths")
    video_context: str = Field(description="Context about the video")
    style: str = Field(default="modern", description="Visual style")


class GenerateMotionGraphicCodeTool(BaseTool):
    name: str = "generate_motion_graphic_code"
    description: str = """
    Generates Remotion TSX code for a motion graphic.
    
    Input:
    - instruction: What to create (e.g., "Logo reveal with fade in")
    - duration: Duration in seconds (3-5)
    - format: Video format (16:9, 9:16, 1:1)
    - assets: Dictionary of assets with paths
    - video_context: Context about the video
    - style: Visual style
    
    Returns:
    - Generated Remotion TSX code
    - Component name
    - Composition ID
    """
    args_schema: Type[BaseModel] = GenerateCodeInput
    
    REMOTION_PROMPT : ClassVar[str] = """# Remotion TSX Video Generator

You are an expert Remotion video developer. Generate production-ready TSX code.

## Context

**Video Context:**
{video_context}

**What to Create:**
{instruction}

**Style:** {style}

## Specs

- **Duration**: {duration} seconds
- **Format**: {format} ({width}x{height})
- **FPS**: 30

## Available Assets

{assets_section}

## Code Structure (MANDATORY)

```tsx
import React from 'react';
import {{ useCurrentFrame, useVideoConfig, interpolate, Easing, AbsoluteFill }} from 'remotion';

export const compositionConfig = {{
  id: '{composition_id}',
  durationInSeconds: {duration},
  fps: 30,
  width: {width},
  height: {height},
}};

const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps, durationInFrames }} = useVideoConfig();

  // Animations here...

  return (
    <AbsoluteFill style={{{{ backgroundColor: '#1a1a2e' }}}}>
      {{/* Content */}}
    </AbsoluteFill>
  );
}};

export default {component_name};
```

## Rules

Code structure mandatory
Your output MUST follow this exact structure and sections:

```tsx
import React from 'react';
import {{ useCurrentFrame, useVideoConfig, interpolate, Easing, AbsoluteFill }} from 'remotion';

// =============================================================================
// COMPOSITION CONFIG (Required for auto-discovery)
// =============================================================================
export const compositionConfig = {{
  id: '[UniqueComponentName]',
  durationInSeconds: [1-5],
  fps: 30,
  width: 1080,
  height: 1920,
}};

// =============================================================================
// PRE-GENERATED DATA (if needed - computed once, NOT during render)
// =============================================================================
const seededRandom = (seed: number): number => {{
  const x = Math.sin(seed * 9999) * 10000;
  return x - Math.floor(x);
}};

// [Any arrays/objects for particles, items, etc. go here]

// =============================================================================
// MAIN COMPONENT
// =============================================================================
const [ComponentName]: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps, durationInFrames }} = useVideoConfig();

  // Animation calculations here...

  return (
    <AbsoluteFill style={{{{ backgroundColor: '#...' }}}}>
      {{/* Content */}}
    </AbsoluteFill>
  );
}};

export default [ComponentName];
```

Animation rules

1. ALL animations must be frame based using useCurrentFrame() and interpolate()
2. NEVER use useState, useEffect, setTimeout, or CSS animations
3. Use extrapolateLeft: 'clamp' and extrapolateRight: 'clamp' to prevent value overflow
4. Use Easing functions for professional motion (example Easing.out(Easing.cubic))
5. Stagger animations logically, do not animate everything at once
6. The composition ID cannot have underscores or hyphens
7. Make sure text components are clear and big enough to be seen on mobile screens

Layout rules

1. Use AbsoluteFill as the root container
2. Position elements with position: absolute and percentage based positioning
3. Reserve safe zones: top 10%, bottom 15% for platform UI overlays
4. Center important content vertically between 25% and 75% of screen height
5. Use transform: translate(-50%, -50%) with left: 50% for true centering

Typography guidelines
Headlines
72 to 120px, bold, high contrast

Subheadlines
36 to 48px

Body text
28 to 36px minimum for readability

Additional typography rules
Always set margin: 0 on text elements
Use textAlign: 'center' for centered layouts

Quality standards
Professional color schemes, avoid pure #000000 or #FFFFFF as backgrounds
Subtle background elements like gradients or particles to add depth
Text shadows or glows to improve readability
Smooth easing on all transitions

Final output rule
Generate ONLY the complete TSX code. No explanations before or after.


"""
    
    def _run(
        self,
        instruction: str,
        duration: int,
        format: str,
        assets: Dict[str, str],
        video_context: str,
        style: str = "modern"
    ) -> str:
        """Generate Remotion code"""
        
        # Get OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Dimensions
        dimensions = self._get_dimensions(format)
        
        # Component name
        component_name = self._generate_component_name(instruction)
        composition_id = component_name
        
        # Format assets
        assets_section = self._format_assets(assets)
        
        # Format prompt
        prompt = self.REMOTION_PROMPT.format(
            video_context=video_context,
            instruction=instruction,
            style=style,
            duration=duration,
            format=format,
            width=dimensions['width'],
            height=dimensions['height'],
            composition_id=composition_id,
            component_name=component_name,
            assets_section=assets_section
        )
        
        # Generate
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Remotion developer. Generate clean TSX code following the structure exactly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        code = response.choices[0].message.content
        code = self._extract_code(code)
        
        # Return as dict
        return {
            "code": code,
            "component_name": component_name,
            "composition_id": composition_id,
            "duration": duration,
            "width": dimensions['width'],
            "height": dimensions['height']
        }
    
    def _get_dimensions(self, format: str) -> dict:
        dimensions = {
            "16:9": {"width": 1920, "height": 1080},
            "9:16": {"width": 1080, "height": 1920},
            "1:1": {"width": 1080, "height": 1080}
        }
        return dimensions.get(format, {"width": 1080, "height": 1920})
    
    def _generate_component_name(self, instruction: str) -> str:
        words = re.findall(r'\w+', instruction)
        words = [w.capitalize() for w in words[:3]]
        return ''.join(words) or "MotionGraphic"
    
    def _format_assets(self, assets: Dict[str, str]) -> str:
        if not assets:
            return "No external assets - generate everything with code."
        
        lines = []
        for key, path in assets.items():
            lines.append(f"- **{key}**: {path}")
        return "\n".join(lines)
    
    def _extract_code(self, text: str) -> str:
        if "```tsx" in text:
            return text.split("```tsx")[1].split("```")[0].strip()
        elif "```typescript" in text:
            return text.split("```typescript")[1].split("```")[0].strip()
        elif "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text.strip()


# =============================================================================
# TOOL 2: PREVIEW MOTION GRAPHIC
# =============================================================================

class PreviewInput(BaseModel):
    """Input for preview_motion_graphic tool"""
    code: str = Field(description="Generated Remotion code")
    component_name: str = Field(description="Component name")
    composition_id: str = Field(description="Composition ID")
    request_id: str = Field(description="Unique request ID")


class PreviewMotionGraphicTool(BaseTool):
    name: str = "preview_motion_graphic"
    description: str = """
    Saves the generated code and prepares it for user preview.
    
    Input:
    - code: Generated Remotion TSX code
    - component_name: Component name
    - composition_id: Composition ID
    - request_id: Unique request ID
    
    Returns:
    - Path to saved code file
    - Preview message for user
    """
    args_schema: Type[BaseModel] = PreviewInput
    
    def _run(
        self,
        code: str,
        component_name: str,
        composition_id: str,
        request_id: str
    ) -> str:
        """Save code and create preview"""
        
        # Create preview directory
        preview_dir = Path("./motion_graphics_previews")
        preview_dir.mkdir(exist_ok=True)
        
        # Save code
        code_path = preview_dir / f"{request_id}.tsx"
        with open(code_path, 'w') as f:
            f.write(code)
        
        # Create preview message
        message = f"""
📝 Motion Graphic Preview Ready!

**File**: {code_path}
**Component**: {component_name}
**Composition ID**: {composition_id}

**Code Preview** (first 500 chars):
```tsx
{code[:500]}...
```

**To review:**
1. Check the code above
2. Provide feedback if changes needed
3. Approve to render final video

**What would you like to do?**
- Approve and render
- Request changes (describe what to change)
"""
        
        return {
            "code_path": str(code_path),
            "component_name": component_name,
            "composition_id": composition_id,
            "message": message
        }


# =============================================================================
# TOOL 3: REVISE MOTION GRAPHIC
# =============================================================================

class ReviseInput(BaseModel):
    """Input for revise_motion_graphic tool"""
    original_code: str = Field(description="Original code")
    feedback: str = Field(description="User's requested changes")


class ReviseMotionGraphicTool(BaseTool):
    name: str = "revise_motion_graphic"
    description: str = """
    Revises the motion graphic code based on user feedback.
    
    Input:
    - original_code: Current Remotion code
    - feedback: User's requested changes
    
    Returns:
    - Revised code
    - Component name
    - Composition ID
    """
    args_schema: Type[BaseModel] = ReviseInput
    
    def _run(self, original_code: str, feedback: str) -> str:
        """Revise code based on feedback"""
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""
Revise this Remotion code based on user feedback.

**Current Code:**
```tsx
{original_code}
```

**User Feedback:**
{feedback}

Apply the requested changes while maintaining:
- Same structure and composition config
- Frame-based animations
- Professional quality

Return ONLY the complete revised code. No explanations.
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Remotion developer. Revise code based on feedback."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        code = response.choices[0].message.content
        code = self._extract_code(code)
        
        # Extract component info
        component_name = self._extract_component_name(code)
        
        return {
            "code": code,
            "component_name": component_name,
            "composition_id": component_name
        }
    
    def _extract_code(self, text: str) -> str:
        if "```tsx" in text:
            return text.split("```tsx")[1].split("```")[0].strip()
        elif "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text.strip()
    
    def _extract_component_name(self, code: str) -> str:
        match = re.search(r'const\s+(\w+):\s*React\.FC', code)
        return match.group(1) if match else "MotionGraphic"


# =============================================================================
# TOOL 4: RENDER MOTION GRAPHIC (CLOUD VERSION)
# =============================================================================

class RenderInput(BaseModel):
    """Input for render_motion_graphic tool"""
    code_path: str = Field(description="Path to TSX file")
    composition_id: str = Field(description="Composition ID")
    output_name: str = Field(description="Output filename (without extension)")
    duration: int = Field(default=5, description="Duration in seconds")
    width: int = Field(default=1080, description="Video width")
    height: int = Field(default=1920, description="Video height")


class RenderMotionGraphicTool(BaseTool):
    name: str = "render_motion_graphic"
    description: str = """
    Renders the final motion graphic video using cloud-based Remotion renderer.
    
    Input:
    - code_path: Path to the TSX file
    - composition_id: Composition ID from the code
    - output_name: Output filename
    - duration: Duration in seconds
    - width: Video width
    - height: Video height
    
    Returns:
    - Status (success/failed)
    - Video path if successful
    - Error message if failed
    """
    args_schema: Type[BaseModel] = RenderInput
    
    def _run(
        self,
        code_path: str,
        composition_id: str,
        output_name: str,
        duration: int = 5,
        width: int = 1080,
        height: int = 1920
    ) -> str:
        """Render video with cloud renderer"""
        
        try:
            # Read TSX code
            with open(code_path, 'r') as f:
                tsx_code = f.read()
            
            print(f"Sending render request to {RENDERER_URL}...")
            
            # Send to cloud renderer
            response = requests.post(
                RENDERER_URL,
                json={
                    'tsx_code': tsx_code,
                    'composition_id': composition_id,
                    'duration': duration,
                    'width': width,
                    'height': height,
                    'fps': 30
                },
                timeout=180  # 3 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "video_path": result.get('video_path', 'N/A'),
                    "filename": result.get('filename', output_name + '.mp4'),
                    "render_time": result.get('render_time_seconds', 0),
                    "file_size_mb": result.get('file_size_mb', 0),
                    "message": f"✅ Video rendered successfully!\n{result.get('message', '')}"
                }
            else:
                error_msg = response.json().get('error', response.text) if response.text else f"HTTP {response.status_code}"
                return {
                    "status": "failed",
                    "error": f"Cloud render failed: {error_msg}"
                }
        
        except requests.Timeout:
            return {
                "status": "failed",
                "error": "Render timeout (exceeded 3 minutes). Try a shorter video or upgrade cloud plan."
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Render error: {str(e)}"
            }
