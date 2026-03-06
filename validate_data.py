#!/usr/bin/env python3
"""
Data Validation Script for Global Digital ID Repository
Validates data.json structure, required fields, and data integrity.
Run as part of CI/CD pipeline on every commit.
"""

import json
import sys
from datetime import datetime

# Required fields for each jurisdiction
REQUIRED_FIELDS = [
    "name", "flag", "region", "status", "issuanceModel",
    "url", "technology", "description", "details", "nodevice", "metrics"
]

# Optional but recommended fields
RECOMMENDED_FIELDS = [
    "credentialType", "walletType", "credentialFormat", "walletTech",
    "issuedCredentialTypes", "issuingAuthorities", "acceptedCredentials"
]

# Valid values for certain fields
VALID_REGIONS = ["eu", "na", "apac", "me", "af", "africa", "sa", "global"]
VALID_STATUSES = ["production", "development", "planned", "discontinued"]
VALID_ISSUANCE_MODELS = ["wallet", "single", "multi", "platform", "cloud", "multiple"]

def load_data(filepath):
    """Load and parse JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        return None
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None

def validate_structure(data):
    """Validate top-level structure"""
    errors = []
    required_keys = ["meta", "stats", "jurisdictions"]

    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required top-level key: {key}")

    return errors

def validate_jurisdictions(jurisdictions):
    """Validate each jurisdiction entry"""
    errors = []
    warnings = []

    for i, jur in enumerate(jurisdictions):
        prefix = f"Jurisdiction {i+1} ({jur.get('name', 'UNKNOWN')})"

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in jur:
                errors.append(f"{prefix}: Missing required field '{field}'")

        # Check recommended fields
        for field in RECOMMENDED_FIELDS:
            if field not in jur:
                warnings.append(f"{prefix}: Missing recommended field '{field}'")

        # Validate region
        if "region" in jur and jur["region"] not in VALID_REGIONS:
            errors.append(f"{prefix}: Invalid region '{jur['region']}'. Valid: {VALID_REGIONS}")

        # Validate status
        if "status" in jur and jur["status"] not in VALID_STATUSES:
            errors.append(f"{prefix}: Invalid status '{jur['status']}'. Valid: {VALID_STATUSES}")

        # Validate issuance model
        if "issuanceModel" in jur and jur["issuanceModel"] not in VALID_ISSUANCE_MODELS:
            errors.append(f"{prefix}: Invalid issuanceModel '{jur['issuanceModel']}'. Valid: {VALID_ISSUANCE_MODELS}")

        # Validate URL format
        if "url" in jur and jur["url"]:
            if not jur["url"].startswith("http://") and not jur["url"].startswith("https://"):
                errors.append(f"{prefix}: URL must start with http:// or https://")

        # Validate multi-credential data structure if present
        if "issuingAuthorities" in jur:
            for j, auth in enumerate(jur["issuingAuthorities"]):
                if "name" not in auth:
                    errors.append(f"{prefix}: issuingAuthorities[{j}] missing 'name'")
                if "credentials" not in auth or not isinstance(auth["credentials"], list):
                    errors.append(f"{prefix}: issuingAuthorities[{j}] 'credentials' must be a list")

        if "acceptedCredentials" in jur:
            if not isinstance(jur["acceptedCredentials"], dict):
                errors.append(f"{prefix}: acceptedCredentials must be an object")
            else:
                for use_case, data in jur["acceptedCredentials"].items():
                    if "agency" not in data:
                        errors.append(f"{prefix}: acceptedCredentials['{use_case}'] missing 'agency'")
                    if "acceptedTypes" not in data or not isinstance(data["acceptedTypes"], list):
                        errors.append(f"{prefix}: acceptedCredentials['{use_case}'] 'acceptedTypes' must be a list")

    return errors, warnings

def validate_stats(data):
    """Validate stats consistency"""
    warnings = []

    if "jurisdictions" in data and "stats" in data:
        actual_count = len(data["jurisdictions"])
        # Stats are displayed as strings like "20+", so we can't directly compare
        # But we can check if the format is reasonable
        if "countries" in data["stats"]:
            if not any(c.isdigit() for c in data["stats"]["countries"]):
                warnings.append(f"Stats 'countries' value '{data['stats']['countries']}' doesn't contain digits")

    return warnings

def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "data.json"

    print(f"🔍 Validating {filepath}...")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    # Load data
    data = load_data(filepath)
    if data is None:
        print("\n❌ VALIDATION FAILED: Could not load data")
        sys.exit(1)

    all_errors = []
    all_warnings = []

    # Validate structure
    errors = validate_structure(data)
    all_errors.extend(errors)

    # Validate jurisdictions
    if "jurisdictions" in data:
        errors, warnings = validate_jurisdictions(data["jurisdictions"])
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    else:
        all_errors.append("No jurisdictions found")

    # Validate stats
    warnings = validate_stats(data)
    all_warnings.extend(warnings)

    # Print results
    print(f"\n📊 Results:")
    print(f"   Total jurisdictions: {len(data.get('jurisdictions', []))}")
    print(f"   Errors: {len(all_errors)}")
    print(f"   Warnings: {len(all_warnings)}")

    if all_errors:
        print("\n❌ ERRORS:")
        for error in all_errors:
            print(f"   • {error}")

    if all_warnings:
        print("\n⚠️  WARNINGS:")
        for warning in all_warnings:
            print(f"   • {warning}")

    print("\n" + "=" * 60)

    if all_errors:
        print("❌ VALIDATION FAILED")
        sys.exit(1)
    else:
        print("✅ VALIDATION PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()
