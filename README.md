---
title: Ads Ai Dashboard
emoji: 👁
colorFrom: blue
colorTo: gray
sdk: gradio
sdk_version: 6.15.2
python_version: '3.13'
app_file: app.py
pinned: false
short_description: Ad management for Preschool
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# PreschoolPulse

PreschoolPulse is a small Gradio app for tracking preschool ad performance, leads, and budget recommendations.

It is built for the Build Small Hackathon idea of keeping the model small while still solving a real workflow problem for a preschool owner.

## What It Does

- Shows demo campaigns for Meta and Google Ads
- Tracks leads by campaign
- Displays metric snapshots with spend, leads, clicks, impressions, CTR, and CPL
- Generates structured recommendations with action, reason, and risk
- Presents a compact summary on the main page and a detailed recommendation view in its own tab

## Project Structure

- `app.py` - Gradio entry point
- `config/` - app settings
- `data/` - sample data and local storage helpers
- `models/` - campaign, lead, metric snapshot, and recommendation objects
- `engine/` - recommendation and insight logic
- `services/` - metrics aggregation helpers
- `ui/` - dashboard layout and table rendering

## Run It

On Windows, from the project folder:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

If you already have the environment active, this also works:

```powershell
python app.py
```

Then open the local Gradio URL shown in the terminal, usually:

```text
http://127.0.0.1:7860
```

## Demo Data

The app ships with three sample campaigns designed to show different behaviors:

- one strong performer that should be scaled
- one average performer that should be modified
- one weak performer that should be paused

This makes the dashboard useful for demos even before connecting real Meta or Google Ads accounts.

## Notes

- Real ad platform API integrations are still stubbed out in `ads/`
- Demo content is seeded locally so the app works immediately
- The detailed recommendations tab is the place for fuller explanations, while the top summary stays compact

## Next Steps

- Connect `ads/meta_ads.py` and `ads/google_ads.py` to live APIs
- Add scheduled sync jobs for real campaign refreshes
- Add authentication and alerts if you want this to run continuously for production use
