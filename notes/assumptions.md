# Assumptions
---
This document is used to keep track of assumptions we're making in the code
regarding station quality, times, etc.

1. Data quality increases as we approach 24z. This is because station observations
need to be input by hand. Further, WIMS still depends on a coded FWN product sent
from every WFO pfcst data, and that time/process is not locked down nationally.
We should expect to run this as close to 24z as possible.

2. Character spacing on each line matters, and should be identical to the legacy
WIMS output found at https://www.wfas.net/nfdr/output/ndfd_predserv_fcst.txt. It
seems the program used to generate the PS 7-day products parses line by line and
expects data at certain positions.
