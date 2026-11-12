#!/usr/bin/env python3
"""
Dynamic Island Extension - Code Quality & Integrity Tests
Validates metadata, schemas, JavaScript syntax, icons, and CSS classes.
Can be executed with: python3 -m unittest tests/test_code_quality.py
"""

import json
import os
import subprocess
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDynamicIslandCodeQuality(unittest.TestCase):
    def setUp(self):
        self.root = REPO_ROOT

    def test_metadata_json_validity(self):
        """Validate metadata.json structure and compatibility."""
        meta_path = os.path.join(self.root, 'metadata.json')
        self.assertTrue(os.path.isfile(meta_path), "metadata.json not found")
        with open(meta_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data.get('uuid'), 'dynamic-island@pheem49')
        self.assertIn('name', data)
        self.assertIn('description', data)
        self.assertIn('shell-version', data)
        self.assertIn('46', data['shell-version'], "Shell version 46 must be supported")

    def test_schema_compilation_and_keys(self):
        """Validate GSettings XML schema syntax and key definitions."""
        schemas_dir = os.path.join(self.root, 'schemas')
        xml_path = os.path.join(schemas_dir, 'org.gnome.shell.extensions.dynamic-island-pheem49.gschema.xml')
        self.assertTrue(os.path.isfile(xml_path), "GSchema XML not found")

        # Compile test with glib-compile-schemas
        res = subprocess.run(
            ['glib-compile-schemas', '--strict', '--dry-run', schemas_dir],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"Schema compilation failed: {res.stderr}")

        # Parse XML tree and verify critical keys
        tree = ET.parse(xml_path)
        root = tree.getroot()
        schema = root.find(".//schema[@id='org.gnome.shell.extensions.dynamic-island-pheem49']")
        self.assertIsNotNone(schema, "Schema ID not found in XML")

        defined_keys = {k.attrib.get('name') for k in schema.findall('key')}
        expected_keys = {
            'position', 'margin', 'width', 'height', 'text-width',
            'expand-on', 'hide-in-fullscreen', 'show-notifications',
            'show-volume', 'show-battery', 'show-recording',
            'show-bluetooth', 'show-progress'
        }
        for key in expected_keys:
            self.assertIn(key, defined_keys, f"Expected key '{key}' missing from schema")

    def test_javascript_syntax(self):
        """Validate syntax for all JavaScript files using node -c."""
        js_files = [
            'extension.js',
            'island.js',
            'prefs.js',
            'sources/battery.js',
            'sources/bluetooth.js',
            'sources/media.js',
            'sources/notification.js',
            'sources/osd.js',
            'sources/progress.js',
            'sources/recording.js',
        ]
        for rel_path in js_files:
            full_path = os.path.join(self.root, rel_path)
            self.assertTrue(os.path.isfile(full_path), f"File {rel_path} does not exist")
            res = subprocess.run(['node', '-c', full_path], capture_output=True, text=True)
            self.assertEqual(
                res.returncode, 0,
                f"Syntax error in {rel_path}:\n{res.stderr}"
            )

    def test_required_icons_exist(self):
        """Check presence of essential SVG icons used in island controls."""
        icons_dir = os.path.join(self.root, 'icons')
        self.assertTrue(os.path.isdir(icons_dir), "icons directory not found")
        required_icons = ['play.svg', 'pause.svg', 'next.svg', 'previous.svg']
        for icon in required_icons:
            icon_path = os.path.join(icons_dir, icon)
            self.assertTrue(os.path.isfile(icon_path), f"Required icon {icon} missing")

    def test_stylesheet_classes(self):
        """Verify stylesheet.css exists and defines core CSS classes."""
        css_path = os.path.join(self.root, 'stylesheet.css')
        self.assertTrue(os.path.isfile(css_path), "stylesheet.css not found")
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        required_classes = [
            '.di-island',
            '.di-handle',
            '.di-island-tucked',
            '.di-toast',
            '.di-btn',
            '.di-art'
        ]
        for cls in required_classes:
            self.assertIn(cls, css_content, f"CSS class '{cls}' not found in stylesheet.css")


if __name__ == '__main__':
    unittest.main()
