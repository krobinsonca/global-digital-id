#!/usr/bin/env python3
"""
Export Script for Global Digital ID Repository
Exports data.json to CSV, PDF report, and JSON summary formats.
"""

import json
import csv
import sys
from datetime import datetime

def load_data(filepath):
    """Load JSON data"""
    with open(filepath, 'r') as f:
        return json.load(f)

def export_to_csv(data, output_path):
    """Export jurisdictions to CSV"""
    jurisdictions = data.get('jurisdictions', [])

    # Define CSV columns
    fieldnames = [
        'name', 'flag', 'region', 'status', 'issuanceModel', 'isSubnational',
        'url', 'technology', 'credentialType', 'walletType', 'credentialFormat',
        'description', 'issuedCredentialTypes', 'issuingAuthorities', 'acceptedCredentials'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for jur in jurisdictions:
            row = jur.copy()
            # Convert lists/dicts to JSON strings for CSV
            if 'issuedCredentialTypes' in row and isinstance(row['issuedCredentialTypes'], list):
                row['issuedCredentialTypes'] = '; '.join(row['issuedCredentialTypes'])
            if 'issuingAuthorities' in row and isinstance(row['issuingAuthorities'], list):
                row['issuingAuthorities'] = '; '.join([a['name'] for a in row['issuingAuthorities']])
            if 'acceptedCredentials' in row and isinstance(row['acceptedCredentials'], dict):
                row['acceptedCredentials'] = '; '.join(row['acceptedCredentials'].keys())
            writer.writerow(row)

    return len(jurisdictions)

def export_summary_json(data, output_path):
    """Export summary statistics to JSON"""
    jurisdictions = data.get('jurisdictions', [])

    summary = {
        'exportDate': datetime.now().isoformat(),
        'meta': data.get('meta', {}),
        'stats': {
            'totalJurisdictions': len(jurisdictions),
            'byStatus': {},
            'byRegion': {},
            'byIssuanceModel': {},
            'withMultiCredential': 0
        },
        'multiCredentialAnalysis': {
            'jurisdictionsWithIssuingAuthorities': [],
            'jurisdictionsWithAcceptedCredentials': [],
            'commonCredentialTypes': {},
            'commonUseCases': {}
        }
    }

    # Count by status, region, model
    for jur in jurisdictions:
        # Status
        status = jur.get('status', 'unknown')
        summary['stats']['byStatus'][status] = summary['stats']['byStatus'].get(status, 0) + 1

        # Region
        region = jur.get('region', 'unknown')
        summary['stats']['byRegion'][region] = summary['stats']['byRegion'].get(region, 0) + 1

        # Issuance model
        model = jur.get('issuanceModel', 'unknown')
        summary['stats']['byIssuanceModel'][model] = summary['stats']['byIssuanceModel'].get(model, 0) + 1

        # Multi-credential tracking
        if jur.get('issuingAuthorities') or jur.get('acceptedCredentials'):
            summary['stats']['withMultiCredential'] += 1

        if jur.get('issuingAuthorities'):
            summary['multiCredentialAnalysis']['jurisdictionsWithIssuingAuthorities'].append(jur['name'])

        if jur.get('acceptedCredentials'):
            summary['multiCredentialAnalysis']['jurisdictionsWithAcceptedCredentials'].append(jur['name'])

            # Track use cases
            for use_case in jur['acceptedCredentials'].keys():
                summary['multiCredentialAnalysis']['commonUseCases'][use_case] =                     summary['multiCredentialAnalysis']['commonUseCases'].get(use_case, 0) + 1

        # Track credential types
        if jur.get('issuedCredentialTypes'):
            for ct in jur['issuedCredentialTypes']:
                summary['multiCredentialAnalysis']['commonCredentialTypes'][ct] =                     summary['multiCredentialAnalysis']['commonCredentialTypes'].get(ct, 0) + 1

    # Sort by count
    summary['multiCredentialAnalysis']['commonCredentialTypes'] = dict(
        sorted(summary['multiCredentialAnalysis']['commonCredentialTypes'].items(), 
               key=lambda x: x[1], reverse=True)
    )
    summary['multiCredentialAnalysis']['commonUseCases'] = dict(
        sorted(summary['multiCredentialAnalysis']['commonUseCases'].items(), 
               key=lambda x: x[1], reverse=True)
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    return summary

def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else 'data.json'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'

    print(f"📊 Exporting data from {data_path}...")
    print(f"📁 Output directory: {output_dir}")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    # Load data
    data = load_data(data_path)

    # Export to CSV
    csv_path = f"{output_dir}/export_jurisdictions.csv"
    csv_count = export_to_csv(data, csv_path)
    print(f"✓ Exported {csv_count} jurisdictions to CSV: {csv_path}")

    # Export summary JSON
    summary_path = f"{output_dir}/export_summary.json"
    summary = export_summary_json(data, summary_path)
    print(f"✓ Exported summary to JSON: {summary_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 EXPORT SUMMARY")
    print("=" * 60)
    print(f"Total Jurisdictions: {summary['stats']['totalJurisdictions']}")
    print(f"With Multi-Credential Data: {summary['stats']['withMultiCredential']}")
    print(f"\nBy Status:")
    for status, count in summary['stats']['byStatus'].items():
        print(f"  • {status}: {count}")
    print(f"\nBy Region:")
    for region, count in summary['stats']['byRegion'].items():
        print(f"  • {region}: {count}")
    print(f"\nTop Credential Types:")
    for ct, count in list(summary['multiCredentialAnalysis']['commonCredentialTypes'].items())[:5]:
        print(f"  • {ct}: {count} jurisdictions")
    print(f"\nTop Use Cases:")
    for uc, count in list(summary['multiCredentialAnalysis']['commonUseCases'].items())[:5]:
        print(f"  • {uc}: {count} jurisdictions")

    print("\n✅ Export complete!")

if __name__ == "__main__":
    main()
