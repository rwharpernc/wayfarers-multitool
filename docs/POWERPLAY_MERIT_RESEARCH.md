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

## Open items

- Zero-pay and low-pay hand-ins: the cause is not determined. The journal does not report the hand-in target.
- Sales of mined goods, exploration data and trade goods: the diminishing-returns reports concern these. They require merits matched to a sale rather than to a `PowerplayDeliver` event.

## Sources

- [Powerplay 2.0 Q&A](https://www.elitedangerous.com/news/powerplay-20-qa) (Frontier)
- [Powerplay 2.0 Merit Changes](https://forums.frontier.co.uk/threads/elite-dangerous-powerplay-2-0-merit-changes.630583/page-6) (Frontier forums, player posts)
- [Update 3.4 notes](https://www.elitedangerous.com/update-notes/4-1-2-103) (Frontier)
