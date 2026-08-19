# -*- coding: utf-8 -*-
"""M&W GroundWorks — site content.

Everything factual here comes from the client's own brief (services, company
name, phone) or from verified public sources (Jefferson County towns, Missouri
mowing/clearing seasonality, county permit thresholds). Nothing that would
require verification — licence numbers, insurance carriers, review counts,
years in business, accreditations — is asserted anywhere. Those live in
CLIENT_TODO and render on the page as visible, replaceable placeholders.
"""

BIZ = {
    "name": "M&W GroundWorks",
    "legal": "M&W GroundWorks",
    "tagline": "Clear. Build. Maintain.",
    "descriptor": "Land & Property Services",
    "phone_display": "(314) 634-6630",
    "phone_href": "+13146346630",
    "phone_e164": "+1-314-634-6630",
    "county": "Jefferson County",
    "state": "Missouri",
    "state_abbr": "MO",
    "seat": "Hillsboro",
    "domain": "mwgroundworks.com",
    "url": "https://mwgroundworks.com",
    "hours": "Mon–Sat, 7:00am – 6:00pm",
}

# ---------------------------------------------------------------- services
# family: clear | build | maintain
SERVICES = [
    dict(slug="land-clearing", name="Land Clearing", family="clear",
         icon="trees", short="Lots, acreage and building pads cleared and left ready to work.",
         body="Overgrown parcels, new build sites, pasture reclaim and fence lines. "
              "We take a lot from impassable to usable — brush, saplings, undergrowth "
              "and the debris that comes with it. Jefferson County requires a land "
              "disturbance permit once you pass roughly 5,000 sq ft, disturb an acre, "
              "or cut or fill 5 feet or more; we'll tell you up front which side of "
              "that line your job falls on.",
         bullets=["Residential lots and building pads", "Acreage and pasture reclaim",
                  "Fence lines and property boundaries", "Honeysuckle, multiflora rose and cedar encroachment",
                  "Debris hauled off, not left in a pile"],
         season="Best November–February, when frozen ground carries equipment without rutting."),
    dict(slug="brush-clearing", name="Brush Clearing", family="clear",
         icon="brush", short="Overgrowth, thickets and scrub cut back and hauled out.",
         body="The tight, ugly work — fence rows choked with honeysuckle, creek banks, "
              "treelines creeping into the yard, and the back half of a property nobody "
              "has touched in ten years. Smaller footprint than a full clear, same "
              "finish standard.",
         bullets=["Fence rows and treelines", "Creek and ditch banks",
                  "Poison ivy, locust and hedge", "Overgrown back lots",
                  "Access paths and trails"],
         season="Fall through winter is cleanest — dormant growth, firm ground, fewer ticks."),
    dict(slug="ditch-clearing", name="Ditch Clearing", family="clear",
         icon="water", short="Drainage reopened so water leaves your property, not sits on it.",
         body="Silted-in ditches, blocked culverts and washed-out swales. Jefferson "
              "County's clay soils and rolling Ozark-foothill terrain move a lot of "
              "water fast — a ditch that stopped draining two seasons ago is usually "
              "why the low corner of the yard stays soft.",
         bullets=["Roadside and field ditches", "Culvert inlets and outlets",
                  "Silt and debris removal", "Regrading for fall",
                  "Erosion trouble spots"],
         season="Spring and fall, ahead of the heavy-rain months."),
    dict(slug="retaining-walls", name="Retaining Walls", family="build",
         icon="wall", short="Block and stone walls that hold grade and drain properly.",
         body="Built for the slope you actually have, with the drainage behind it that "
              "keeps it standing. Around St. Louis, walls over 4 feet measured from the "
              "bottom of the footing generally need a permit and an engineer's stamp — "
              "we'll tell you before you're committed, not after.",
         bullets=["Segmental block and natural stone", "Terraced and tiered walls",
                  "Proper base, backfill and drainage", "Grade correction and levelled yards",
                  "Wall repair and rebuild"],
         season="Spring through late fall, before ground freeze."),
    dict(slug="masonry", name="Brick & Masonry Work", family="build",
         icon="brick", short="Brick, block and stone — new work and repairs.",
         body="Piers, columns, steps, mailbox surrounds, fire pits, veneer and repair "
              "work on what's already there. Straight lines, full joints, and mortar "
              "matched to the existing when we're tying into old work.",
         bullets=["Brick, block and natural stone", "Steps, piers and columns",
                  "Fire pits and seating walls", "Tuckpointing and repairs",
                  "Veneer and facing"],
         season="Spring through fall — mortar needs temperatures above freezing."),
    dict(slug="decks", name="Decks & Outdoor Construction", family="build",
         icon="deck", short="Decks, steps, landings and the structures around them.",
         body="New builds and rebuilds — framing, decking, rails, stairs and landings. "
              "Sized and detailed for the grade, which on a lot of Jefferson County "
              "properties means working with a slope rather than pretending it's flat.",
         bullets=["New deck construction", "Rebuilds and board replacement",
                  "Stairs, landings and rails", "Ground-level and elevated",
                  "Grading and site prep included"],
         season="Spring through fall."),
    dict(slug="lawn-care", name="Lawn Care & Yard Management", family="maintain",
         icon="mower", short="Mowing, trimming and edging on a schedule you can forget about.",
         body="Weekly and bi-weekly mowing April through October, with trimming, "
              "edging and blow-off every visit. Cool-season fescue and bluegrass go "
              "semi-dormant in the July–August heat, so the schedule flexes with the "
              "grass instead of billing you for cuts it doesn't need.",
         bullets=["Weekly and bi-weekly mowing", "Trimming, edging and blow-off",
                  "Residential and commercial", "Vacant lots and rentals",
                  "One-time overgrown-lot cuts"],
         season="April to late October. Peak growth April–June."),
    dict(slug="junk-removal", name="Junk Removal", family="maintain",
         icon="truck", short="Hauled off in one trip — yard, garage, outbuilding or lot.",
         body="Storm debris, old fencing, appliances, brush piles, construction leftovers "
              "and the contents of a shed nobody has opened since 2009. Loaded and hauled; "
              "you don't touch it.",
         bullets=["Yard and storm debris", "Garage, shed and outbuilding clean-outs",
                  "Old fencing, decking and lumber", "Appliances and scrap",
                  "Post-construction clean-up"],
         season="Year-round."),
    dict(slug="property-maintenance", name="General Property Maintenance", family="maintain",
         icon="shield", short="One number for keeping the whole property in shape.",
         body="Spring clean-up, leaf removal, mulch, gutter clearing, seasonal knock-downs "
              "and the running list of small things that never quite get done. Set up as "
              "a standing arrangement or call when you need it.",
         bullets=["Spring and fall clean-ups", "Leaf removal, October–November",
                  "Mulch and bed maintenance", "Vacant and rental property upkeep",
                  "Standing seasonal schedules"],
         season="Year-round, with clean-up peaks in spring and October–November."),
]

