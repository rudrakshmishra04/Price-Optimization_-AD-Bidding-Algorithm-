# Price-Optimization--For-AD-bidding-

## GOAL: 
To optimize keyword bid price (KWs) based on the information given, which includes information from Google Ads' Search campaigns. 


## Data:

Inventory_Historical – contains the trailing 120 day average inventory by Mk/Mo/Yr
Inventory_Current_Onsite – contains the current number of the vehicles on our site by make, model and year (e.g., 205 2013 Honda Accords, 150 2015 Toyota Camrys, etc)
KW_Attributes – contains KW, KW ID, Ad Group, Campaign, Match Type, Quality Score, Est First Pos. Bid, Est Top of Page Bid
KW_Performance_L120D – contains historical KW performance (impressions, clicks, cost, conversions) for prior 120 days by KW ID
Make_Model_ARS – contains the historical average ARS for each make/model

## Bidding logic:

### Step 1: Calculate initial bid for each KW based on its historical performance
  a) If KW has >10 conversions
  Calculate KW bid based on KW’s historical performance
  New KW Bid = KW CVR * Mk/Mo ARS
  b) If KW has <11 conversions but ad group has >10 conversions
  Calculate KW bid based on its ad group’s historical performance
  New KW Bid = AG CVR * Mk/Mo ARS
  c) If AG has <11 conversions, but Mk/Mo/Yr has >10 conversions
  Calculate KW bid based on the Mk/Mo’s historical performance
  New KW bid = Mk/Mo/Yr CVR * Mk/Mo ARS
  d) If Mk/Mo/Yr has <11 conversions, but Mk/Mo has >10 conversions
  Calculate KW bid based on the Mk/Mo’s historical performance
  New KW bid = Mk/Mo CVR * Mk/Mo ARS
  e) If Mk/Mo has <11 conversions
  New KW bid = Est First Pos Bid
  Hint: aggregate KW data to level needed to get AG, Mk/Mo/Yr, Mk/Mo and Mkt level data
  Hint: several attributes (e.g., Mkt, Mk/Mo, etc) will need to be extracted from CMPN and AG names
 

### Step 2: Adjust calculated bid based on the following considerations:
a) Adjust bid based on current onsite inventory
If current Mk/Mo/Yr inv < hist Mk/Mo/Yr inv
Reduce KW bid by % equal to half the % diff between current and historical inv
E.g., if hist avg is 20 and current inv is 15, reduce bid by 12.5% (i.e., half of 25%)
b) Adjust bid based on Mkt CVR only for KWs whose bids were calculated based on Mk/Mo/Yr or Mk/Mo CVR (i.e., not based on KW or AG CVR)
Increase/decrease KW bid by the half the % above or below overall site CVR the market CVR is relative to overall site average
i.e., if overall CVR for the entire site is 1.0% and DAL overall CVR is 1.07%, increase bids for KWs in DAL by 3.5%
c) Cap bids at reasonable levels, based on their quality score
KWs with QS>7 cannot be higher than Est First Pos Bid
KWs with QS<8 and QS>5 cannot be higher than average of Est Top of Page Bid and Est First Pos Bid
KWs with QS<6 cannot be higher than (Est Top of Page Bid *0.9) + (Est First Pos Bid *0.1)
No bids can be higher than $12
d) Cap bids of broad match KWs
Ensure that no bid for a broad match KW is greater than any bid for an exact match KW within the same ad group
E.g., if bids for exact match KWs within the same ad group are $1.50, $1.75 and $1.60, then if a broad match KW with a calculated of bid of $2.00 should have its bid reduced to $1.50

## Definitions:

KW = keyword
AG = ad group
CMPN = campaign
o   Campaigns target geographical areas where users are located (e.g., a campaign could target all people physically located in Dallas)
o   CMPNs contain multiple AGs; AGs contain multiple KWs (learn more here)
QS = quality score = value google assigns to each KW based (learn more here)
Impressions = # of times a KW’s ad was seen on in google search results
Clicks = # of times the KW’s ads were clicked (i.e., # of times people clicked through)
Conversions = # of car sales generated from the clicks
CTR = click through rate = clicks / impressions
CVR = conversion rate = conversions / clicks
ARS = average revenue per sale = amount of money made per item sold
o   This is specific to each make and model, but not by year

Est First Pos. Bid = Google’s estimate for the bid required to show up in first position (see below)
Est Top of Page Bid = Google’s estimate for the bid required to show up at the top of the page (i.e., 4th position)
Mkt = Market = the geography the campaign is targeting
o   ATL = Atlanta

o   DAL = Dallas

o   NYC = New York City

o   CHI = Chicago

o   SFO = San Francisco

Mk/Mo/Yr = combination of make, model and year
