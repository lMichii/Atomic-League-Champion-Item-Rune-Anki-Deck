"""Refresh the readable production QA report from immutable review and run artifacts."""
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lol_anki.io import atomic,read_json,write_json
from lol_anki.package import inspect_apkg

qa=ROOT/'data/batch01/qa'
report=read_json(qa/'report.json')
editorial=read_json(ROOT/'data/batch01/editorial_review.json')
validation=read_json(ROOT/'build/batch01/reports/validation.json')
report['package']=inspect_apkg(ROOT/'build/LoL_Anki_Batch_01_100_Cards.apkg')
report['validation']={k:validation[k] for k in ('errors','warnings')}
report['tests']=read_json(ROOT/'build/reports/tests.json')
report['reimport']=read_json(ROOT/'build/batch01/reimport_verification.json')
report['asset_validation_summary']={k:v for k,v in read_json(qa/'asset_validation.json').items() if k!='records'}
report['change_review']=read_json(ROOT/'data/content/production.lock.json')['reviews'][-1]
for card in report['cards']:
    card['content_issues']=[issue for issue in editorial['source_conflicts'] if issue['champion']==card['champion'] and card['slot'] in (issue['slot'],'-')]
    card['wiki_revision_url']=f"https://wiki.leagueoflegends.com/en-us/{card['champion']}?oldid={card['wiki_revision']}"
write_json(qa/'report.json',report)
classification=read_json(qa/'pilot_warning_classification.json')
classification['counts']={'blocking_error':0,**classification['counts']}
write_json(qa/'pilot_warning_classification.json',classification)
# Retain exactly what was inspected; these are QA-only, never packaged media.
for source in (ROOT/'build/batch01/contact_sheets').glob('*.jpg'):
    destination=qa/'contact_sheets'/source.name
    atomic(destination,source.read_bytes())
write_json(qa/'validation.json',validation)
lines=['# Batch 01 production QA','',
       '**100 cards: 64 unchanged pilots + 36 approved Batch 01 additions. Withheld: 0.**','',
       'Approval covers source-grounded qualitative learning content and official media suitability after frame review. Current-client, skin, opponent-view and target-device playback checks remain explicit follow-up items. Reviewer: Codex; no human or live-client review is implied.','',
       '## Baseline warning classification','',
       '| Category | Warning records | Treatment |','| --- | ---: | --- |',
       '| Blocking structural errors | 0 | None found; any new identity/media/schema failure blocks export. |',
       '| Factual review requirements | 73 | 64 missing evidence + 9 editorial/timer QA labels. Retained pilots unchanged; no automatic approval. |',
       '| Media review requirements | 40 | 30 pending media QA + 6 passive cues + 4 Locke active GIF gaps. Still visible. |',
       '| Non-blocking metadata warnings | 31 | 25 general-term labels + 6 hash-pinned CDragon snapshots with unknown upstream release. No claimed verification. |','',
       'The 144 records overlap at card level. Full classification: [pilot_warning_classification.json](pilot_warning_classification.json).','',
       '## New sources and content decisions','',
       'All six official Riot pages, six versioned Data Dragon details, six pinned CommunityDragon records and six Wiki pages were retrieved. Wiki HTML includes revision IDs and is retained byte-for-byte. No unresolved Batch 01 source access failures. Snapshots, source URLs, claims and hashes are in production source/content JSON.','',
       '- Lux overview: replaced “across the map” with “long-range”; Final Spark is not presented as global.',
       '- Ashe passive: removed the bonus-damage condition disputed between Riot and Wiki. The card states their shared slow/critical-slow behavior.',
       '- Leona passive: sources disagree on duration; no duration is taught.',
       '- Clarified damage types, Caitlyn Q trap exception, Morgana shield condition and Jinx passive qualifying targets using the archived sources.',
       '- Repaired replacement characters in the supplied draft, retained its 36 IDs, and kept every card in English.',
       '- Counterplay is explicitly marked as a teaching inference from cited mechanics, not an empirical matchup guarantee. Build focus is broad AD/AP/tank-stat orientation, not an optimal-build claim.',
       '- No new cooldown, damage formula, exact scaling or L3 cards.','',
       '## Media and passive cues','',
       'Real media: **6 splash portraits, 30 ability icons, 24 looping active GIFs, 4 supplementary passive GIFs**. All 30 original WebMs are archived. No new active fallbacks or unresolved active media. The production APKG references **120** real files. Every new image and every GIF frame decoded successfully.','',
       '| Passive | Release cue | Required follow-up |','| --- | --- | --- |']
for name,cue in editorial['passive_cues'].items():
    lines.append(f"| {name} | {'Icon + official P GIF' if cue['include'] else 'Champion-labeled icon; cue unresolved'} | {cue['manual_follow_up']} |")
lines += ['', 'Caitlyn’s demonstration is included to support Headshot recognition; a precise ready-state glow/color is not asserted. Leona’s mark and Morgana’s healing feedback were not isolated confidently enough to approve supplementary cues. The contact sheets are available in [contact_sheets](contact_sheets/).','',
          'Some source WebMs emit Opus audio-header diagnostics. Audio is absent from GIF output; all emitted GIF frames were fully decoded. No diagnostic was silently turned into a media verification claim.','',
          '## Card-by-card release register','',
          '| Stable card ID | Front | Content decision / unresolved follow-up |','| --- | --- | --- |']
production=read_json(ROOT/'data/content/production.json')
cards={c['id']:c for c in production['cards']}
for card in report['cards']:
    row=cards[card['id']]['row']
    front='portrait' if card['level']=='L1' else ('passive icon + GIF' if row['visual_cue_media_path'] else row['media_type'])
    follow='Approved; '+(card['manual_visual_review'] or 'portrait identity checked; broad build focus and counterplay remain editorial teaching guidance.')
    lines.append(f"| `{card['id']}` | {front} | {follow} |")
lines += ['', 'Full changes, per-card media/source hashes, Wiki revision links, conflicts and decisions: [report.json](report.json).','',
          '## Validation and reimport','',
          f"- Structural errors: **{validation['errors']}**. Warning records: **{validation['warnings']}**.",
          '- All 144 inherited records remain. New follow-ups: 36 editorial counterplay labels + 30 current-client visual checks + 2 unresolved passive cues = 68.',
          f"- **{report['tests']['tests_run']} tests passed**, with {report['tests']['failures']} failures, {report['tests']['errors']} errors and {report['tests']['skipped']} skips.",
          '- Exact v4 CSS, stat colors, field order, note type and single forward template preserved. Pilot IDs, note fields/revisions and media bytes unchanged.',
          '- Actual Anki 25.9.2 importer: original 64 → 100 → repeated 100. All 64 pilot schedules and 64 test review-history rows preserved; all 120 media files imported. User collection never opened.',
          '- Repeated production builds are byte-identical; no mass expansion beyond Batch 01.',
          '- Headless import and frame/asset checks do not substitute for desktop/mobile GUI playback or current-client gameplay review.','',
          'Package: `build/LoL_Anki_Batch_01_100_Cards.apkg`.',
          f"SHA-256: `{report['package']['sha256']}`.",'',
          f"Applied proposal: `{report['change_review']['proposal_sha256']}`. Only the 36 new IDs were changed; [the receipt](../../content/production.lock.json) records the reviewer and source promotion.",'']
atomic(qa/'report.md',('\n'.join(lines)).encode())
print('Updated',qa/'report.md')
