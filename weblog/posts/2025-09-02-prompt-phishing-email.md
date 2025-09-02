---
title: "promptbait"
tags: [ai, prompt-injection]
slug: "prompt-phishing-email"
---


Following the recent Perplexity’s AI agentic browser Comet prompt injection attack reported by teams at [Brave](https://brave.com/blog/comet-prompt-injection/) and [Guardio](https://guard.io/labs/scamlexity-we-put-agentic-ai-browsers-to-the-test-they-clicked-they-paid-they-failed), a similar kind of attack [has been identified](https://malwr-analysis.com/2025/08/24/phishing-emails-are-now-aimed-at-users-and-ai-defenses/) but this time it’s Gmail.

<figure style="text-align: center;">
  <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/prompt-phishing-email/Screenshot%202025-09-02%20at%202.22.45%E2%80%AFAM.png" style="max-width: 100%; height: auto;" />
  <figcaption>Password Expiry notice</figcaption>
</figure>

The sender combined **two** same old book tricks:

1. Social engineering to lure the user into updating their password, and 

2. A hidden prompt for the AI agent to evade automated defences and spiral into long reasoning steps instead of labelling it as phishing.

<figure style="text-align: center;">
  <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/prompt-phishing-email/Screenshot%202025-09-02%20at%202.22.27%E2%80%AFAM.png" style="max-width: 100%; height: auto;" />
  <figcaption>Hidden in the plain-text MIME section was this block of text</figcaption>
</figure>

This campaign therefore runs on two tracks simultaneously

- One for users

- One for AI

As AI-powered email filtering and assistance become the norm, phishing campaigns are already adapting. What looks like an old scam in a new inbox may in fact be a carefully designed **AI-aware attack**, with both human and machine targets in mind.

Defending against phishing now means securing three targets at once:

- Users (against social engineering)

- AI tools (against prompt injection)

- Infrastructure (against beaconing and redirect abuse)  

The article by Guardio shows one of the ways in which scammers [can train automated systems using GANs](https://guard.io/labs/scamlexity-we-put-agentic-ai-browsers-to-the-test-they-clicked-they-paid-they-failed) (Generative Adversarial Networks) where one AI generates phishing variants and another AI plays the role of the filter trying to block them. The generator doesn’t stop until it wins.

“The only real answer is to stay several steps ahead of scammers by thinking like one. Instead of training the generator to scam, we must focus on training the discriminator to anticipate, detect, and neutralize these attacks.” – Guardio

<figure style="text-align: center;">
  <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/prompt-phishing-email/gan-for-ai-threat-model.webp" style="max-width: 100%; height: auto;" />
  <figcaption>The diagram above is only a simplified schematic of how automated scam training might look, but it is just the beginning</figcaption>
</figure>