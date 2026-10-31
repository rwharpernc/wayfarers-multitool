# Powerplay merit limits: research notes

This page is research only. No code changed because of it. It records one question, how it was checked, and what was found, so the question is not asked again from scratch. For how WFMT attributes merits today, see [POWERPLAY_TECH_SPEC.md](POWERPLAY_TECH_SPEC.md).

Checked on 2026-10-29 against journals from 2025-05-20 to 2026-10-29.

**On this page:**

- [Question](#question)
- [Answer](#answer)
- [What the journals show](#what-the-journals-show)
- [What published sources say](#what-published-sources-say)
- [Open items](#open-items)
- [Sources](#sources)

## Question

Is there a daily cap on the merits a commander can earn? If there were, WFMT could show how much of it is left. The same check was run for weekly and per-delivery limits.

## Answer

No cap was found, at any level, in the journals or in published sources. A "merits remaining" display has nothing to measure against and is not planned.

## What the journals show

Method: every `PowerplayMerits` event (24,788 of them) was totaled per UTC day and per cycle (Thursday 07:00 UTC to the next Thursday, assumed as the boundary). Every `PowerplayDeliver` event was paired with the merit events that followed it within 6 seconds.

**Daily and cycle totals**

- The busiest day earned 604,921 merits and the busiest cycle 1,153,708. The median day was 17,656.
- The top days and cycles are spread out. They do not level off at a common value, which a cap would produce.

**Hand-ins (Power commodities and data)**

- The two types with enough hand-ins to compare, `markedslaves` and `utopiandissident`, pay about the same per delivery whatever the count: 8 units paid about 3,640, 30 units about 3,700 to 3,800, and 120 units 4,561. The pay is flat per delivery, not smaller per unit.
- `siriusfranchisepackage` pays a steady 6 merits per unit, including one 1,000-unit hand-in that paid 6,000.
- Some types, such as `utopianpublicity` and `utopianfieldsupplies`, often pay only about 3 to 7 per unit.
- Some deliveries paid 0 or a few hundred merits where the same type normally pays about 3,700.
  - They happen when the commander had earned nothing yet that cycle (for example a 60-unit delivery that paid 396) and after more than 500,000 (a 64-unit delivery that paid 0).
  - So earnings to date do not explain them. The cause is **open**. The hand-in may have gone to a target or system that does not count, or the merit event may have arrived outside the 6-second window.

## What published sources say

All of this is secondhand. None of it was checked against the game.

- Frontier's Powerplay 2.0 Q&A states there are no diminishing-return restrictions.
- Players reported diminishing returns when selling goods in the Powerplay 2.0 merit-changes thread. One described repeated sales of the same commodity paying about 2,400 merits three times, then 1,300, then nothing by the fifth. Another claimed trading merits scale with the square root of the quantity sold. Neither is confirmed, and both disagree with the Q&A.
- The Trailblazers Update 3 notes give offensive actions +5% merits and defensive actions (Reinforcing) -35%. This was seen only in a search summary, so read the notes before relying on it.
- Merit decay at the weekly reset is described in older guides. Community pages say Powerplay 2.0 removed merit degradation. Control scores, not merits, decay each week (Update 3.4).
- Frontier switched off merits for rare goods, settlement data delivery and escape pods in November 2024. Whether they were restored was not found.
- A July 2026 report says players were unsure whether weekly assignments must be repeated every week to keep ranking up. It came from a secondary site and is unconfirmed.
- An answer from a web search engine said there is no daily limit and mentioned logarithmic scaling on bulk trades. It named no source, and it does not match the hand-in pay above.

## Open items

- **Zero-pay and low-pay hand-ins.** Find what separates them from normal ones. The journal does not report the hand-in target.
- **Sales of mined goods, exploration data and trade goods.** The diminishing-returns reports concern these, and the hand-in check above does not cover them. They would need merits matched to a sale, not to a `PowerplayDeliver`.
- **Reinforcement against Undermining pay.** If the Update 3 multipliers hold, the ledger should show defensive merits about 40% lower than offensive ones for comparable work. Not yet checked.

## Sources

- [Powerplay 2.0 Q&A](https://www.elitedangerous.com/news/powerplay-20-qa) (Frontier)
- [Powerplay 2.0 Merit Changes](https://forums.frontier.co.uk/threads/elite-dangerous-powerplay-2-0-merit-changes.630583/page-6) (Frontier forums, player posts)
- [Trailblazers Update 3 notes](https://www.elitedangerous.com/update-notes/4-1-2-0) and [Update 3.4 notes](https://www.elitedangerous.com/update-notes/4-1-2-103) (Frontier)
