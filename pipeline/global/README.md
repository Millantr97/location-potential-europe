# Global expansion pipeline

Country adapters preserve the product's three evidence classes:

- **OBSERVED**: named streets, shops, amenities, stations and competitors from OpenStreetMap.
- **AREA CONTEXT**: official small-area census statistics. US pages use ACS 2024 5-year census tracts; Australian pages use ABS Census 2021 small-area data.
- **MODELLED**: pedestrian flow, rent, spend and revenue. Modelled values are recalibrated in local currency and never presented as observed.

A city is not published if its commercial street clusters are too thin or the official small-area context cannot be joined reliably.
