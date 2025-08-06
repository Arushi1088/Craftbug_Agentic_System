#!/usr/bin/env python3
"""
Golden File Snapshot Tests for UX Analyzer
Ensures consistent output by comparing against golden reference files
"""

import json
import pytest
import subprocess
import os
import sys
from pathlib import Path
from deepdiff import DeepDiff
import re
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestGoldenFiles:
    """Test suite for golden file validation"""
    
    @pytest.fixture
    def golden_dir(self):
        """Return path to golden files directory"""
        return Path(__file__).parent / "golden"
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test outputs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def normalize_json_for_comparison(self, data):
        """Normalize JSON data for comparison by removing/fixing dynamic fields"""
        if isinstance(data, dict):
            # Remove or normalize dynamic fields
            normalized = data.copy()
            
            # Remove fields that are always dynamic
            dynamic_fields = ['timestamp', 'analysis_id']
            for field in dynamic_fields:
                if field in normalized:
                    normalized[field] = 'NORMALIZED'
            
            # Recursively normalize nested objects
            for key, value in normalized.items():
                normalized[key] = self.normalize_json_for_comparison(value)
            
            return normalized
        elif isinstance(data, list):
            return [self.normalize_json_for_comparison(item) for item in data]
        else:
            return data
    
    def normalize_html_for_comparison(self, html_content):
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
        
        # Replace 8-character hex IDs (like analysis IDs)
        html_content = re.sub(
            r'\b[a-f0-9]{8}\b',
            'test-id',
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
    
    @pytest.mark.parametrize("test_case", [
        {
            "name": "url_scenario_office_tests",
            "cmd": ["python3", "bin/ux-analyze", "url-scenario", "https://example.com", 
                   "scenarios/office_tests.yaml", "--json_out", "--test-mode"],
            "golden_file": "url_scenario_office_tests.json",
            "output_type": "json"
        },
        {
            "name": "mock_scenario_office_tests", 
            "cmd": ["python3", "bin/ux-analyze", "mock-scenario", "/mock/office/word",
                   "scenarios/office_tests.yaml", "--json_out", "--test-mode"],
            "golden_file": "mock_scenario_office_tests.json",
            "output_type": "json"
        }
    ])
    def test_cli_json_output(self, test_case, golden_dir, temp_output_dir):
        """Test CLI JSON output against golden files"""
        # Modify command to use temp output directory
        cmd = test_case["cmd"] + ["--output_dir", temp_output_dir]
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        # Check command succeeded
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        # Find the generated JSON file
        json_files = list(Path(temp_output_dir).glob("*.json"))
        assert len(json_files) == 1, f"Expected 1 JSON file, found {len(json_files)}"
        
        generated_file = json_files[0]
        golden_file = golden_dir / test_case["golden_file"]
        
        # Load and normalize both files
        with open(generated_file) as f:
            generated_data = json.load(f)
        
        with open(golden_file) as f:
            golden_data = json.load(f)
        
        # Normalize for comparison
        normalized_generated = self.normalize_json_for_comparison(generated_data)
        normalized_golden = self.normalize_json_for_comparison(golden_data)
        
        # Compare using DeepDiff for better error messages
        diff = DeepDiff(normalized_golden, normalized_generated, ignore_order=True)
        
        assert not diff, f"JSON output differs from golden file:\n{diff}"
    
    @pytest.mark.parametrize("test_case", [
        {
            "name": "url_scenario_office_tests_html",
            "cmd": ["python3", "bin/ux-analyze", "url-scenario", "https://example.com", 
                   "scenarios/office_tests.yaml", "--test-mode"],
            "golden_file": "url_scenario_office_tests.html",
            "output_type": "html"
        }
    ])
    def test_cli_html_output(self, test_case, golden_dir, temp_output_dir):
        """Test CLI HTML output against golden files"""
        # Modify command to use temp output directory
        cmd = test_case["cmd"] + ["--output_dir", temp_output_dir]
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        # Check command succeeded
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        # Find the generated HTML file
        html_files = list(Path(temp_output_dir).glob("*.html"))
        assert len(html_files) == 1, f"Expected 1 HTML file, found {len(html_files)}"
        
        generated_file = html_files[0]
        golden_file = golden_dir / test_case["golden_file"]
        
        # Load and normalize both files
        with open(generated_file) as f:
            generated_content = f.read()
        
        with open(golden_file) as f:
            golden_content = f.read()
        
        # Normalize for comparison
        normalized_generated = self.normalize_html_for_comparison(generated_content)
        normalized_golden = self.normalize_html_for_comparison(golden_content)
        
        # Compare normalized content
        assert normalized_generated == normalized_golden, "HTML output differs from golden file"
    
    def test_golden_files_exist(self, golden_dir):
        """Verify all required golden files exist"""
        required_files = [
            "url_scenario_office_tests.json",
            "mock_scenario_office_tests.json", 
            "url_scenario_office_tests.html"
        ]
        
        for filename in required_files:
            golden_file = golden_dir / filename
            assert golden_file.exists(), f"Golden file missing: {filename}"
            assert golden_file.stat().st_size > 0, f"Golden file empty: {filename}"
    
    def test_golden_json_structure(self, golden_dir):
        """Validate structure of golden JSON files"""
        json_files = ["url_scenario_office_tests.json", "mock_scenario_office_tests.json"]
        
        for filename in json_files:
            golden_file = golden_dir / filename
            
            with open(golden_file) as f:
                data = json.load(f)
            
            # Validate required top-level fields
            required_fields = [
                "analysis_id", "timestamp", "type", "overall_score", 
                "scenario_results", "module_results", "metadata"
            ]
            
            for field in required_fields:
                assert field in data, f"Missing required field '{field}' in {filename}"
            
            # Validate scenario results structure
            assert isinstance(data["scenario_results"], list), f"scenario_results must be list in {filename}"
            assert len(data["scenario_results"]) > 0, f"scenario_results empty in {filename}"
            
            # Validate module results structure
            assert isinstance(data["module_results"], dict), f"module_results must be dict in {filename}"
            assert len(data["module_results"]) > 0, f"module_results empty in {filename}"
            
            # Validate score ranges
            assert 0 <= data["overall_score"] <= 100, f"Invalid overall_score in {filename}"


class TestAPIGoldenFiles:
    """Test API endpoints against golden outputs"""
    
    @pytest.fixture
    def api_base_url(self):
        """Base URL for API testing"""
        return "http://localhost:8000"
    
    @pytest.mark.asyncio
    async def test_api_scenarios_endpoint(self, api_base_url):
        """Test the scenarios listing endpoint"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base_url}/api/scenarios")
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert "scenarios" in data
            assert "count" in data
            assert isinstance(data["scenarios"], list)
            assert data["count"] == len(data["scenarios"])
            
            # Validate scenario structure
            for scenario in data["scenarios"]:
                required_fields = ["filename", "path", "name", "description"]
                for field in required_fields:
                    assert field in scenario, f"Missing field '{field}' in scenario"


class TestPerformanceRegression:
    """Performance regression tests"""
    
    def test_cli_performance_baseline(self, tmp_path):
        """Ensure CLI commands complete within reasonable time"""
        import time
        
        start_time = time.time()
        
        result = subprocess.run([
            "python3", "bin/ux-analyze", "url-scenario", "https://example.com",
            "scenarios/office_tests.yaml", "--json_out", "--test-mode",
            "--output_dir", str(tmp_path)
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert duration < 10.0, f"Command took too long: {duration:.2f}s"
    
    def test_deterministic_output_consistency(self, tmp_path):
        """Ensure multiple runs with test-mode produce identical output"""
        cmd = [
            "python3", "bin/ux-analyze", "url-scenario", "https://example.com",
            "scenarios/office_tests.yaml", "--json_out", "--test-mode"
        ]
        
        results = []
        for i in range(3):
            output_dir = tmp_path / f"run_{i}"
            output_dir.mkdir()
            
            result = subprocess.run(
                cmd + ["--output_dir", str(output_dir)],
                capture_output=True, text=True
            )
            
            assert result.returncode == 0
            
            json_files = list(output_dir.glob("*.json"))
            assert len(json_files) == 1
            
            with open(json_files[0]) as f:
                data = json.load(f)
            
            results.append(data)
        
        # All runs should produce identical output
        for i in range(1, len(results)):
            assert results[0] == results[i], f"Run {i} differs from run 0"


def test_integration_with_existing_system():
    """Test that golden file system integrates with existing codebase"""
    # Test scenario executor can be imported
    from scenario_executor import ScenarioExecutor, get_available_scenarios
    
    # Test deterministic mode
    executor = ScenarioExecutor(deterministic_mode=True, fixed_seed=12345)
    assert executor.deterministic_mode == True
    assert executor.fixed_seed == 12345
    
    # Test available scenarios
    scenarios = get_available_scenarios()
    assert len(scenarios) > 0
    
    # Test at least office_tests.yaml is available
    scenario_names = [s["filename"] for s in scenarios]
    assert "office_tests.yaml" in scenario_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
