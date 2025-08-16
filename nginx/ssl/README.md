# SSL Certificates

Place your SSL certificates in this directory:

- certificate.crt (or .pem)
- private.key
- ca_bundle.crt (if required)

For Let's Encrypt certificates:
- fullchain.pem
- privkey.pem

Make sure to update nginx configuration to use the correct certificate paths.
