---
title: "GitHub Actions for Automating My TIL"
tags: [github, markdown]
slug: "github-actions-til"
---
Today I learned about GitHub Actions for automating TILs on my blog. My stack is simple(HTML&CSS): I append a markdown file to my GitHub repository, and a GitHub Action formats it into a static page on my TIL site. Yes, I push one `.md` file per TIL.

Previously, I only used GitHub’s UI-based deploys, but for this, I wrote a `.yaml` file—surprisingly similar to a Dockerfile in how declarative it felt. The page loads fast, as I dump the images and GIFs in free B2 buckets on Backblaze. I’ve added a search feature to filter out the TIL list by name and keyword(as I plan to write many more).

The motivation behind this? I've recently grown into the habit of writing down something I’ve just learned, big or small, even if it doesn’t seem interesting to anyone else. That said, it should aslo be worth writing for, not just for the sake of habit. Iwant to be more productive with my life and how I value time now, since I have graduated and have time at disposal. That, and stumbling onto [Simon Willison’](https://simonwillison.net/2024/Dec/22/link-blog/#trying-to-add-something-extra) thoughts on “what to write in a blog post.” It really resonated. He reminded me that it’s okay, more than okay, to write things that seem obvious, or unpolished, as long as they are new and intriguing to you.

Writing a TIL resets that mental buffer,like clearing context from chat_history [] on a daily basis lul. It grounds me. It makes space.. It sits somewhere between a full-length blog and a tweet. Everything seems easier when looking in retrospect—like, *of course that idea was obvious*. But I want my TILs to reflect that moment of intrigue, even if they’re flawed.

I feel like I’ll never stop writing them now. So if you’re reading this, [Simon](https://x.com/simonw), thank you for adding that half-measure of madness and meaning. Your words helped me appreciate the value in what I learn, and to write what I love.
