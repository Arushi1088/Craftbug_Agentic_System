# ado_sync_service.py
import os, requests, json, logging, os.path as p
from datetime import datetime

log = logging.getLogger("ado_sync_service")
log.setLevel(logging.INFO)

ORG = os.getenv("ADO_ORGANIZATION")
PROJ = os.getenv("ADO_PROJECT") 
PAT  = os.getenv("ADO_PAT")

API = f"https://dev.azure.com/{ORG}/{PROJ}/_apis"
APIV = "7.0"

def _auth():
    if not (ORG and PROJ and PAT):
        raise RuntimeError("ADO credentials not configured. Set ADO_* in .env")
    return ("", PAT)  # PAT in password slot for basic auth

def create_bug(title:str, html_description:str, analysis_id:str, module:str, app_type:str):
    url = f"{API}/wit/workitems/$Bug?api-version={APIV}"
    payload = [
        {"op":"add","path":"/fields/System.Title","value": title},
        {"op":"add","path":"/fields/System.Description","value": html_description},
        {"op":"add","path":"/fields/Analyzer.AnalysisId","value": analysis_id},
        {"op":"add","path":"/fields/Analyzer.Module","value": module or "unknown"},
        {"op":"add","path":"/fields/Analyzer.AppType","value": app_type or "unknown"},
    ]
    r = requests.post(url, auth=_auth(),
        headers={"Content-Type":"application/json-patch+json"},
        json=payload, timeout=30)
    r.raise_for_status()
    wi = r.json()
    return {"id": wi["id"], "url": wi["url"]}

def attach_screenshot(work_item_id:int, screenshot_path:str):
    # 1) upload attachment
    filename = p.basename(screenshot_path)
    with open(screenshot_path, "rb") as f:
        content = f.read()
    up_url = f"{API}/wit/attachments?fileName={filename}&api-version={APIV}"
    up = requests.post(up_url, auth=_auth(),
        headers={"Content-Type":"application/octet-stream"},
        data=content, timeout=60)
    up.raise_for_status()
    att = up.json()["url"]

    # 2) add relation
    patch = [{"op":"add","path":"/relations/-","value":{"rel":"AttachedFile","url":att}}]
    wi_url = f"{API}/wit/workitems/{work_item_id}?api-version={APIV}"
    pr = requests.patch(wi_url, auth=_auth(),
        headers={"Content-Type":"application/json-patch+json"},
        json=patch, timeout=30)
    pr.raise_for_status()
    return True

def set_state(work_item_id:int, state:str, reason:str=""):
    url = f"{API}/wit/workitems/{work_item_id}?api-version={APIV}"
    patch = [{"op":"add","path":"/fields/System.State","value": state}]
    if reason:
        patch.append({"op":"add","path":"/fields/System.Reason","value": reason})
    r = requests.patch(url, auth=_auth(),
        headers={"Content-Type":"application/json-patch+json"}, json=patch, timeout=20)
    r.raise_for_status()
    return True

def add_history(work_item_id:int, text:str):
    url = f"{API}/wit/workitems/{work_item_id}?api-version={APIV}"
    patch = [{"op":"add","path":"/fields/System.History","value": text}]
    r = requests.patch(url, auth=_auth(),
        headers={"Content-Type":"application/json-patch+json"}, json=patch, timeout=20)
    r.raise_for_status()
    return True

def open_url(work_item_id:int):
    return f"https://dev.azure.com/{ORG}/{PROJ}/_workitems/edit/{work_item_id}"


# Legacy compatibility wrapper class
class ADOSyncService:
    def __init__(self):
        self.organization = ORG
        self.project = PROJ
        self.personal_access_token = PAT

    def validate_credentials(self):
        return bool(ORG and PROJ and PAT)

    def create_work_item(self, title, description, analysis_id, module="", app_type=""):
        try:
            result = create_bug(title, description, analysis_id, module, app_type)
            return {
                "success": True,
                "work_item_id": result["id"],
                "work_item_url": result["url"]
            }
        except Exception as e:
            log.error(f"Failed to create work item: {e}")
            return {"success": False, "error": str(e)}

    def attach_screenshot(self, work_item_id, screenshot_path):
        try:
            attach_screenshot(work_item_id, screenshot_path)
            return {"success": True}
        except Exception as e:
            log.error(f"Failed to attach screenshot: {e}")
            return {"success": False, "error": str(e)}

# Initialize service instance for backward compatibility
ado_service = ADOSyncService()
