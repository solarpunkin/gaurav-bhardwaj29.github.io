// Blog upvote widget for frontend-only blog posts
// Place this in a file like blog-upvote.js and include it on your blog post pages
// Requires Cloudflare Turnstile and Cloudflare Analytics
(function() {
  // Replace with your blog post's unique slug or identifier
  var slug = window.BLOG_POST_SLUG || (window.location.pathname.split('/').filter(Boolean).pop() || 'blog');
  var upvotedKey = 'blog_upvoted_' + slug;
  var sessionKey = 'cf_upvote_verified';

  function isSessionVerified() {
    return localStorage.getItem(sessionKey) === '1';
  }
  function setSessionVerified() {
    localStorage.setItem(sessionKey, '1');
  }
  function isUpvoted() {
    return localStorage.getItem(upvotedKey) === '1';
  }
  function setUpvoted() {
    localStorage.setItem(upvotedKey, '1');
    upvoteBtn.classList.add('upvoted');
    upvoteBtn.style.transform = 'scale(1.2)';
    setTimeout(() => upvoteBtn.style.transform = '', 120);
  }
  if (isUpvoted()) {
    upvoteBtn.classList.add('upvoted');
    upvoteBtn.disabled = true;
  }

  // Create upvote button
  var upvoteBtn = document.createElement('button');
  upvoteBtn.className = 'upvote-btn';
  upvoteBtn.title = 'Upvote this blog';
  upvoteBtn.innerHTML = '<svg class="upvote-arrow" viewBox="0 0 24 24" fill="none" stroke="#ff4500" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12,4 19,20 5,20"/></svg>';
  upvoteBtn.style.marginLeft = '0.5em';
  if (isUpvoted()) {
    upvoteBtn.classList.add('upvoted');
    upvoteBtn.disabled = true;
  }

  // Create share button
  var shareBtn = document.createElement('button');
  shareBtn.className = 'share-btn';
  shareBtn.title = 'Share this blog';
  shareBtn.innerHTML = '<svg class="share-icon" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>';

  // Insert upvote and share buttons after blog title (h1)
  var h1 = document.querySelector('h1');
  if (h1) {
    h1.parentNode.insertBefore(upvoteBtn, h1.nextSibling);
    h1.parentNode.insertBefore(shareBtn, upvoteBtn.nextSibling);
  }

  // Create Turnstile container
  var turnstileContainer = document.createElement('div');
  turnstileContainer.id = 'turnstile-container';
  turnstileContainer.style.display = 'none';
  turnstileContainer.innerHTML = '<div id="cf-turnstile" class="cf-turnstile" data-sitekey="0x4AAAAAABiDRLV2JxUJ_Qv6"></div>';
  document.body.appendChild(turnstileContainer);

  upvoteBtn.addEventListener('click', function() {
    if (isUpvoted()) return;
    upvoteBtn.classList.add('upvoted');
    upvoteBtn.style.transform = 'scale(1.2)';
    setTimeout(() => upvoteBtn.style.transform = '', 120);
    if (isSessionVerified()) {
      setUpvoted();
      upvoteBtn.disabled = true;
      if (window.cfAnalytics && window.cfAnalytics.trackEvent) {
        window.cfAnalytics.trackEvent('upvote', {slug: slug, type: 'blog'});
      }
    } else {
      turnstileContainer.style.display = 'block';
    }
  });

  shareBtn.addEventListener('click', function() {
    if (navigator.share) {
      navigator.share({
        title: document.title,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      shareBtn.classList.add('shared');
      shareBtn.title = 'Copied!';
      setTimeout(() => { shareBtn.classList.remove('shared'); shareBtn.title = 'Share this blog'; }, 1200);
    }
  });

  window.turnstileCallback = function(token) {
    // No backend, just set session and upvoted
    setSessionVerified();
    setUpvoted();
    upvoteBtn.disabled = true;
    if (window.cfAnalytics && window.cfAnalytics.trackEvent) {
      window.cfAnalytics.trackEvent('upvote', {slug: slug, type: 'blog'});
    }
    turnstileContainer.style.display = 'none';
  };

  window.onloadTurnstile = function() {
    if (window.turnstile) {
      window.turnstile.render('#cf-turnstile', {
        sitekey: '0x4AAAAAABiDRLV2JxUJ_Qv6',
        callback: window.turnstileCallback
      });
    }
  };
  document.addEventListener('DOMContentLoaded', function() {
    if (window.turnstile) window.onloadTurnstile();
  });

  // Add minimal CSS for upvote and share button
  var style = document.createElement('style');
  style.textContent = '.upvote-btn{display:inline-flex;align-items:center;cursor:pointer;border:none;background:none;padding:0.2em 0.4em;margin-left:0.5em;transition:color 0.2s,transform 0.1s;color:#aaa;font-size:1.5em;}.upvote-btn.upvoted{color:#ff4500;font-weight:bold;transform:scale(1.2);}.upvote-arrow{width:1.2em;height:1.2em;display:inline-block;vertical-align:middle;transition:stroke 0.2s;}.upvote-btn.upvoted .upvote-arrow{stroke:#ff4500;}.share-btn{display:inline-flex;align-items:center;cursor:pointer;border:none;background:none;padding:0.2em 0.4em;margin-left:0.2em;color:#555;font-size:1.3em;transition:color 0.2s;}.share-btn.shared,.share-btn:hover .share-icon{stroke:#2563eb;color:#2563eb;}.share-icon{width:1.1em;height:1.1em;display:inline-block;vertical-align:middle;transition:stroke 0.2s;}#turnstile-container{margin-top:1em;}';
  document.head.appendChild(style);

  // Load Turnstile script if not present
  if (!document.querySelector('script[src*="turnstile"]')) {
    var s = document.createElement('script');
    s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
    s.async = true;
    s.defer = true;
    document.head.appendChild(s);
  }
})();
