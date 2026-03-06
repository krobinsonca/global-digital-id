# 🌐 Global Digital ID Landscape

Interactive visualization of digital ID systems worldwide for the **BC Government Digital Trust Initiative**.

![Preview](preview.png)

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| **Jurisdictions Tracked** | 50+ |
| **Countries** | 20+ |
| **Subnational Regions** | 30+ (US states, Canadian provinces, Australian states) |
| **Users Covered** | 1.4B+ |
| **Multi-Credential Analysis** | 100% of jurisdictions |

---

## ✨ Features

### Core Features
- **Comprehensive Coverage**: 50+ jurisdictions across 6 regions
- **Real-time Filters**: Status (Live/Dev), Region, Wallet Type, Credential Format
- **Deep Details**: Technology specs, metrics, no-device solutions
- **Verified URLs**: All jurisdiction links tested and working
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme**: Toggle for user preference

### 🆕 New Features (2026)

#### Multi-Credential Tracking
Every jurisdiction now includes:
- **Issued Credential Types**: What credentials the jurisdiction issues
- **Issuing Authorities**: Which agencies/authorities issue each credential
- **Accepted Credentials**: Where multiple credential types are accepted as proof

#### Example Use Cases Tracked:
| Use Case | Agency/Authority | Accepted Credential Types |
|----------|-----------------|--------------------------|
| TSA Airport Security | TSA (USA) | mDL, Physical DL, Passport, Passport Card, Global Entry |
| Government Services | Various | eID, Digital ID, Physical ID, Bank ID |
| Healthcare | Health Ministries | Health Card, eID, National ID |
| Banking | Financial Regulators | National ID, eID, Bank ID, Passport |
| Age Verification | Retailers / Licensing | Driver License, ID Card, Passport |

#### Export Functionality
- **CSV Export**: All jurisdiction data for spreadsheet analysis
- **JSON Summary**: Statistics and multi-credential analysis
- **On-demand**: Run `python3 export_data.py` anytime

#### CI/CD Validation
- **Automated Validation**: Every commit validates data.json structure
- **Schema Enforcement**: Required fields, valid values, data types
- **GitHub Actions**: Runs on pull requests and pushes to main

---

## 🚀 Quick Start

### Option 1: GitHub Pages (Recommended)

The site is hosted at: **https://krobinsonca.github.io/global-digital-id/**

### Option 2: Local Development

```bash
# Clone the repo
git clone https://github.com/krobinsonca/global-digital-id.git
cd global-digital-id

# Start a local server (required for fetch to work)
python3 -m http.server 8080

# Open in browser
open http://localhost:8080
```

Or use any static server:

```bash
# Node.js
npx serve .

# PHP
php -S localhost:8080
```

---

## 📁 Data Structure

All data lives in `data.json`. Here's the complete schema:

### Top-Level Structure

```json
{
  "meta": {
    "title": "Global Digital ID Landscape",
    "description": "Jurisdictional scan of digital ID systems worldwide",
    "lastUpdated": "2026-03-02",
    "preparedFor": "BC Government Digital Trust Initiative"
  },
  "stats": {
    "countries": "20+",
    "users": "1.4B",
    "subnationals": "30+",
    "euDeadline": "2026"
  },
  "jurisdictions": [...],
  "nodeviceSolutions": [...],
  "techCategories": [...],
  "interoperability": {...}
}
```

### Jurisdiction Schema