FAMILIES = {
    "clear": dict(n="01", title="Clear", label="Clear",
                  blurb="Take it back to workable ground. Overgrowth, scrub, "
                        "silted-in drainage and everything in the way of what comes next."),
    "build": dict(n="02", title="Build", label="Build",
                  blurb="Put something permanent in its place — walls that hold grade, "
                        "masonry that lasts, and structures sized for the slope you have."),
    "maintain": dict(n="03", title="Maintain", label="Maintain",
                     blurb="Keep it that way. Mowing on a schedule, seasonal clean-ups, "
                           "and hauling off whatever accumulates."),
}

# ------------------------------------------------------- service area
# Verified incorporated cities/villages and unincorporated communities
# of Jefferson County, Missouri.
TOWNS_KEY = ["Arnold", "Festus", "Hillsboro", "Imperial", "High Ridge",
             "House Springs", "Barnhart", "De Soto", "Cedar Hill", "Pevely",
             "Herculaneum", "Byrnes Mill"]
TOWNS_MORE = ["Crystal City", "Kimmswick", "Antonia", "Dittmer", "Hematite",
              "Mapaville", "Morse Mill", "Otto", "Seckman", "Weber Hill",
              "Maxville", "Victoria", "Goldman", "Valles Mines", "Sulphur Springs",
              "Grubville", "Byrnesville", "Plattin", "Horine", "Olympian Village",
              "Cedar Hill Lakes", "Scotsdale", "Parkdale", "Liguori", "Fletcher"]
TOWNS_EDGE = ["Fenton", "Valley Park", "Eureka", "Pacific", "Bonne Terre",
              "Ste. Genevieve"]

# ------------------------------------------------------------- seasonal
# Missouri / St. Louis-region seasonality. Months are 0-indexed Jan..Dec.
# 2 = peak season, 1 = in season, 0 = off.
CALENDAR = [
    ("Mowing & yard management", [0, 0, 0, 2, 2, 2, 1, 1, 1, 1, 0, 0]),
    ("Land & brush clearing",    [2, 2, 1, 0, 0, 0, 0, 0, 1, 1, 2, 2]),
    ("Walls, masonry & decks",   [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 1, 0]),
    ("Ditch clearing & drainage",[0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 1, 0]),
    ("Leaf & seasonal clean-up", [0, 0, 1, 2, 1, 0, 0, 0, 1, 2, 2, 0]),
    ("Junk removal",             [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]),
]
MONTHS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]

