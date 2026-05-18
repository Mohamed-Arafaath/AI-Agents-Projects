#!/bin/bash
# Script to push AI Agents projects to GitHub

cd "/Users/apple/Library/CloudStorage/OneDrive-UniversityofPisa/Startup building/AI Agency Planning/AI Agents Course"

# Add all changes
git add .

# Commit with timestamp
git commit -m "Update projects and notes - $(date +'%Y-%m-%d %H:%M')"

# Push to GitHub
git push