```json
{
  "name": "Country/Region Name",
  "flag": "iso-country-code",
  "region": "eu|na|apac|me|af|sa|global",
  "status": "production|development|planned|discontinued",
  "issuanceModel": "wallet|single|multi|platform|cloud|multiple",
  "isSubnational": false,
  "parent": "Parent Country (if subnational)",
  "url": "https://official-website.gov",
  "technology": "Primary technology description",
  "techStack": ["PKI", "Biometric", "OIDC", "ISO 18013-5"],
  "credentialType": "Type of credential issued",
  "description": "Brief description",
  "details": ["Detail 1", "Detail 2"],
  "nodevice": ["Physical ID", "OTP Fallback"],
  "metrics": [{"label": "Users", "value": "10M"}],
  "walletType": "Government|Platform|Private",
  "credentialFormat": "mDL|Verifiable Credentials|Proprietary",
  "walletTech": "Technology stack",

  // NEW: Multi-Credential Fields
  "issuedCredentialTypes": ["mDL", "eID", "Health Card"],
  "issuingAuthorities": [
    {
      "name": "Agency Name",
      "type": "National|State|Private",
      "credentials": ["Credential 1", "Credential 2"]
    }
  ],
  "acceptedCredentials": {
    "Use Case Name": {
      "agency": "Accepting Agency",
      "acceptedTypes": ["Type 1", "Type 2"]
    }
  }
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Jurisdiction name |
| `flag` | string | ✅ | ISO country code (fi, us, ca, etc.) |
| `region` | string | ✅ | eu, na, apac, me, af, sa, global |
| `status` | string | ✅ | production, development, planned, discontinued |
| `issuanceModel` | string | ✅ | wallet, single, multi, platform, cloud, multiple |
| `isSubnational` | boolean | ✅ | true for states/provinces |
| `url` | string | ✅ | Official website URL |
| `technology` | string | ✅ | Primary technology description |
| `description` | string | ✅ | Brief overview |
| `details` | array | ✅ | List of key details |
| `nodevice` | array | ✅ | No-device verification options |
| `metrics` | array | ✅ | Statistics with label/value pairs |
| `issuedCredentialTypes` | array | 🟡 | Types of credentials issued |
| `issuingAuthorities` | array | 🟡 | Agencies that issue credentials |
| `acceptedCredentials` | object | 🟡 | Use cases with accepted credential types |

🟡 = Recommended for comprehensive multi-credential tracking

---

## 🛠️ Tools & Scripts

### Data Validation

Validate data.json structure before committing:

```bash
python3 validate_data.py data.json
```

This checks:
- Required fields present
- Valid region/status/issuanceModel values
- Proper data types
- Multi-credential data structure

### Data Export

Export data to CSV and summary JSON:

```bash
python3 export_data.py data.json ./output/
```

Outputs:
- `export_jurisdictions.csv` - All jurisdictions in spreadsheet format
- `export_summary.json` - Statistics and multi-credential analysis

---

## 🤝 Contributing

### Adding a New Jurisdiction

1. **Research**: Gather official information from government sources
2. **Edit data.json**: Add new entry following the schema above
3. **Validate**: Run `python3 validate_data.py data.json`
4. **Test**: Run locally and verify display
5. **Submit**: Create pull request

### Updating Existing Data

1. **Find jurisdiction** in data.json
2. **Update fields** as needed
3. **Add multi-credential data** if missing:
   - `issuedCredentialTypes`: What they issue
   - `issuingAuthorities`: Who issues them
   - `acceptedCredentials`: Where they're accepted
4. **Validate and test**

### Data Sources

When adding/updating data, cite sources:
- Official government websites
- Legislation/regulations
- Press releases
- Verified news articles

Add source URLs to the jurisdiction's `details` array:
```json
"details": [
  "Launched 2024",
  "Source: https://gov.example.gov/digital-id-announcement"
]
```

---

## 📋 Methodology

### Data Collection

1. **Primary Sources**: Official government websites and documentation
2. **Verification**: Cross-reference multiple sources when possible
3. **Updates**: Reviewed quarterly or when major changes announced
4. **Community Input**: Contributions from practitioners and experts

### Multi-Credential Analysis

Jurisdictions are analyzed for:
- **Credential Diversity**: Number and types of credentials issued
- **Authority Distribution**: Centralized vs. distributed issuance
- **Acceptance Breadth**: Number of use cases accepting multiple types
- **Interoperability**: Cross-border and cross-sector acceptance

### Status Definitions

| Status | Description |
|--------|-------------|
| **Production** | Live and available to citizens |
| **Development** | Active development, pilot, or limited rollout |
| **Planned** | Announced but not yet in development |
| **Discontinued** | Deprecated or replaced |

---

## 📁 Project Structure

```
global-digital-id/
├── index.html              # Main visualization UI
├── summary.html            # Executive summary view
├── presentation.html       # Presentation mode
├── data.json               # All jurisdiction data
├── README.md               # This file
├── validate_data.py        # Data validation script
├── export_data.py          # Export to CSV/JSON
├── server.js               # Optional Node.js server
├── .github/
│   └── workflows/
│       ├── deploy.yml      # GitHub Pages deployment
│       └── validate.yml    # CI/CD data validation
└── preview.png             # Screenshot for README
```

---

## 🔧 CI/CD Pipeline

### Automated Workflows

| Workflow | Trigger | Purpose |
|----------|---------|----------|
| **Deploy** | Push to main | Deploy to GitHub Pages |
| **Validate** | PR or push (data.json) | Validate data structure |

### Validation Rules

- ✅ JSON syntax valid
- ✅ All required fields present
- ✅ Valid enum values (region, status, issuanceModel)
- ✅ URLs start with http:// or https://
- ✅ Multi-credential data properly structured

---

## 📊 Export Analysis

Based on current data (50 jurisdictions):

### By Status
- **Production**: 32 jurisdictions (64%)
- **Development**: 18 jurisdictions (36%)

### By Region
- **North America**: 22 jurisdictions (44%)
- **Europe**: 11 jurisdictions (22%)
- **Asia-Pacific**: 10 jurisdictions (20%)
- **Middle East**: 5 jurisdictions (10%)
- **Africa**: 2 jurisdictions (4%)

### Top Credential Types
1. Physical Driver License (19 jurisdictions)
2. Passport (15 jurisdictions)
3. Driver License (15 jurisdictions)
4. mDL (15 jurisdictions)
5. State ID (14 jurisdictions)

### Top Use Cases
1. Government Services (40 jurisdictions)
2. Age Verification (30 jurisdictions)
3. Healthcare (18 jurisdictions)
4. Banking (17 jurisdictions)
5. Travel (15 jurisdictions)

---

## 📞 Contact

**Prepared for**: BC Government Digital Trust Initiative  
**Last Updated**: 2026-03-02  
**Repository**: https://github.com/krobinsonca/global-digital-id  
**Live Site**: https://krobinsonca.github.io/global-digital-id/

---

## 📄 License

This project is maintained for the BC Government Digital Trust Initiative.  
Data may be used for research, policy development, and digital ID planning purposes.
