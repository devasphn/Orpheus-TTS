# Orpheus TTS RunPod Deployment Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment

- [ ] RunPod account created
- [ ] Credits added to account (minimum $10)
- [ ] Docker Hub account created (if using custom image)
- [ ] Repository cloned locally
- [ ] Reviewed GPU requirements and pricing

## Docker Image Preparation (Choose One)

### Option A: Custom Docker Image
- [ ] Dockerfile reviewed and customized if needed
- [ ] Docker image built locally
- [ ] Docker image tested locally (optional)
- [ ] Image pushed to Docker Hub
- [ ] Image URL copied for RunPod

### Option B: Manual Setup
- [ ] Base PyTorch image selected
- [ ] server.py file ready to upload
- [ ] Installation commands prepared

## RunPod Pod Configuration

- [ ] GPU type selected (RTX 3090 or better recommended)
- [ ] Container image specified
- [ ] HTTP port 8080 exposed
- [ ] Container disk set to 20GB minimum
- [ ] Environment variables configured (optional):
  - [ ] MODEL_NAME
  - [ ] MAX_MODEL_LEN
  - [ ] PORT
- [ ] Volume disk configured (optional, for caching)
- [ ] Auto-stop configured (recommended)

## Deployment

- [ ] Pod deployed successfully
- [ ] Pod status shows "Running"
- [ ] Public URL obtained from pod details
- [ ] URL format verified: `https://[pod-id]-8080.proxy.runpod.net`

## Initial Testing

- [ ] Health check endpoint tested: `/health`
- [ ] Health check returns "healthy" status
- [ ] Voices endpoint tested: `/voices`
- [ ] Test TTS request completed successfully
- [ ] WAV file downloaded and plays correctly
- [ ] Audio quality verified

## Performance Verification

- [ ] Model loading time measured (30-120s expected)
- [ ] First inference latency checked (~200ms expected)
- [ ] GPU utilization verified with `nvidia-smi`
- [ ] VRAM usage checked (should be ~6GB)
- [ ] Multiple requests tested for stability

## Production Readiness (Optional)

- [ ] Gunicorn configured instead of Flask dev server
- [ ] API authentication implemented
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Error alerting configured
- [ ] Backup pod configured (for high availability)
- [ ] Load testing completed
- [ ] Cost monitoring enabled

## Documentation

- [ ] API endpoint URL documented
- [ ] API key stored securely (if using auth)
- [ ] Team members notified of deployment
- [ ] Usage examples created for your use case
- [ ] Troubleshooting steps documented

## Cost Optimization

- [ ] Auto-stop enabled
- [ ] Billing alerts configured
- [ ] GPU type optimized for workload
- [ ] Volume storage minimized
- [ ] Usage patterns monitored

## Ongoing Maintenance

- [ ] Weekly cost review scheduled
- [ ] Monthly performance review scheduled
- [ ] Model updates monitored
- [ ] Security updates planned
- [ ] Backup strategy defined

---

## Quick Reference

**Your Deployment Details:**

```
Pod ID: ___________________________
Public URL: ___________________________
GPU Type: ___________________________
Hourly Cost: $___________________________
Deployed Date: ___________________________
```

**API Endpoints:**
- Health: `https://your-url/health`
- Voices: `https://your-url/voices`
- TTS: `https://your-url/tts?prompt=text&voice=tara`

**Test Command:**
```bash
curl "https://your-url/tts?prompt=Hello%20world&voice=tara" --output test.wav
```

---

## Troubleshooting Quick Links

If you encounter issues, check:

1. **Model not loading**: [RUNPOD_DEPLOYMENT.md#issue-1-model-not-loading](RUNPOD_DEPLOYMENT.md#issue-1-model-not-loading)
2. **Out of memory**: [RUNPOD_DEPLOYMENT.md#issue-2-out-of-memory-oom](RUNPOD_DEPLOYMENT.md#issue-2-out-of-memory-oom)
3. **Slow inference**: [RUNPOD_DEPLOYMENT.md#issue-3-slow-inference](RUNPOD_DEPLOYMENT.md#issue-3-slow-inference)
4. **Connection issues**: [RUNPOD_DEPLOYMENT.md#issue-4-connection-refused--502-errors](RUNPOD_DEPLOYMENT.md#issue-4-connection-refused--502-errors)

---

## Success Criteria

Your deployment is successful when:

✅ Health check returns `{"status": "healthy", "model_loaded": true}`
✅ TTS endpoint generates audio in <5 seconds
✅ Audio quality is clear and natural
✅ Server handles multiple requests without crashing
✅ Costs are within expected range
✅ Uptime meets your requirements

---

**Deployment Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Production

**Notes:**
```
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
```

