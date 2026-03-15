# Lumifren Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Active support  |
| < 1.0   | ❌ No support      |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: [security@lumifren.dev] (update with real email)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (if you have them)

You should receive a response within 48 hours. If the issue is confirmed, we will:
1. Work on a fix privately
2. Release a patch
3. Credit you in the release notes (unless you prefer anonymity)

## Security Best Practices for Users

1. **Never commit `.env` files** - Keep your API keys secret
2. **Use HTTPS** - Always use Cloudflare tunnel or proper SSL for remote access
3. **Firewall your Redis** - Don't expose Redis to the internet
4. **Keep updated** - Pull latest security patches regularly
5. **Review permissions** - Only grant necessary access to your Tailscale network

## Scope

Security issues we care about:
- Authentication bypasses
- API key exposure
- XSS/CSRF vulnerabilities
- SQL/NoSQL injection
- Unauthorized data access

Out of scope:
- Self-inflicted issues from misconfiguration
- Denial of service (we're self-hosted, you'd DoS yourself)
- Social engineering

Thank you for helping keep Lumifren secure! 🔒
