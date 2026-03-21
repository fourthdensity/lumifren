#!/usr/bin/env python3

import os
import subprocess

# Set the base directory of the nano-banana-pro skill
base_dir = "/home/brewuser/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/nano-banana-pro"

# Define the prompt for generating the banana image
prompt = "A vibrant, hyper-realistic banana with a glossy yellow peel and tiny brown spots, set against a clean white background"

# Define the output filename with timestamp
import datetime
timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
output_filename = f"{timestamp}-banana.png"

# Run the generate_image.py script
command = [
    "uv", "run", 
    f"{base_dir}/scripts/generate_image.py",
    "--prompt", prompt,
    "--filename", output_filename,
    "--resolution", "1K"
]

# Execute the command
try:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    print(f"Image generated: {output_filename}")
    print("MEDIA:", output_filename)
except subprocess.CalledProcessError as e:
    print(f"Error generating image: {e.stderr}")