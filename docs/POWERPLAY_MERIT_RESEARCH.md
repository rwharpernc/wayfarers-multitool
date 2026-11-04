# Powerplay merit limits: research notes

This page records one research question about Powerplay merit limits, the method used, and the result. No code depends on it. For merit attribution in WFMT, see [POWERPLAY_TECH_SPEC.md](POWERPLAY_TECH_SPEC.md).

- Checked on: 2026-10-29.
- Journals examined: 2025-05-20 to 2026-10-29.
- The journal figures below come from the project owner's own journal files. They are not reproducible from the repository.

**On this page:**

- [Question](#question)
- [Result](#result)
- [Journal analysis](#journal-analysis)
- [Published sources](#published-sources)
- [Open items](#open-items)
- [Sources](#sources)

## Question

Whether a daily cap on earned merits exists. The same check was run for weekly and per-delivery limits.

## Result

No cap was found at any level in the journals or in the published sources. WFMT has no "merits remaining" display.

## Journal analysis

Method:

- Every `PowerplayMerits` event (24,788) was totaled per UTC day and per cycle. The cycle boundary was assumed to be Thursday 07:00 UTC.
- Every `PowerplayDeliver` event was paired with the merit events that followed it within 6 seconds.

Daily and cycle totals:

- Busiest day: 604,921 merits. Busiest cycle: 1,153,708 merits. Median day: 17,656 merits.
- The highest days and cycles do not level off at a common value.

Hand-ins (Power commodities and data):

- `markedslaves` and `utopiandissident` were the only types with enough hand-ins to compare. Pay per delivery was nearly independent of unit count: 8 units paid about 3,640; 30 units paid about 3,700 to 3,800; 120 units paid 4,561.
- `siriusfranchisepackage` paid 6 merits per unit, including one 1,000-unit hand-in that paid 6,000.
- `utopianpublicity` and `utopianfieldsupplies` often paid about 3 to 7 merits per unit.
- Some deliveries paid 0 or a few hundred merits where the same type normally paid about 3,700. These occurred both when the commander had earned no merits yet in the cycle (a 60-unit delivery paid 396) and after more than 500,000 merits (a 64-unit delivery paid 0). Earnings to date do not account for them. The cause is not determined.

## Published sources

- The Powerplay 2.0 Q&A states that there are no diminishing-return restrictions.
- Posts in the Powerplay 2.0 merit-changes forum thread report diminishing returns when selling goods: repeated sales of one commodity paid about 2,400 merits three times, then 1,300, then none by the fifth; another post states that trading merits scale with the square root of the quantity sold. Neither report is confirmed, and both differ from the Q&A.
- Community pages state that Powerplay 2.0 removed merit degradation, and that control scores, not merits, decay each week (Update 3.4).
- Frontier switched off merits for rare goods, settlement data delivery and escape pods in November 2024. Whether they were restored was not found.

None of the published statements was checked against the game.

## Trade merits: what players report (web research, 2026-11-04)

Searched the web only; no game play. None of this is from Frontier or checked in the game. The Frontier forum blocked automated reading (HTTP 403), so the forum figures below come from search-result summaries and one Steam thread read in full, not from the forum threads themselves.

- **Conditions reported** (Steam thread, 31 January to 2 February 2025, and forum summaries): a trade counts only with a profit of about 40% over the buying price (a 1,000 cr/t purchase must sell for 1,400 or more), in an Acquisition or Reinforcement system. For Acquisition, the goods are said to need buying in a system within range of a supporting Fortified (about 20 ly) or Stronghold (about 30 ly) system; one poster doubted this is stated in the game. Mined goods are said to count only when sold in the system they were mined in.
- **Amount, by profit:** one tester reported 1 merit per 1,000 cr of profit (22,000 cr gave 22 merits); another, from a spreadsheet, about 0.75 merits per 1,000 cr. A proposal in a forum thread suggested 1 merit per ton plus 1 merit per 15,000 cr of profit; it was a suggestion, not observed behavior.
- **Amount, by quantity:** the launch-period reports agree that selling one ton at a time paid far more per ton than a full hold: 1 t paid 28 merits, 10 t paid 88 and 100 t paid 276 (one tester); 320 t sold singly paid about 3,500 merits against about 200 sold as one lot (another). A post in the same thread period reports "square root of the quantity". Another Steam post gave 1 unit = 4 merits, 2 = 8 and 10 = 20 and called it a bug. These are launch-period figures; one thread was reported to Frontier's issue tracker, and later reports say the one-ton method was addressed. How it behaves now was not found.
- **Intended design:** a player summary of a Frontier discussion says normal trading was meant to give one third for tonnage and two thirds for profit, aiming at about 400 merits a trip. Unconfirmed.
- **Rare goods:** reported as the best earner at launch, then reduced, then switched off in November 2024 together with settlement data and escape pods. Whether they were restored was not found.
- **Zero-pay deliveries:** one tester reported three trades that met every condition above paying nothing after earlier ones paid. No cause was found, matching the zero-pay hand-ins in the journal analysis.

What this does not settle: the live formula. The figures conflict (per profit, per ton, square root), they date from 2025 or earlier, and no 2026 source on trade merits was found. A number from this list should not be shown in WFMT as an estimate.

## Open items

- Zero-pay and low-pay hand-ins: the cause is not determined. The journal does not report the hand-in target.
- Sales of mined goods, exploration data and trade goods: the diminishing-returns reports concern these. They require merits matched to a sale rather than to a `PowerplayDeliver` event. The web reports above leave the current rule open; measuring it needs sales made while pledged, with the merits that follow each one, in systems that qualify (Acquisition or Reinforcement, 40% profit).

## Sources

- [Powerplay 2.0 Q&A](https://www.elitedangerous.com/news/powerplay-20-qa) (Frontier)
- [Powerplay 2.0 Merit Changes](https://forums.frontier.co.uk/threads/elite-dangerous-powerplay-2-0-merit-changes.630583/page-6) (Frontier forums, player posts)
- [Update 3.4 notes](https://www.elitedangerous.com/update-notes/4-1-2-103) (Frontier)
