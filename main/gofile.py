import requests

async def gofile_upload(file_path, new_name):
    # Upload to GoFile
    upload_url = "https://store1.gofile.io/uploadFile"
    
    with open(file_path, 'rb') as f:
        response = requests.post(upload_url, files={'file': f})
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'ok':
            download_url = data.get('data', {}).get('downloadPage')
            return download_url
        else:
            return "GoFile upload failed."
    else:
        return "Error during GoFile upload."
