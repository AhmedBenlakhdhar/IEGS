import subprocess
import hmac
import hashlib
import json
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt # Disable CSRF protection for this view (webhook comes from GitHub)
@require_POST # Only allow POST requests
def github_webhook(request):
    """
    Handles incoming GitHub webhooks to trigger a git pull.
    """
    # 1. Verify the signature
    signature_header = request.headers.get('X-Hub-Signature-256')
    if not signature_header:
        print("WARN: Webhook view received request without X-Hub-Signature-256 header.")
        return HttpResponseForbidden('Permission denied. Missing signature.')

    sha_name, signature = signature_header.split('=', 1)
    if sha_name != 'sha256':
        print(f"WARN: Webhook view received unsupported signature type: {sha_name}")
        return HttpResponseServerError('Unsupported signature type.', status=501)

    # Calculate the expected signature
    try:
        secret_bytes = settings.GITHUB_WEBHOOK_SECRET.encode('utf-8')
        mac = hmac.new(secret_bytes, msg=request.body, digestmod=hashlib.sha256)
        expected_signature = mac.hexdigest()
    except AttributeError:
         print("ERROR: GITHUB_WEBHOOK_SECRET not configured in settings.py")
         return HttpResponseServerError('Server configuration error.', status=500)
    except Exception as e:
         print(f"ERROR: Error calculating HMAC: {e}")
         return HttpResponseServerError('Server configuration error.', status=500)


    if not hmac.compare_digest(signature, expected_signature):
        print(f"WARN: Invalid signature received. Expected={expected_signature}, Got={signature}")
        return HttpResponseForbidden('Permission denied. Invalid signature.')

    # 2. Optionally check the event and branch
    try:
        payload = json.loads(request.body)
        ref = payload.get('ref', '')
        # --- ADJUST BRANCH NAME IF NEEDED ---
        expected_ref = 'refs/heads/main'
        # ------------------------------------
        if ref != expected_ref:
            print(f"INFO: Push ignored. Ref '{ref}' is not '{expected_ref}'.")
            return HttpResponse(f"Push ignored (not {expected_ref} branch)")
    except json.JSONDecodeError:
        print("WARN: Could not decode JSON payload from GitHub.")
        return HttpResponseServerError("Invalid payload format", status=400)
    except Exception as e:
         print(f"ERROR: Error processing payload: {e}")
         return HttpResponseServerError('Error processing payload.', status=500)

    # 3. If signature is valid and branch matches, pull the code
    try:
        repo_path = settings.REPO_PATH
        print(f"INFO: Signature verified for {ref}. Pulling code in {repo_path}...")

        # Ensure the REPO_PATH exists
        if not os.path.isdir(repo_path):
             print(f"ERROR: Repository path does not exist: {repo_path}")
             return HttpResponseServerError('Server configuration error: Repo path invalid.', status=500)

        # Run git pull using subprocess
        result = subprocess.run(
            ['git', '-C', repo_path, 'pull'],
            capture_output=True, text=True, check=True, timeout=60 # Add timeout
        )
        print(f"INFO: Git pull successful. Output:\n{result.stdout}")

        # Optional: Touch the WSGI file to force reload (adjust path if needed)
        # username = os.environ.get('PA_USER', 'your_pythonanywhere_username') # Best get username reliably
        # wsgi_file_path = f'/var/www/{username}_pythonanywhere_com_wsgi.py'
        # try:
        #     if os.path.exists(wsgi_file_path):
        #         subprocess.run(['touch', wsgi_file_path], check=True)
        #         print(f"INFO: Touched WSGI file: {wsgi_file_path}")
        #     else:
        #          print(f"WARN: WSGI file not found at expected path: {wsgi_file_path}")
        # except Exception as e:
        #     print(f"ERROR: Failed to touch WSGI file: {e}")

        return HttpResponse('Update successful')

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git pull failed. Return code: {e.returncode}\nStderr:\n{e.stderr}\nStdout:\n{e.stdout}")
        return HttpResponseServerError(f'Update script failed:\n{e.stderr}', status=500)
    except subprocess.TimeoutExpired:
        print(f"ERROR: Git pull timed out after 60 seconds.")
        return HttpResponseServerError('Update script timed out.', status=500)
    except FileNotFoundError:
         print("ERROR: 'git' command not found. Is git installed and in PATH?")
         return HttpResponseServerError('Server configuration error: git command not found.', status=500)
    except Exception as e:
         print(f"ERROR: An unexpected error occurred during git pull: {e}")
         return HttpResponseServerError(f'An unexpected error occurred: {e}', status=500)