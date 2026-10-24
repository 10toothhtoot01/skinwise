# Live YouCam workflow verification

Verified October24,2026 at02:45IST (2026-10-23T21:15:07Z).

One real provider analysis completed through the local application API running in the Vinext/Cloudflare Workers runtime. Input was an AI-generated adult portrait,1254×1254PNG approximately1.5MB. No real person was depicted. This proves integration behavior; the resulting scores do not establish clinical accuracy or validity for real skin.

## Observed results

- GET `/api/status`: HTTP200, configuredtrue.
- POST `/api/analyze` with multipart field `file`: HTTP202, running,12units.
- GET `/api/analyze` using the issued signed receipt after10seconds: HTTP200, success, source`youcam`, six supported metrics.
- No second paid task was started. Earlier failures occurred before provider task creation.

| Metric | Actual returned UI score |
|---|---:|
| Hydration |72|
| Texture |72|
| Pores |71|
| Redness |78|
| Blemishes |92|
| Oil balance |66|

Higher UI scores are better according to the vendor interpretation guide. The earlier adapter sorted oiliness, pores, and moisture by their numeric values. These are observations on unrelated scales, not validated action priorities; the adapter now returns an empty concerns list. These values came from the provider response; the app did not synthesize them. Current labels explicitly describe appearance or estimates. Method metadata identifies endpoint2.1 andSD, while modelVersion remains null because the provider did not return its engine build.

The zero-cost unit endpoint reported1040spendable units before the analysis and1028afterward, confirming a12unit deduction.

## Runtime defects found and corrected

1. Vinext parses multipart requests before dispatching route handlers and applies its server-action body limit. Default1MB blocked the documented upload size before application validation. `experimental.serverActions.bodySizeLimit:'9mb'` now permits multipart overhead around an8MB file; the application independently bounds streamed reads at9MB and rejects files over8MB. The original1.5MBPNG passed after restart.
2. Workers rejects fetch redirect mode`error`. Both provider requests and presigned uploads now use`manual`; their existing response checks reject redirects without following them or forwarding bearer credentials. A regression assertion verifies the redirect option on every mocked network call.

`node --experimental-strip-types --test tests/api.test.mjs`:5/5pass. TypeScript and scoped ESLint also passed after both fixes.

## Evidence handling and limits

Public evidence excludes the API key, presigned upload URL, task identifier, and signed task token. The resumable receipt is stored only in the private working evidence directory. No real-person selfie has been analyzed, browser photo acquisition was not part of this provider check, and this does not claim that hosting secrets have been configured on a remote deployment. Preserve owner-private site access until intentional spending controls are in place.
