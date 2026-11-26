# ViralClips playbook (YouTube Shorts only, for now)

Owner: Sarthak Nandvikar. Channel: "Sarthak Nandvikar" (@sarthaknandvikar1968, id UCKJ4b986A3TRxBV5Hsdczkg).
Instagram is OFF until Sarthak says to add it.

## Daily rhythm (IST)
- 09:23 PRODUCTION run: research trends → ideas → copyright check → make up to 10 clips (only ones that pass every check; never pad with weak or repetitive clips) → upload each to YouTube as UNLISTED (auto-approved) → save to Drive + this repo → log (with a best-first rank) → message Sarthak the links.
- 12:10, 15:10, 17:10, 19:10, 21:10 POSTING runs: publish ONE Unlisted clip per run (max 5/day, at least 2h apart). Clips beyond 5 carry over to the next day: oldest production date first, then by the "rank N" note in log.csv (rank 1 = best).
- Approval (from 24 Nov 2026, per Sarthak: "I don't want to open Studio every time"): the production run uploads every clip that passes all checks as UNLISTED, which counts as approved. Only UNLISTED clips may be made public. PRIVATE = vetoed or held: never publish it. Sarthak can veto a clip any time by setting it to Private in Studio. Clips 1-20 still Private from before this change stay Private (not approved).
- The YouTube Data API does not expose Content ID claims, so posting runs check what they can (uploadStatus processed, no rejectionReason, no regionRestriction) and Sarthak may still glance at the Copyright column when he wants.

## Infrastructure
- Repo: sartahkk06/viralclips-staging (public). Attach with push access, clone to /home/claude/viralclips-staging.
- Clip files go in clips/YYYY-MM-DD/. After pushing, use the COMMIT-PINNED raw URL so caches never serve an old file:
  https://raw.githubusercontent.com/sartahkk06/viralclips-staging/<commit-sha>/clips/YYYY-MM-DD/<file>
- Renderer: tools/setup.sh (deps + CC0 voice; stops if the voice license is not CC0), then
  python3 tools/make_clip.py <out_dir> <spec.json> → clip.mp4 (1080x1920, H.264/AAC), thumb.png.
  Spec format is documented at the top of tools/make_clip.py. Example spec for clip 01: clips/2026-11-19/clip01-make_clip.py (old inline version).
- Zapier MCP (load with ToolSearch "zapier"; always inspect_zapier_actions before executing):
  - YouTube: upload_video (tool youtube_upload_video). Params used: video (raw URL), title, description, tags, privacy_status "unlisted", made_for_kids "false", category_id "20" (Gaming) or best fit, default_language "en", default_audio_language "en", notify_subscribers "false".
  - YouTube read: youtube_make_api_get_request, url https://www.googleapis.com/youtube/v3/videos, querystring {"part":"status,processingDetails,contentDetails","id":"<ids>"}; channel uploads: /youtube/v3/playlistItems part=snippet,status playlistId=UUKJ4b986A3TRxBV5Hsdczkg maxResults=25.
  - YouTube publish: youtube_make_api_mutating_request, method PUT, url https://www.googleapis.com/youtube/v3/videos, querystring {"part":"status"} (putting ?part= in the url fails with 400), headers {"Content-Type":"application/json"}, body {"id":"<id>","status":{"privacyStatus":"public","selfDeclaredMadeForKids":false,"embeddable":true,"publicStatsViewable":true,"license":"youtube"}}.
  - Google Drive (account sarthaksmtrials@gmail.com): ViralClips folder id 1nsaLwkIgVkYc9QCCRZ82s_tjzUO-oKk2. Create the day folder with google_drive_create_folder (title YYYY-MM-DD, folder = ViralClips id). Upload with google_drive_upload_file (file = raw URL, folder = day folder id, new_name WITHOUT extension, because Zapier appends it). Then fix the name with google_drive_update_file_or_folder_metadata if it doubled.
