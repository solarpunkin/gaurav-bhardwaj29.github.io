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
  }

  // Create upvote button
  var upvoteBtn = document.createElement('button');
  upvoteBtn.className = 'upvote-btn';
  upvoteBtn.title = 'Upvote this blog';
  upvoteBtn.innerHTML = '<svg class="upvote-arrow" viewBox="0 0 20 20"><polygon points="10,3 17,15 3,15"/></svg>';
  upvoteBtn.style.marginLeft = '0.5em';
  if (isUpvoted()) {
    upvoteBtn.classList.add('upvoted');
    upvoteBtn.disabled = true;
  }

  // Insert upvote button after blog title (h1)
  var h1 = document.querySelector('h1');
  if (h1) h1.parentNode.insertBefore(upvoteBtn, h1.nextSibling);

  // Create Turnstile container
  var turnstileContainer = document.createElement('div');
  turnstileContainer.id = 'turnstile-container';
  turnstileContainer.style.display = 'none';
  turnstileContainer.innerHTML = '<div id="cf-turnstile" class="cf-turnstile" data-sitekey="0x4AAAAAABiDRLV2JxUJ_Qv6"></div>';
  document.body.appendChild(turnstileContainer);

  upvoteBtn.addEventListener('click', function() {
    if (isUpvoted()) return;
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

  // Add minimal CSS for upvote button
  var style = document.createElement('style');
  style.textContent = '.upvote-btn{display:inline-flex;align-items:center;cursor:pointer;border:none;background:none;padding:0.2em 0.4em;margin-left:0.5em;transition:color 0.2s;color:#aaa;font-size:1.2em;}.upvote-btn.upvoted{color:#222;font-weight:bold;}.upvote-arrow{width:1em;height:1em;display:inline-block;vertical-align:middle;}#turnstile-container{margin-top:1em;}';
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
