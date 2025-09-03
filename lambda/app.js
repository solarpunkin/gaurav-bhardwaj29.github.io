document.addEventListener('DOMContentLoaded', () => {
    const CLIENT_ID = 'b1f10cffb95d45ada07f921e7322310d'; // IMPORTANT: Replace with your Spotify Client ID
    const REDIRECT_URI = window.location.origin + '/lambda/';

    const overlayContainer = document.getElementById('spotify-overlay-container');
    let accessToken = localStorage.getItem('spotify_access_token');
    const refreshToken = localStorage.getItem('spotify_refresh_token');
    const tokenExpiresAt = localStorage.getItem('spotify_token_expires_at');

    const api = {
        auth: 'https://accounts.spotify.com',
        base: 'https://api.spotify.com/v1',
    };

    // Main function to initialize the overlay
    async function init() {
        console.log('Initializing Spotify Overlay');
        const params = new URLSearchParams(window.location.search);
        if (params.has('code')) {
            console.log('Found authorization code. Handling redirect.');
            await handleRedirect();
        }

        if (isTokenExpired()) {
            console.log('Access token expired. Refreshing...');
            await refreshAccessToken();
        }

        if (accessToken) {
            console.log('Access token found. Updating overlay.');
            updateOverlay();
            setInterval(updateOverlay, 5000); // Refresh every 5 seconds
        } else {
            console.log('No access token. Rendering login.');
            renderLogin();
        }
    }

    // Handle the redirect from Spotify's authorization page
    async function handleRedirect() {
        const code = new URLSearchParams(window.location.search).get('code');
        const codeVerifier = localStorage.getItem('spotify_code_verifier');

        try {
            const response = await fetch(`${api.auth}/api/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    client_id: CLIENT_ID,
                    grant_type: 'authorization_code',
                    code,
                    redirect_uri: REDIRECT_URI,
                    code_verifier: codeVerifier,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            storeTokens(data);
            window.history.pushState({}, '', REDIRECT_URI); // Clean up URL
        } catch (error) {
            console.error('Error fetching access token:', error);
            renderLogin();
        }
    }

    // Redirect user to Spotify to log in
    async function login() {
        const codeVerifier = generateRandomString(64);
        const codeChallenge = await generateCodeChallenge(codeVerifier);
        localStorage.setItem('spotify_code_verifier', codeVerifier);

        const params = new URLSearchParams({
            client_id: CLIENT_ID,
            response_type: 'code',
            redirect_uri: REDIRECT_URI,
            scope: 'user-read-playback-state user-read-currently-playing',
            code_challenge_method: 'S256',
            code_challenge: codeChallenge,
        });

        window.location.href = `${api.auth}/authorize?${params}`;
    }

    // Fetch currently playing data from Spotify API
    async function getPlaybackState() {
        if (!accessToken) return null;
        try {
            const response = await fetch(`${api.base}/me/player/currently-playing`, {
                headers: { Authorization: `Bearer ${accessToken}` },
            });
            if (response.status === 401) {
                await refreshAccessToken();
                return getPlaybackState();
            }
            if (response.status === 204) return null; // No content
            return response.json();
        } catch (error) {
            console.error('Error fetching playback state:', error);
            return null;
        }
    }

    // Fetch user's queue
    async function getQueue() {
        if (!accessToken) return null;
        const response = await fetch(`${api.base}/me/player/queue`, {
            headers: { Authorization: `Bearer ${accessToken}` },
        });
        return response.json();
    }

    // Update the overlay with the latest data
    async function updateOverlay() {
        const playback = await getPlaybackState();
        if (!playback || !playback.item) {
            renderNothingPlaying();
            return;
        }

        const queue = await getQueue();
        renderPlayback(playback, queue);
    }

    // Render UI functions
    function renderLogin() {
        overlayContainer.innerHTML = `<div class="spotify-overlay"><button class="spotify-login-btn">Login with Spotify</button></div>`;
        overlayContainer.querySelector('.spotify-login-btn').addEventListener('click', login);
    }

    function renderNothingPlaying() {
        overlayContainer.innerHTML = `<div class="spotify-overlay"><span>Nothing playing right now</span></div>`;
    }

    function renderPlayback(playback, queue) {
        const { item, progress_ms } = playback;
        const artistName = item.artists.map(a => a.name).join(', ');
        const isLongTitle = item.name.length > 30;

        overlayContainer.innerHTML = `
            <div class="spotify-overlay">
                <div class="spotify-playback-info">
                    <img src="${item.album.images[0].url}" class="spotify-album-art" alt="Album Art">
                    <div class="spotify-track-details">
                        <a href="${item.external_urls.spotify}" target="_blank" class="spotify-track-title ${isLongTitle ? 'marquee' : ''}">${item.name}</a>
                        <div class="spotify-track-artist">${artistName}</div>
                    </div>
                </div>
                <div class="spotify-queue">
                    ${queue.queue.slice(0, 2).map(q => `<span class="spotify-queue-item">${q.name}</span>`).join('')}
                </div>
                <div class="spotify-progress-container">
                    <div class="spotify-progress-bar" style="width: ${(progress_ms / item.duration_ms) * 100}%"></div>
                </div>
            </div>
        `;
    }

    // Helper functions for OAuth
    function isTokenExpired() {
        return Date.now() >= (tokenExpiresAt || 0);
    }

    async function refreshAccessToken() {
        if (!refreshToken) return;
        try {
            const response = await fetch(`${api.auth}/api/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    grant_type: 'refresh_token',
                    refresh_token: refreshToken,
                    client_id: CLIENT_ID,
                }),
            });
            const data = await response.json();
            storeTokens(data);
        } catch (error) {
            console.error('Error refreshing token:', error);
            accessToken = null;
        }
    }

    function storeTokens(data) {
        accessToken = data.access_token;
        localStorage.setItem('spotify_access_token', data.access_token);
        if (data.refresh_token) {
            localStorage.setItem('spotify_refresh_token', data.refresh_token);
        }
        localStorage.setItem('spotify_token_expires_at', Date.now() + data.expires_in * 1000);
    }

    function generateRandomString(length) {
        let text = '';
        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (let i = 0; i < length; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }

    async function generateCodeChallenge(codeVerifier) {
        const data = new TextEncoder().encode(codeVerifier);
        const digest = await window.crypto.subtle.digest('SHA-256', data);
        return btoa(String.fromCharCode.apply(null, [...new Uint8Array(digest)]))
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=+$/, '');
    }

    init();
});