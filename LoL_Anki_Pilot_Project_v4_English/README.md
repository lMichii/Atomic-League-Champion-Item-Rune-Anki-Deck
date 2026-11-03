# League of Legends Anki Pilot v4 (English)

**64 cards:** L0 terminology 25 (including new True Damage), L1 champion overview 6, L2 abilities 30 and hook timers 3. Ahri, Ezreal, Blitzcrank, Nautilus, Thresh and Locke.

## v4 changes

- Ezreal's L1 **Build focus: AD**. Mixed spell damage is described only where it is relevant on ability cards. Build focus means *typical itemization*, not the damage type of each ability.
- Every passive front explicitly identifies the champion, e.g. **AHRI · PASSIVE**. The icon tests the passive effect, not the identity of the champion. Active spell fronts still use animated GIFs and reveal name/slot/icon on the back.
- L0 now includes a **True Damage** terminology card: ignores Armor and MR, can still be absorbed by shields.
- Automatic highlighting from editable CSV text: AP/magic damage = blue, AD/physical damage = orange, true damage = white underline, MR = violet, Armor = gold, Health = green, Mana = teal. Terms remain written out for accessibility.
- No reverse cards. Passives remain icon-first; optional visual cues can be added using `visual_cue_media_path` once reviewed.

## Rebuilding on Windows

1. Edit `cards.csv` in a UTF-8 capable editor or Excel (save as **CSV UTF-8**).
2. Double-click `start_windows.bat`, or use `python build_deck.py` in this folder.
3. Import the generated `LoL_Anki_Pilot_6_Champions_v4_English.apkg` into Anki.

No Python packages or FFmpeg required for rebuilding, since GIFs are already supplied. Keep existing files in `media/` and do not change card IDs (`id` column) when making normal content corrections.

## Updates from v3 and scheduling

The 63 original note GUIDs, note type ID, field names/order and card template count are unchanged. Only CSV content, formatting in CSS, and one new terminology note were added. Make an Anki backup before importing and confirm existing learning progress remains intact. The import may require an option to update existing notes and/or note types. If the v3 *styling* doesn't refresh in your Anki collection, open **Tools > Manage Note Types**, select `LoL Pilot · Media Cards V1`, inspect the Cards CSS/template, or test in a clean profile. Don't delete learned notes just to refresh styling.

## Manual review before scaling

The imported videos were not re-audited for the newest patch, and six passive visuals remain marked for review in `cards.csv`. For ability-specific numeric facts, always recheck the League Wiki for the intended patch.
