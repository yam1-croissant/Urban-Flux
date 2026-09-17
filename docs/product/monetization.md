# UrbanFlux — Business Model & Monetization Strategy

## 1. Executive Summary

UrbanFlux operates a **B2G (Business-to-Government) and B2B SaaS licensing model**, complemented by API-based infrastructure simulation services for engineering consultancies and construction contractors.

---

## 2. Tiered Subscription & Pricing Architecture

```text
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│     CIVIC / EXPLORER    │     │      PLANNER / PRO      │     │    ENTERPRISE / SMART   │
│         (Community)     │     │     (Engineering & Planners)   │     (Municipal & Transit)    │
│                         │     │                         │     │                         │
│ • Public OSM Maps       │     │ • Private Network Data  │     │ • Full Citywide Digital │
│ • 5 Preset Scenarios    │     │ • Unlimited Scenarios   │     │   Twin Deployment       │
│ • Standard BPR Model    │     │ • Custom OD Matrices    │     │ • Real-Time Sensor Feeds│
│ • Free / Open Source    │     │ • PDF Diversion Reports │     │ • Direct CAD/GIS APIs   │
│                         │     │ • \$1,500 / seat / mo   │     │ • \$50k–\$250k / year   │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

---

## 3. Detailed Tier Breakdown

### Tier 1: Civic / Community Edition (Free / Open Tier)
- **Target**: Academic researchers, civic advocacy groups, open-source contributors.
- **Features**:
  - Pre-loaded open Bengaluru arterial network (from OSM).
  - Up to 5 pre-configured demo disruption scenarios (e.g., Silk Board bridge closure, Hebbal flyover flooding).
  - Standard Bureau of Public Roads (BPR) calculations.
- **Strategic Purpose**: Establishes brand awareness, community trust, and organic adoption among urban planning students and researchers.

---

### Tier 2: Planner Pro (B2B SaaS for Consultancies & Contractors)
- **Target**: Civil engineering contractors (L&T, Afcons, Shapoorji Pallonji), traffic engineering consultancies (WSP, AECOM, Atkins), event logistics planners.
- **Features**:
  - Upload proprietary road network geometry, local lane counts, and custom OD demand matrices.
  - Unlimited scenario creation and iterative "what-if" disruption comparisons.
  - Automated generation of **Certified Traffic Diversion Impact Reports** formatted for municipal regulatory submission.
  - Export simulation metrics (link travel times, delay curves, V/C heatmaps) in GeoJSON / CSV formats.
- **Pricing Model**: Seat-based subscription (\$1,500 – \$3,000 / seat / month) or Project-Based Licensing (\$10,000 / construction package).

---

### Tier 3: Enterprise & Municipal Smart City Deployment (B2G Annual License)
- **Target**: Municipal Corporations (BBMP), Urban Development Authorities (BDA, BMRDA), Smart City Control Centers, Traffic Police Command Centers (BTP).
- **Features**:
  - Full-scale digital twin of the metropolitan road network (10,000+ directed links).
  - Automated integration with live municipal sensor feeds (traffic camera vehicle counts, TomTom/Google speed telemetry, weather radar).
  - Multi-agency access control (Traffic Police, Emergency Services, City Engineers).
  - Dedicated SLA, on-premise or sovereign cloud hosting, custom calibration to local vehicle mix (PCU tuning).
- **Pricing Model**: Annual Municipal License (\$75,000 – \$250,000 / year based on urban population and network size).

---

## 4. Total Addressable Market (TAM) & Scaling Strategy

1. **Serviceable Addressable Market (SAM)**:
   - Top 50 Tier-1 and Tier-2 Indian cities undergoing rapid metro and flyover construction (Smart Cities Mission budget allocations).
   - ~500 infrastructure contractors and engineering consultancies operating in South Asia.
   - Estimated SAM: **\$45M - \$60M annually**.
2. **Go-to-Market (GTM) Phasing**:
   - **Phase 1 (Hackathon & Early Pilot)**: Validate prototype with Bengaluru academic partners (IISc) and local civic mobility groups.
   - **Phase 2 (B2B Construction Beachhead)**: Target metro construction contractors who urgently need fast, defensible Traffic Diversion Plans.
   - **Phase 3 (Municipal Expansion)**: Tender for Smart Cities Mission municipal control room resilience simulation contracts.
