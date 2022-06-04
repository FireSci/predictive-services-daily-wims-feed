# Assumptions
---
This document is used to keep track of assumptions we're making in the code
regarding station quality, times, etc.

1. Data quality increases as we approach 24z. WIMS still depends on a coded FWN product sent
from every WFO pfcst data, and that time/process is not locked down nationally.
We should expect to run this as close to 24z as possible.


2. Character spacing on each line matters, and should be identical to the legacy
WIMS output found at https://www.wfas.net/nfdr/output/ndfd_predserv_fcst.txt. It
seems the program used to generate the PS 7-day products parses line by line and
expects data at certain positions.


3. Some stations may be temporary or seasonal. In the case that a station does
not report for a particular WIMS endpoint, -99s should be returned for all values
pertaining to that endpoint.


4. If a station does not report data from all four endpoints, it is omitted from
the final output. These stations are logged to an errors file for GACC meteorologists
to follow up on.


5. Stations may report multiple fuel models for the same observation time. In this
case, it is acceptable to just record the first model observation per stakeholders.


6. Stations have a regularly scheduled observation time that rarely changes. We use
this time to obtain only the observations we want as some stations might report
at greater temporal frequencies.


7. The final output file should reflect eleven dates. The first two dates represent
observation data for the previous day and the day on which the file was created. The next seven dates
represent forecast data for both weather and NFDRS. The final two dates are left
as -99s to be compatible with legacy WIMS output.