- Log: log.csv in this repo (one row per clip). Columns: date,clip_id,trend,idea,assets_and_licenses,copyright_check,yt_id,yt_link,status,views_24h,likes_24h,views_7d,likes_7d,notes. Upload a copy to the day's Drive folder after each run.

## Content mix (from 26 Nov 2026, per Sarthak): HINDI ANIMATED ONLY
Every new clip is an original flat-2D cartoon with Hindi voiceover, made with tools/hindi_anim.py (spec format documented at the top of that file; examples: clips/2026-11-26/clip38..41-spec.json). No more English-voice clips.
Topics (rotate, vary every day):
- Puzzles / paheli / riddles / maths & logic puzzles (with options, 5-second timer, reveal). Classic puzzles are fine; write our own wording.
- Jokes: 100% original jokes as short 2-character dialogues with speech bubbles (doctor/patient, teacher/student, husband/wife, friends, boss/employee). Clean, family-friendly, no jokes about religion, caste, region, gender stereotypes, body shaming, disability or real people.
- Informative / educational: science, "kyun hota hai?", how things work, general knowledge. Every fact must come from a reliable source retrieved that day (NASA, NOAA, WHO, government sites, encyclopaedias, official docs) and be cited in the description.
- Tips & tricks: phone, money basics, study, daily life. Only safe, verifiable tips from official/reliable sources; no medical dosing, no financial "buy this" advice, no hacks that break laws or terms of service.
- Explaining situations: "agar aisa ho toh kya karein?", everyday situations explained (e.g. UPI payment failed, train ticket waitlist) with official sources.
Script rules:
- Hindi voice lines ("hi") in natural, everyday spoken Hindi (Devanagari), short sentences, commas for pauses. Avoid formal/Sanskritised words; use common English loanwords people say (phone, battery, setting, follow).
- Captions ("cap") in Hinglish (Roman), key words wrapped in *stars* for yellow highlight. On-screen text Latin script only (font has no Devanagari).
- 30–50 s, 6–9 scenes: hook in first 2 s, build-up, (for puzzles) options + 5 s timer, reveal/punchline, outro asking to comment/tag/follow.
- No fake statistics in hooks ("only 1% can solve" is not allowed unless sourced). Curiosity hooks are fine.
- Description must include: "Animation: original." and "Hindi voice: AI-generated with the SYSPIN TTS model by SPIRE Lab, IISc Bengaluru (CC BY 4.0)." plus sources for any facts.
- default category: 24 Entertainment (puzzles), 23 Comedy (jokes), 27 Education (informative/situations), 28 Science & Technology (tech tips).
Kids/baby content stays on hold (made-for-kids rules).

## Uploading
Try Zapier upload_video first. If Zapier says "throttled", use the Windsor.ai connector instead: connector "youtube", account "104863" (same channel, UCKJ4b986A3TRxBV5Hsdczkg), action "upload_video" with video_url = commit-pinned raw URL, title, description, tags, category_id, privacy_status, made_for_kids false. If Windsor says the connection is read-only, mark the clip upload-pending and tell Sarthak to reconnect at https://onboard.windsor.ai/app/youtube with every permission.

