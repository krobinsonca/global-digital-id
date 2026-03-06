# Changelog

All notable changes to the Global Digital ID Landscape project.

## [2026-03-06] - Major Enhancement Release

### 🎉 Added

#### Multi-Credential Tracking (100% Coverage)
- Added `issuedCredentialTypes` field to all 50 jurisdictions
- Added `issuingAuthorities` field with agency details
- Added `acceptedCredentials` field tracking use cases by agency
- Updated UI to display issuing authorities and accepted credentials

#### New Jurisdictions with Multi-Credential Data
- **EU**: Finland, Italy, Spain, France, Netherlands, Portugal, Sweden, Germany
- **North America**: All US states (CA, AZ, CO, LA, MD, GA, OH, UT, NY, IA, VA, NV, VT, NJ, TX) and Canadian provinces (BC, QC, AB, ON, MB, SK)
- **Asia-Pacific**: Australia, China, India, Singapore, South Korea, Taiwan, Malaysia, NSW, Victoria
- **Middle East**: Israel, UAE, Oman, Qatar, Saudi Arabia
- **Africa**: Nigeria, Kenya
- **Other**: Brazil, Estonia, UK

#### CI/CD & Automation
- Created `validate_data.py` for data structure validation
- Added GitHub Actions workflow for automated validation on PR/push
- Created `export_data.py` for CSV and JSON export
- Added export summary with multi-credential analysis

#### Documentation
- Comprehensive README rewrite with full schema documentation
- Added methodology section
- Added contribution guidelines
- Added field reference table
- Created CHANGELOG

### 🔧 Changed

- Updated validation script to accept existing region/issuanceModel values
- Enhanced modal UI with new sections for authorities and acceptance
- Improved export with statistics and analysis

### 📊 Statistics

| Metric | Before | After |
|--------|--------|-------|
| Jurisdictions | 50 | 50 |
| With Multi-Credential Data | 0 (0%) | 50 (100%) |
| Validation Scripts | 0 | 1 |
| Export Scripts | 0 | 1 |
| GitHub Workflows | 1 | 2 |
| README Size | 2.1KB | 12KB |

### 🎯 Key Use Cases Tracked

| Use Case | Jurisdictions |
|----------|---------------|
| Government Services | 40 |
| Age Verification | 30 |
| Healthcare | 18 |
| Banking | 17 |
| Travel | 15 |

---

## [2026-03-02] - Previous Version

- 50 jurisdictions tracked
- Basic credential type tracking
- GitHub Pages deployment
- Interactive filtering

---

## Future Enhancements (Planned)

- [ ] Interactive world map visualization
- [ ] Side-by-side jurisdiction comparison tool
- [ ] Historical timeline data
- [ ] API endpoint for programmatic access
- [ ] RSS/Newsletter for updates
- [ ] Accessibility improvements (WCAG 2.1)
- [ ] Additional Latin America coverage
- [ ] More African jurisdictions
