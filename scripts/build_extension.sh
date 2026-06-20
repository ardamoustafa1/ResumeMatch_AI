#!/usr/bin/env bash
set -e

# Package Chrome Extension
EXTENSION_DIR="extension"
BUILD_DIR="build/extension"
OUTPUT_ZIP="ResumeMatch_Extension.zip"

echo "Building Chrome Extension..."

mkdir -p "$BUILD_DIR"

# Copy files
cp -r "$EXTENSION_DIR/"* "$BUILD_DIR/"

# Remove unnecessary dev files if any
rm -rf "$BUILD_DIR/.DS_Store"

# Create zip
cd "$BUILD_DIR"
zip -r "../$OUTPUT_ZIP" ./*
cd ../..

echo "Extension packaged successfully at build/$OUTPUT_ZIP"
