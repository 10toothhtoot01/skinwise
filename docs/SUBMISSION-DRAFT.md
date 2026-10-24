# Skinwise

**Tagline:** One change. A clearer skincare story.

## Problem

People often assess a skincare purchase with memory and photos taken under different conditions. Simultaneous routine changes and missing context make those observations difficult to interpret. Skinwise gives a person a structured way to record what they changed, how their skin felt, and what a comparable image analysis estimated.

## What it does

Skinwise pairs YouCam skin appearance analysis with a one-change journal. The user prepares a photo, consents to processing, receives appearance scores, selects a single routine change to observe, and logs check-ins with notes and comfort. History views keep source and capture provenance visible and show matching metrics descriptively, with warnings when capture context is unknown or changed. Export and deletion controls give the person direct control of browser journal data.

## YouCam integration

The server adapter validates an image, creates a YouCam upload, submits a Skin Analysis task, and lets the browser poll the asynchronous job. It surfaces actual provider failures and extracts documented UI scores. API keys are server-only. The app includes a separate sample walkthrough so its journal interactions can be explored without representing synthetic fixtures as live analysis.

## Value beyond an API call

The product preserves context after a result: a deliberate change, context recorded over time, and a comparison with limitations explained. It does not diagnose skin conditions, prescribe treatment, sell a guaranteed result, or infer that an observed score change proves product effectiveness.

## Stack

React, TypeScript, Vinext, Cloudflare Workers runtime, browser-local journal persistence, YouCam REST APIs. Development and reviews follow vetted GitHub skill methods recorded in BUILD-DECISIONS.md and accompanying provenance.

## Honest completion checklist

- [ ] Live API successfully exercised with a consenting adult photo; record evidence without retaining photo/key.
- [ ] Final functional screenshots attached.
- [ ] Source repository accessible to judges with license and reproducible setup.
- [ ] Published demo video URL (1–3 minutes).
- [ ] Final deployed app URL and access instructions for judges.
- [ ] Confirm all current eligibility and submission rules on Devpost.

These boxes describe remaining submission obligations; this draft is not evidence they are complete.

## Accuracy boundary

The shipped prototype is not a validated product-effectiveness evaluator. We separate software verification from model validity, preserve unknown model-build identity, avoid cross-metric clinical priorities, and explain that score changes may be photographic noise. Guided capture is designed to reduce acquisition problems; real-hardware and subgroup validation remain future work. See ACCURACY-EVIDENCE.md and CAPTURE-RELIABILITY.md.