# ------------------------------------------------------------------ FAQ
FAQ = [
    ("Do you charge for an estimate?",
     "No. Estimates are free, and for most jobs we'll come walk the property "
     "rather than guess from the road. If you can send photos of an overgrown "
     "lot, we can often get you a ballpark before we ever drive out."),
    ("How fast can you get out here?",
     "Call or text and we'll get back to you the same day. Scheduling depends "
     "on the season — mowing books up in spring, clearing books up in late fall "
     "— so the earlier you call for seasonal work, the better the slot."),
    ("What areas do you cover?",
     "Jefferson County, Missouri and the immediate edges of it — Arnold, Festus, "
     "Hillsboro, Imperial, High Ridge, House Springs, Barnhart, De Soto, Cedar "
     "Hill, Pevely, Herculaneum, Byrnes Mill and the communities between them. "
     "If you're just outside the county line, ask anyway."),
    ("When is the best time to clear land?",
     "November through February. Frozen or firm ground carries equipment without "
     "rutting or compacting your soil, the vegetation is dormant so there's far "
     "less debris, and with no leaf canopy we can actually see the lot. Fall is "
     "the second-best window. Spring is the worst — it's mud."),
    ("Do I need a permit?",
     "Sometimes. Jefferson County requires a land disturbance permit once you "
     "disturb roughly 5,000 sq ft, exceed an acre, or cut or fill 5 feet or more. "
     "Retaining walls over 4 feet from the bottom of the footing generally need a "
     "permit and an engineer's stamp in this region, and cities within the county "
     "set their own thresholds on top of that. We'll tell you what your job needs "
     "before you commit."),
    ("Do you do commercial and rental properties?",
     "Yes — vacant lots, rentals, small commercial sites and HOA common ground. "
     "Standing schedules available for anything recurring."),
    ("What does mowing season look like in Missouri?",
     "April through late October, roughly. Peak growth is April to June, then "
     "cool-season fescue and bluegrass slow down in the July–August heat. Early "
     "September is the right window for aeration and overseeding, and leaves need "
     "to be off the lawn before snow mold sets in around November."),
    ("How do I get a quote?",
     "Call or text " + BIZ["phone_display"] + ", or fill out the form on the "
     "contact page. Tell us what you need, where you are, and send a photo if "
     "you've got one — a picture of an overgrown lot is worth ten minutes of "
     "description."),
]

PROCESS = [
    ("You call or text", "Tell us what you're looking at. Photos help. "
     "We'll tell you same day whether it's something we do."),
    ("We walk the property", "Free, on site, at a time that works. We look at "
     "access, slope, drainage and what's actually under the growth."),
    ("You get it in writing", "A written estimate with the scope spelled out — "
     "including whether the job needs a permit and who pulls it."),
    ("We schedule it", "You get a date and a window, and we tell you if weather "
     "moves it. Ground conditions matter more than the calendar in this work."),
    ("We finish and clean up", "Debris hauled off, not stacked in a corner. "
     "You walk it with us before we leave."),
]

# ------------------------------------------------------------------- todo
# Rendered on-page as visible notices so nothing unverified ships silently.
CLIENT_TODO = {
    "insurance": "Confirm general liability coverage and the carrier name before "
                 "publishing any “Fully Insured” badge. Missouri has no statewide "
                 "landscaping or masonry licence, so avoid the word “Licensed” "
                 "unless you hold a specific municipal registration or a Missouri "
                 "Dept. of Agriculture Commercial Applicator licence — name that "
                 "one specifically if you have it.",
    "reviews": "Reviews are placeholders. Connect a live Google review widget once "
               "the Google Business Profile has real reviews on it. Do not hand-write "
               "testimonials or add aggregateRating markup with invented numbers.",
    "photos": "Every image on the site is a marked placeholder sized to the final "
              "layout. Send real job photos — your machine, your dirt, your finished "
              "walls — and they drop straight in. This is the single biggest upgrade "
              "available to the site.",
    "stats": "Years in business, jobs completed and acres cleared are left blank on "
             "purpose. Fill them in with real numbers you can defend.",
    "address": "No street address is published, which is correct for a service-area "
               "business. Set the Google Business Profile up the same way — service "
               "areas by city, address hidden.",
}
