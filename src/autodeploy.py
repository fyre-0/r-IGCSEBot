from quart import Quart, request
import os
import hashlib
import hmac

webhook_handler_app = Quart(__name__)

@webhook_handler_app.post("/github-webhook")
async def github():
    # Requests will be forwarded from a nginx reverse proxy
    if request.remote_addr != "127.0.0.1":
        return {"error": "Invalid IP"}, 403
    
    payload = await request.get_data()
    signature = request.headers.get("X-Hub-Signature-256")
    
    if not signature:
        return {"error": "No signature"}, 403
    hash_object = hmac.new(os.environ['GITHUB_WEBHOOK_SECRET'].encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        return {"error": "Invalid signature"}, 403
    
    event = request.headers["X-GitHub-Event"]
    if event == "push":
        print("New commit, restarting...")
        exit(0)
    
    return {"success": True}