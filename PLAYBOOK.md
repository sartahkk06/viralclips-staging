# ViralClips playbook (YouTube Shorts only, for now)

Owner: Sarthak Nandvikar. Channel: "Sarthak Nandvikar" (@sarthaknandvikar1968, id UCKJ4b986A3TRxBV5Hsdczkg).
Instagram is OFF until Sarthak says to add it.

## Daily rhythm (IST)
- 09:23 PRODUCTION run: research trends → ideas → copyright check → make up to 10 clips (only ones that pass every check; never pad with weak or repetitive clips) → upload each to YouTube as PRIVATE → save to Drive + this repo → log → message Sarthak the links.
- 12:10, 15:10, 17:10, 19:10, 21:10 POSTING runs: publish ONE approved clip per run (max 5/day, at least 2h apart). Approved clips beyond 5 carry over to the next day, oldest first.
- Approval signal: Sarthak checks the Copyright column in YouTube Studio and changes a clip from Private to UNLISTED. Only UNLISTED clips may be made public. Private = not approved; never publish it.

## Infrastructure
- Repo: sartahkk06/viralclips-staging (public). Attach with push access, clone to /home/claude/viralclips-staging.
- Clip files go in clips/YYYY-MM-DD/. After pushing, use the COMMIT-PINNED raw URL so caches never serve an old file:
  https://raw.githubusercontent.com/sartahkk06/viralclips-staging/<commit-sha>/clips/YYYY-MM-DD/<file>
- Renderer: tools/setup.sh (deps + CC0 voice; stops if the voice license is not CC0), then
  python3 tools/make_clip.py <out_dir> <spec.json> → clip.mp4 (1080x1920, H.264/AAC), thumb.png.
  Spec format is documented at the top of tools/make_clip.py. Example spec for clip 01: clips/2026-11-19/clip01-make_clip.py (old inline version).
- Zapier MCP (load with ToolSearch "zapier"; always inspect_zapier_actions before executing):
  - YouTube: upload_video (tool youtube_upload_video). Params used: video (raw URL), title, description, tags, privacy_status "private", made_for_kids "false", category_id "20" (Gaming) or best fit, default_language "en", default_audio_language "en", notify_subscribers "false".
  - YouTube read: youtube_make_api_get_request, url https://www.googleapis.com/youtube/v3/videos, querystring {"part":"status,processingDetails,contentDetails","id":"<ids>"}; channel uploads: /youtube/v3/playlistItems part=snippet,status playlistId=UUKJ4b986A3TRxBV5Hsdczkg maxResults=25.
  - YouTube publish: youtube_make_api_mutating_request, method PUT, url https://www.googleapis.com/youtube/v3/videos, querystring {"part":"status"} (putting ?part= in the url fails with 400), headers {"Content-Type":"application/json"}, body {"id":"<id>","status":{"privacyStatus":"public","selfDeclaredMadeForKids":false,"embeddable":true,"publicStatsViewable":true,"license":"youtube"}}.
  - Google Drive (account sarthaksmtrials@gmail.com): ViralClips folder id 1nsaLwkIgVkYc9QCCRZ82s_tjzUO-oKk2. Create the day folder with google_drive_create_folder (title YYYY-MM-DD, folder = ViralClips id). Upload with google_drive_upload_file (file = raw URL, folder = day folder id, new_name WITHOUT extension, because Zapier appends it). Then fix the name with google_drive_update_file_or_folder_metadata if it doubled.
- Log: log.csv in this repo (one row per clip). Columns: date,clip_id,trend,idea,assets_and_licenses,copyright_check,yt_id,yt_link,status,views_24h,likes_24h,views_7d,likes_7d,notes. Upload a copy to the day's Drive folder after each run.

## Production steps
1. Trend research (last 24–48h; India first, then global): cricket, Bollywood/OTT news, Indian gaming (BGMI, GTA, Valorant), tech launches, viral news, global game launches and challenges. Use WebSearch (some sources such as TikTok Creative Center and X trending are not readable; note it). Write trend-report.md: top 15 trends with platform, region, why viral, expected lifespan, source links.
2. 15+ ideas (aim for variety: different topics/categories, not 5 clips on one story), each with: 2-second hook text, format, script outline, footage plan, title, description, hashtags (Hinglish + English), virality score 1–10 with reason. Pick the top 10 (fewer if not enough are safe and distinct). Save ideas.md.
3. Copyright check for EVERY asset, recorded in clipNN-assets-and-rights.md. Allowed: (a) original generated visuals, text, AI voice; (b) real photos/video from: Pexels (Pexels License), Pixabay (Content License), Wikimedia Commons ONLY if CC0, Public Domain or CC BY (no BY-SA, NC, ND), NASA images (public domain, no NASA logo). Save source URL, author and license text for every file. No identifiable people from stock sites in a misleading context; no stock shot presented as if it shows the actual news event (label it "representative image" on screen). At the start of each run test that these sites are reachable; if blocked, note it and use original visuals; (c) explicit creator clip permission, saved; (d) press kits only where the license explicitly allows reuse. Use real media (make_clip.py scene "media" field) in most scenes when a licensed match exists; keep animated text on top. Never: others' video, movie/TV/IPL/sports broadcast, celebrity/player photos from news sites or social media, copyrighted or "trending" music, news footage, logos, game footage, anything unclear. One failing asset means the idea is dropped and logged.
4. Make clips: 20–45s, voice slightly fast (Piper length-scale 0.84, set in make_clip.py), hook in first 2s, burned captions, loopable ending, substantial original value (explanation/analysis/commentary). Watch a contact sheet of frames before uploading. No emoji in on-screen text (font can't draw them).
5. Pre-publish checklist (all YES or don't upload): licenses saved; no copyrighted music/audio; no misleading logos/trademarks; no real private individuals, no misleading claims or fake news (every fact sourced, numbers checked); YouTube community guidelines; credits in the description.
6. Upload each clip PRIVATE with title ending "#Shorts", description with sources and "Voiceover: AI-generated. Visuals: original.", hashtags. Retry a failed upload once, then log.
7. Push files to the repo, copy to Drive, update log.csv.
8. Message Sarthak: top 5 trends, the private links, what was skipped and why, and the reminder "set to Unlisted in Studio to approve".

## Posting steps
1. List recent uploads. For each Unlisted clip uploaded by this pipeline (title in log.csv): check status.uploadStatus == "processed", no rejectionReason, no contentDetails.regionRestriction. Any issue → don't publish, log it, message Sarthak.
2. Publish the OLDEST clean Unlisted clip (only one per run). Never publish within 2h of the last publish, or more than 5 per IST day.
3. Update log.csv (status public, link), push, copy to Drive.
4. In the 21:10 run also fill views/likes for clips 24h and 7d old (youtube/v3/videos part=statistics) and write the daily summary: clips posted with links, skipped and why, any claims, yesterday's best performer, and what to weight toward tomorrow.

## Hard rules
- Unsure about rights → skip. Never "risk it".
- No sexual, hateful, violent or one-sided political content; no clickbait lies.
- Never delete or edit Sarthak's existing videos. Only touch videos this pipeline uploaded (listed in log.csv).
- If any sign of a copyright claim, warning or strike on the account appears, stop posting and message Sarthak.
- Never mention S3K Technologies' client names in any content.
