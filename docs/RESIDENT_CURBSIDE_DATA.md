# Public resident-suggested curbside charging locations

Collected November 18, 2026 from NYC DOT's public suggestion map:
https://nycdotprojects.info/project-feedback-map/where-should-dot-install-curbside-l2-ev-chargers-next

These are resident suggestions, not DOT-approved or construction-verified sites.
The source snapshot has 631 public records grouped into 544 suggested locations.
Visible feedback: 558 Wanted, 9 Not Wanted, 64 In Review. All records have original
public pin coordinates; 629 have street descriptions and 2 have missing descriptions.
No resident names or comment bodies are included.

## Files

- `data/NYC_Curbside_Resident_Suggestions.xlsx`: readable workbook with Locations and
  Records sheets, feedback counts, dates and source links.
- `data/reference/public_resident_suggestions_records.csv`: 631 individual records.
- `data/reference/public_resident_suggestions_locations.csv`: 544 location groups.
- `data/reference/public_collection_summary.json`: collection coverage and grouping rules.
- `data/resident_curbside_candidates_2026-11-18.csv`: all 544 groups, with explicit
  `candidate_eligible` and `exclusion_reason` fields. Filter `candidate_eligible = true`
  to obtain the 487 research candidates. Do not treat all rows as eligible.
- `data/reference/resident_candidates_screening_metadata.json`: screening controls,
  source links and hashes. Scenario site caps are separate from data eligibility.
- `data/reference/nyc_borough_boundaries_2026-11-18.geojson`: official borough geometry
  used for the initial administrative-boundary screen.

## Preparation and limitations

Location groups share coordinates rounded to six decimal places, or have identical
normalized street descriptions within 25 metres of a representative original pin.
No fuzzy street-name matching is performed. Original coordinates are retained,
not averaged, snapped to tracts or replaced by invented geocodes.

Eligibility requires at least one published Wanted record, a pin inside an official
NYC borough land polygon, and no explicit trailing-borough label that conflicts with
the pin's borough. This excludes 56 groups with no published support and 1 outside
the land boundary. The complete source snapshots remain available for review.

Boundary source:
https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne

This screen does not establish curb availability, electrical feasibility, right of
way, road or bridge access, or permission to install. Some pins may still be inaccurate.
Feedback counts are not EV registration counts or kWh demand and should not replace
the existing demand calculation.

## Selected modeling direction

The group selected parking plus curbside investment, fixed 0.5-mile radius, a $15M
installation budget and at most 150 curbside projects. The existing cost assumption
of $25,000/curbside port (four ports/site, $100,000/site) is not a DOT quotation and
requires independent cost evidence or sensitivity analysis.

This data-only addition does not change the repository's solver, configuration or
checked-in reference results. The existing `tract_curbside_case.json` still generates
tract-center candidates until the resident-location loader/configuration is integrated.
