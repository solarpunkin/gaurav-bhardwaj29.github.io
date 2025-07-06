---
title: "Integrating TLS via mbedTLS in web server"
tags: [TLS, C]
slug: "tls-handshakes"
---

I added TLS support to a web server I’m building. The idea was to serve both static and dynamic content securely — no reverse proxies, no bloated frameworks. Just raw HTTP(S), and optional TLS. I chose `mbedTLS` because it’s portable, open source, and suitable for zero-dependency systems. I did not bother to chose `openssl` as it would overkill for my lightweight server.

Initially, I tried wiring in `mbedtls_ssl_conf_rng()`, as almost all examples suggested. It failed. After digging through the migration guide, I realized that mbedTLS 4.0+ dropped this function entirely in favor of internal PSA crypto. So I dropped the legacy logic and focused on initializing TLS, cleaning deprecated APIs.

In the actual server setup, this is how I gated TLS setup logic:

```c
#ifdef USE_TLS
if (tls) {
    psa_crypto_init();

    mbedtls_ssl_init(&ssl);
    mbedtls_ssl_config_init(&conf);
    mbedtls_x509_crt_init(&srvcert);
    mbedtls_pk_init(&pkey);

    mbedtls_x509_crt_parse_file(&srvcert, tls_cert_path);
    mbedtls_pk_parse_keyfile(&pkey, tls_key_path, NULL);

    mbedtls_ssl_config_defaults(&conf,
        MBEDTLS_SSL_IS_SERVER,
        MBEDTLS_SSL_TRANSPORT_STREAM,
        MBEDTLS_SSL_PRESET_DEFAULT);

    mbedtls_ssl_conf_ca_chain(&conf, srvcert.next, NULL);
    mbedtls_ssl_conf_own_cert(&conf, &srvcert, &pkey);
    mbedtls_ssl_setup(&ssl, &conf);
}
#endif

Fallback to HTTP works via `--dev` or when certs are not supplied. Devs can toggle TLS with `--tls --cert cert.pem --key key.pem`. It is platform-agnostic and uses no system daemon.

This TLS handshake now works directly over port 443 or any specified port, and can handle browser connections.