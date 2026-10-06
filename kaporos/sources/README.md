# Sources

Every article and video the film cites, archived so the edit has a source card for each claim and nothing
disappears before upload. `urls.txt` is generated from the citations in `../research.md`; `videos.txt` is the
archive footage list by act. Run `pull.sh` on the laptop. PDFs are committed; video and raw HTML are not (size).

| Act | Needs | From |
|---|---|---|
| 2.4 | U-Haul headlines on screen | Gothamist, amNY, News 12, JTA, Yeshiva World, Farm Sanctuary |
| 2.12 | Penelope poster + short film | penelopesplacethesanctuary.com, Gothamist 2015, theirturn.net |
| 2.13 | Rashba / Karo / Rema, OU, Rav Mazuz | sefaria.org (OC 605), koltorah, jewishideas, yeshivaworld |
| 4.1–4.2 | Chabad facts, 1996 RCA resolution, Berger, sticker funders | chabad.org, jweekly 1996, commentary.org, forward 2023 |
| 4.3 | tunnel: facts and debunks | factcheck.org, politifact, AP (columbian), Haaretz 2025, Newsweek, ABC |
| 4.4 | proclamations, Ohel visits, 1990 clip, Gold Medal, Milei, Putin/Lazar | whitehouse archives, congress.gov, JTA, jewishinsider, chabad.org, anash, collive, algemeiner, vinnews |
| 4.5 | Agriprocessors / Rubashkin / commutation / Kushner | PETA, animalpeopleforum, JTA, Forward, radioiowa, thegazette, CNN 2019, trumpwhitehouse archive, timesofisrael |
| 4.6 | Amidah/Musaf text, Temple Institute, red heifers, Temple Mount 2025–26, 770 as sanctuary | opensiddur, jewishencyclopedia, templeinstitute.org, texasmonthly, religionnews, israel365, nysun, haaretz 2026, jns (Hegseth), chabad.org 5752 discourse |
| 4.7 | Tanya ch. 1–2 in Chabad's translation; the JC defence | chabad.org/library/tanya, thejc.com |
| 5 | USDA numbers, Panarion 30.16.5, Cambridge NTS article | nass.usda.gov, earlychristianwritings, cambridge.org |

Rights: news clips and archive video are used under fair use for commentary and criticism; keep each clip short,
on screen with attribution, and never as the hero image of a thumbnail.

## Pull run 2026-10-06 (laptop)

`pull.sh` printed 95 of 105 article PDFs on the first pass; the rest were Cloudflare "Just a moment" pages (chabad.org ×11,
forward.com ×4, congress.gov ×2, israel365, religionnews, au.org), 403s (jweekly), or empty prints (timesofisrael ×3,
texasmonthly, thegazette, nysun, haaretz ×2, jpost ×2, newsweek, nycourts, yahoo, columbian, amny, chhatzalah). Those were
re-printed with `pdf_via_cdp.py` (a real headless Chrome that waits the challenge out), which cleared all but the six below.
`review_pdfs.py` now reports 99 of 105 readable. The two USDA reports are the original PDFs fetched with curl, not prints.

### Needs manual save

Open in the logged-in browser and print to PDF over the placeholder in `articles/`:

| # | URL | Why |
|---|---|---|
| 059 | columbian.com … fact-focus-discovery-of-a-tunnel-at-a-chabad-synagogue… | paywall ("Already a subscriber?"); the same AP piece is in 104 (yahoo) and factcheck/politifact (063, 091) |
| 061 | congress.gov/bill/103rd-congress/house-bill/4497 | "Verify you are human" — needs a real session |
| 062 | congress.gov/bill/119th-congress/house-resolution/852/text | same |
| 066 | haaretz.com … netanyahu-backs-expanded-jewish-prayer… (2026-01-05) | premium paywall, 39 words printed |
| 067 | haaretz.com … 6-chabad-tunnel-defendants-plead-guilty… (2025-01-15) | paywall, 40 words printed |
| 089 | nysun.com … ben-gvir-confirms-jews-prayed-out-loud… | subscription wall (headline + lede only) |

Spot-check, not verified: 039 (weanimals, 42 MB of photos) and 043 (animals24-7) printed huge; fine for a source card but
crop before putting on screen.

### Archive video (`video/`, not committed)

One file per `videos.txt` entry after review; the other search hits were deleted. Kept:

| Entry | Kept | Note |
|---|---|---|
| Netanyahu / Rebbe 1990 | `Bibi Netanyahu Meets the Rebbe 1990 [rHBiT6eJaQQ]` (JEM, 1:06) | collive.com link is a page, not a video: yt-dlp "Unsupported URL" |
| Trump at the Ohel 2024 | — | first pass left only .part files; a direct retry of the NBC clip (NcsjaSs8u5g; NY Post is Dx4pexT6pks, Forbes mK5wHVgjeQw) got YouTube's "page needs to be reloaded" throttle. Retry after a cool-down. |
| Education and Sharing Day | `Reagan Hosts Rabbis in Oval Office [74DgoRMwVqc]` | the Obama search returned nothing, twice |
| Yechi at 770 | `Singing Yechi On Eastern Parkway [yLWVR15UPJY]` | |
| Moshiach campaign stickers | — | no results, twice; shoot the stickers / billboards as pickups instead |
| Tunnel Jan 2024 | `Multiple arrested after digging hidden tunnel at Chabad headquarters [qQqJcxl6Xbg]` (ABC7) | NY Post / India Today / JewsOnTelevision deleted |
| Tunnel fact check | — | both hits were conspiracy channels; the fact-checks are articles 063 / 091 / 104 |
| PETA Agriprocessors 2004 | — | age-gated: needs `--cookies-from-browser chrome` run from a terminal (the Keychain prompt hangs a background run); the PETA page itself is article 090 |
| Postville raid 2008 | `Postville, Iowa Struggles on After ICE Raid [JYwG6Z6NvsA]` (AP) | |
| Rubashkin release 2017 | `Rubashkin arrives to his parents' house after release [3VCrbe1Pivk]` | |
| Temple Institute promo | `The Third Holy Temple Plans Have Begun [A2IkxmwkayM]` (official, 2015) | |
| Red heifers arrive 2022 | `Red Heifers' Arrival In Israel… [n2wzY_vcrSg]` | |
| Red heifer ceremony 2025 | `Biblical Prophecy? Video of Red Heifer Ceremony… [12ZVxYE56Ws]` (KENS 5, 38 min, the ceremony footage is inside) | |
| Hegseth Third Temple | — | no hit matched; search by hand for the actual speech clip |
| Ben Gvir Temple Mount 2025 | `Israeli minister sparks anger by praying… [i_I1A0Muq1E]` (BBC) | |
| Milei at the Ohel | — | no results, twice; try the Casa Rosada / Chabad.org clip by hand |
| Putin / Lazar | — | only hit was a conspiracy channel; find the Kremlin / TASS clip by hand |
| Fuentes / Jiang debate | — | reference only; not downloaded |
| 2026 press, U-Haul | — | search returned nothing, twice; the News 12 piece is article 041 (bronx.news12.com), save its player clip by hand |
| Kapparot 2026 | — | hits were 2012 / 2015; use the Christspiracy footage |
| Penelope | `Penelope: A Rescue Story [llFZmcy5Whw]` (12:19) | |

YouTube rate-limited the subtitle fetch (HTTP 429) part-way through, and by the end of the run was throttling downloads
and returning empty searches. Back off for an hour or more before rerunning `pull.sh` (it skips what exists); one retry per
~10 min recovers, hammering it does not. Subs for the kept files are there except where the 429 hit.
