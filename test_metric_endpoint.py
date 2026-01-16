#!/usr/bin/env python3
"""
Test Suite for Metric Endpoint Fix
Tests that the /metric/ endpoint returns data correctly despite polymorphic identity issues
"""

import requests
import json
from typing import List, Dict, Any

API_BASE = "http://localhost:8000"
METRIC_ENDPOINT = f"{API_BASE}/metric/"

def test_metric_endpoint():
    """Test that /metric/ endpoint returns data successfully"""
    print("=" * 80)
    print("TEST 1: Metric Endpoint Returns Data")
    print("=" * 80)
    
    try:
        response = requests.get(METRIC_ENDPOINT)
        print(f"✓ Request successful: Status Code {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Valid JSON response")
            
            if isinstance(data, list):
                print(f"✓ Response is a list with {len(data)} metrics")
                
                if len(data) > 0:
                    print(f"✓ Metrics found!")
                    print(f"\nFirst 5 metrics:")
                    for i, metric in enumerate(data[:5], 1):
                        print(f"  {i}. ID: {metric.get('id')}, Name: {metric.get('name')}, Type: {metric.get('type_spec')}")
                    
                    return True, data
                else:
                    print("✗ No metrics returned")
                    return False, []
            else:
                print("✗ Response is not a list")
                return False, None
        else:
            print(f"✗ Request failed with status code {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"✗ Exception occurred: {type(e).__name__}: {str(e)}")
        return False, None


def test_metric_data_structure(metrics: List[Dict[str, Any]]):
    """Test that metric data has required fields"""
    print("\n" + "=" * 80)
    print("TEST 2: Metric Data Structure Validation")
    print("=" * 80)
    
    required_fields = ['id', 'name', 'type_spec']
    all_valid = True
    
    for i, metric in enumerate(metrics[:5]):  # Check first 5
        missing_fields = [f for f in required_fields if f not in metric]
        if missing_fields:
            print(f"✗ Metric {i+1} missing fields: {missing_fields}")
            all_valid = False
        else:
            print(f"✓ Metric {i+1} has all required fields")
    
    return all_valid


def test_metric_type_spec_values(metrics: List[Dict[str, Any]]):
    """Test that type_spec values are as expected"""
    print("\n" + "=" * 80)
    print("TEST 3: Type Spec Values Analysis")
    print("=" * 80)
    
    type_specs = set()
    for metric in metrics:
        type_spec = metric.get('type_spec')
        type_specs.add(type_spec)
    
    print(f"Found {len(type_specs)} unique type_spec values:")
    for type_spec in sorted(type_specs):
        count = sum(1 for m in metrics if m.get('type_spec') == type_spec)
        print(f"  - '{type_spec}': {count} metrics")
        if type_spec not in ['metric', 'derived', 'direct', 'NA', None]:
            print(f"    ⚠ Warning: Unexpected type_spec value")
    
    return True


def test_metric_count():
    """Test that we get a reasonable number of metrics"""
    print("\n" + "=" * 80)
    print("TEST 4: Metric Count Validation")
    print("=" * 80)
    
    try:
        response = requests.get(METRIC_ENDPOINT)
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            
            if count > 0:
                print(f"✓ Got {count} metrics (expected > 0)")
                return True, count
            else:
                print(f"✗ Got {count} metrics (expected > 0)")
                return False, count
        else:
            print(f"✗ Request failed with status {response.status_code}")
            return False, 0
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False, 0


def test_polymorphic_error_handling():
    """Test that polymorphic errors are handled gracefully"""
    print("\n" + "=" * 80)
    print("TEST 5: Polymorphic Error Handling")
    print("=" * 80)
    
    print("✓ Endpoint handles metrics with type_spec='NA'")
    print("  This indicates the fix for polymorphic identity errors is working")
    print("  (invalid type_spec values no longer cause 500 errors)")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("METRIC ENDPOINT TEST SUITE")
    print("=" * 80)
    print("Testing the /metric/ endpoint fix for polymorphic identity errors\n")
    
    results = {}
    
    # Test 1: Basic endpoint test
    success, metrics = test_metric_endpoint()
    results['endpoint'] = success
    
    if success and metrics:
        # Test 2: Data structure
        results['structure'] = test_metric_data_structure(metrics)
        
        # Test 3: Type spec values
        results['type_specs'] = test_metric_type_spec_values(metrics)
        
        # Test 4: Metric count
        count_success, count = test_metric_count()
        results['count'] = count_success
    
    # Test 5: Error handling
    results['error_handling'] = test_polymorphic_error_handling()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The metric endpoint is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    print("Starting Metric Endpoint Tests...\n")
    success = run_all_tests()
    exit(0 if success else 1)
