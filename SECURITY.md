# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported |
| ------- | --------- |
| main    | ✅ Active development |
| 3.x     | ✅ Current stable |
| < 3.0   | ❌ End of life |

## Reporting a Vulnerability

**Please do not open public GitHub issues for security vulnerabilities.**

### Preferred Method: GitHub Security Advisory

1. Go to [Security Advisories](https://github.com/LessUp/yolo-toys/security/advisories)
2. Click "Report a vulnerability"
3. Fill in the details (see below)

### Alternative: Private Contact

If GitHub Security Advisories are not available, contact maintainers through private channels.

### What to Include

Please provide:

- **Description** — Clear explanation of the vulnerability
- **Affected versions** — Which versions are impacted
- **Reproduction steps** — Minimal code or commands to reproduce
- **Impact** — What an attacker could achieve
- **Suggested fix** — If you have ideas for mitigation

### Response Timeline

| Stage | Target |
|-------|--------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 7 days |
| Fix development | Depends on severity |
| Patch release | As soon as possible |

We will keep you informed throughout the process.

## Security Best Practices

When deploying YOLO-Toys:

### Input Validation

- The API validates file types and sizes (`MAX_UPLOAD_MB`)
- Only image files are accepted for inference endpoints
- WebSocket frames are size-limited

### Deployment

- Run behind a reverse proxy (nginx, Caddy) in production
- Set appropriate `ALLOW_ORIGINS` for CORS
- Use HTTPS for all public deployments
- Consider rate limiting for public endpoints

### Container Security

- Docker image runs as non-root user
- Multi-stage build minimizes attack surface
- No sensitive data in image layers

### Dependencies

- Keep dependencies updated
- Use `pip-audit` to check for known vulnerabilities:

```bash
pip install pip-audit
pip-audit
```

## Known Security Considerations

### Model Downloads

- YOLO weights are downloaded from Ultralytics on first use
- HuggingFace models are downloaded from HuggingFace Hub
- Ensure network access to trusted sources only

### Resource Limits

- Set `MAX_CONCURRENCY` to prevent resource exhaustion
- Monitor memory usage with large models
- Consider container resource limits in production

## Security Updates

Security patches are released as patch versions. Subscribe to GitHub releases or watch the repository for updates.

---

Thank you for helping keep YOLO-Toys secure! 🔒
