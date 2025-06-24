# Cloudflare Pages Function for TIL upvotes with Turnstile verification
# Place this file at /functions/api/upvote.py in your repo
import os
import json
import httpx

def get_user_id(request):
    # Use a combination of IP and User-Agent as a weak fingerprint (not perfect)
    ip = request.headers.get('cf-connecting-ip') or request.headers.get('x-forwarded-for', '')
    ua = request.headers.get('user-agent', '')
    return f"{ip}:{ua}"

async def on_request(request):
    if request.method != 'POST':
        return Response(
            json.dumps({'success': False, 'error': 'POST required'}),
            status=405,
            headers={'content-type': 'application/json'}
        )
    try:
        data = await request.json()
    except Exception:
        return Response(
            json.dumps({'success': False, 'error': 'Invalid JSON'}),
            status=400,
            headers={'content-type': 'application/json'}
        )
    slug = data.get('slug')
    token = data.get('token')
    user_id = get_user_id(request)
    if not slug:
        return Response(
            json.dumps({'success': False, 'error': 'Missing slug'}),
            status=400,
            headers={'content-type': 'application/json'}
        )
    # Use D1 to check for existing upvote
    db = request.ctx.env.COUNT
    row = await db.prepare("SELECT 1 FROM upvotes WHERE user_id = ? AND slug = ?").bind(user_id, slug).first()
    if row:
        return Response(
            json.dumps({'success': True, 'already_upvoted': True}),
            headers={'content-type': 'application/json'}
        )
    # If not session-verified, require Turnstile token
    cookies = request.cookies
    if not cookies.get('cf_upvote_verified'):
        if not token:
            return Response(
                json.dumps({'success': False, 'error': 'Verification required'}),
                status=400,
                headers={'content-type': 'application/json'}
            )
        # Verify Turnstile token
        TURNSTILE_SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY', 'YOUR_TURNSTILE_SECRET_KEY')
        async with httpx.AsyncClient() as client:
            resp = await client.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data={
                'secret': TURNSTILE_SECRET_KEY,
                'response': token,
                'remoteip': request.headers.get('cf-connecting-ip', '')
            })
            result = resp.json()
        if not result.get('success'):
            return Response(
                json.dumps({'success': False, 'error': 'Turnstile failed'}),
                status=403,
                headers={'content-type': 'application/json'}
            )
    # Insert upvote into D1
    await db.prepare("INSERT INTO upvotes (user_id, slug) VALUES (?, ?)").bind(user_id, slug).run()
    # Set session cookie for global upvote session
    resp = Response(json.dumps({'success': True}), headers={'content-type': 'application/json'})
    resp.set_cookie('cf_upvote_verified', '1', max_age=60*60*24*30, samesite='Lax')
    return resp

# Cloudflare Pages Functions expects an 'on_request' async function
