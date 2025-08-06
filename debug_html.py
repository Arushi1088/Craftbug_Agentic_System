#!/usr/bin/env python3
import tempfile
import subprocess
import re
from pathlib import Path

def normalize_html_for_comparison(html_content):
    """Normalize HTML content for comparison, removing dynamic elements"""
    # Replace timestamps with fixed value
    html_content = re.sub(
        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        '2024-01-01 12:00:00',
        html_content
    )
    
    # Replace dynamic UUIDs/IDs with fixed value
    html_content = re.sub(
        r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',
        'test-uuid',
        html_content
    )
    
    # Replace random numeric IDs (like in titles) with fixed value
    html_content = re.sub(
        r'UX Analysis Report - [a-f0-9]+',
        'UX Analysis Report - test-id',
        html_content
    )
    
    # Replace report IDs in content (numeric or hex)
    html_content = re.sub(
        r'Report ID: [a-f0-9]+',
        'Report ID: test-id',
        html_content
    )
    
    # Remove extra whitespace and normalize line endings
    html_content = re.sub(r'\s+', ' ', html_content)
    html_content = html_content.strip()
    
    return html_content

# Generate new HTML
with tempfile.TemporaryDirectory() as temp_dir:
    cmd = ['python3', 'bin/ux-analyze', 'url-scenario', 'https://example.com', 
           'scenarios/office_tests.yaml', '--test-mode', '--output_dir', temp_dir]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Error: {result.stderr}')
        exit(1)
    
    # Find HTML file
    html_files = list(Path(temp_dir).glob('*.html'))
    if len(html_files) != 1:
        print(f'Expected 1 HTML file, found {len(html_files)}')
        exit(1)
    
    # Read and normalize generated
    with open(html_files[0]) as f:
        generated_content = f.read()
    
    # Read golden file
    with open('tests/golden/url_scenario_office_tests.html') as f:
        golden_content = f.read()
    
    # Normalize both
    normalized_generated = normalize_html_for_comparison(generated_content)
    normalized_golden = normalize_html_for_comparison(golden_content)
    
    # Write for comparison
    with open('/tmp/generated_normalized.html', 'w') as f:
        f.write(normalized_generated)
    
    with open('/tmp/golden_normalized.html', 'w') as f:
        f.write(normalized_golden)
    
    print(f"Generated length: {len(normalized_generated)}")
    print(f"Golden length: {len(normalized_golden)}")
    print(f"Are equal: {normalized_generated == normalized_golden}")
    
    # Find first difference
    for i, (g, h) in enumerate(zip(normalized_generated, normalized_golden)):
        if g != h:
            print(f"First difference at position {i}:")
            print(f"Generated: {repr(normalized_generated[max(0, i-10):i+10])}")
            print(f"Golden:    {repr(normalized_golden[max(0, i-10):i+10])}")
            break