## Production steps
1. Trend research (last 24–48h; India first, then global): cricket, Bollywood/OTT news, Indian gaming (BGMI, GTA, Valorant), tech launches, viral news, global game launches and challenges. Use WebSearch (some sources such as TikTok Creative Center and X trending are not readable; note it). Write trend-report.md: top 15 trends with platform, region, why viral, expected lifespan, source links.
2. 15+ ideas (aim for variety: different topics/categories, not 5 clips on one story), each with: 2-second hook text, format, script outline, footage plan, title, description, hashtags (Hinglish + English), virality score 1–10 with reason. Pick the top 10 (fewer if not enough are safe and distinct). Save ideas.md.
3. Copyright check for EVERY asset, recorded in clipNN-assets-and-rights.md. Allowed: (a) original generated visuals, text, AI voice; (b) real photos/video from: Pexels (Pexels License), Pixabay (Content License), Wikimedia Commons ONLY if CC0, Public Domain or CC BY (no BY-SA, NC, ND), NASA images (public domain, no NASA logo). Save source URL, author and license text for every file. No identifiable people from stock sites in a misleading context; no stock shot presented as if it shows the actual news event (label it "representative image" on screen). At the start of each run test that these sites are reachable; if blocked, note it and use original visuals; (c) explicit creator clip permission, saved; (d) press kits only where the license explicitly allows reuse. Use real media (make_clip.py scene "media" field) in most scenes when a licensed match exists; keep animated text on top. Never: others' video, movie/TV/IPL/sports broadcast, celebrity/player photos from news sites or social media, copyrighted or "trending" music, news footage, logos, game footage, anything unclear. One failing asset means the idea is dropped and logged.
4. Make clips with tools/hindi_anim.py (30–50s), voice slightly fast (Piper length-scale 0.84, set in make_clip.py), hook in first 2s, burned captions, loopable ending, substantial original value (explanation/analysis/commentary). Watch a contact sheet of frames before uploading. No emoji in on-screen text (font can't draw them).
5. Pre-publish checklist (all YES or don't upload): licenses saved; no copyrighted music/audio; no misleading logos/trademarks; no real private individuals, no misleading claims or fake news (every fact sourced, numbers checked); YouTube community guidelines; credits in the description.
6. Upload each clip UNLISTED with title ending "#Shorts", description with sources and "Voiceover: AI-generated. Visuals: original.", hashtags. Retry a failed upload once, then log.
7. Push files to the repo, copy to Drive, update log.csv.
8. Message Sarthak: top 5 trends, the Unlisted links in publish order, what was skipped and why, and: "All clips are auto-approved (Unlisted) and will go public one per slot. To stop one, set it to Private in Studio."

## Posting steps
1. List recent uploads. For each Unlisted clip uploaded by this pipeline (title in log.csv): check status.uploadStatus == "processed", no rejectionReason, no contentDetails.regionRestriction. Any issue → don't publish, log it, message Sarthak.
2. Publish the next clean Unlisted clip (only one per run): oldest production date first, then lowest "rank N" in log.csv notes. Never publish within 2h of the last publish, or more than 5 per IST day.
3. Update log.csv (status public, link), push, copy to Drive.
4. In the 21:10 run also fill views/likes for clips 24h and 7d old (youtube/v3/videos part=statistics) and write the daily summary: clips posted with links, skipped and why, any claims, yesterday's best performer, and what to weight toward tomorrow.

## Hard rules
- Unsure about rights → skip. Never "risk it".
- No sexual, hateful, violent or one-sided political content; no clickbait lies.
- Never delete or edit Sarthak's existing videos. Only touch videos this pipeline uploaded (listed in log.csv).
- If any sign of a copyright claim, warning or strike on the account appears, stop posting and message Sarthak.
- Never mention S3K Technologies' client names in any content.

## Monetization safety (Sarthak: "monetization should not hurt")
- Post max 5 per day, at least 2h apart, even if 10 are made. Never bulk-post.
- YouTube's inauthentic / mass-produced content rule: every clip must add real original value (analysis, comparison, explanation), not read out a news headline. No two clips the same day on the same story with the same angle.
- Vary the look: rotate layouts, colours and real-media backgrounds; don't let every clip use the same template, hook wording or ending line.
- Reused content rule: no third-party footage, even short; licensed stock is background only, with our own narration and text as the main content.
- If a clip is realistic AI-made imagery of real people/events (we don't make these), turn on the "altered or synthetic content" label. AI voice over our own text needs no label, but keep "Voiceover: AI-generated" in the description.
- No clickbait titles that the video doesn't deliver on. Advertiser-friendly topics only.
- If YPP status, a monetization warning, or limited ads (yellow $) appears on any clip, stop producing, tell Sarthak.
