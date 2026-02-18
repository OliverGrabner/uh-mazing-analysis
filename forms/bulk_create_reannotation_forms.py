"""Create Google Forms for disfluency reannotation tasks."""
# python3 forms/bulk_create_reannotation_forms.py

import json
import pandas as pd
import os
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ------------------------------------------------------------
# 1. AUTHENTICATION
# ------------------------------------------------------------
load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive"
]


def authorize():
    creds = None
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    except Exception:
        pass

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "./forms/credentials.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0, open_browser=False)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


# ------------------------------------------------------------
# 2. GOOGLE FORMS HELPERS
# ------------------------------------------------------------

def create_form(forms_service, title):
    result = forms_service.forms().create(
        body={"info": {"title": title}}
    ).execute()
    return result["formId"]


def set_description(forms_service, form_id, description_text):
    forms_service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": [
                {
                    "updateFormInfo": {
                        "info": {"description": description_text},
                        "updateMask": "description"
                    }
                }
            ]
        }
    ).execute()


def add_items(forms_service, form_id, items):
    requests = []
    for idx, item in enumerate(items):
        requests.append({
            "createItem": {
                "item": item,
                "location": {"index": idx}
            }
        })

    forms_service.forms().batchUpdate(
        formId=form_id,
        body={"requests": requests}
    ).execute()


def move_to_folder(drive_service, file_id, folder_id):
    file = drive_service.files().get(
        fileId=file_id,
        fields="parents"
    ).execute()

    prev_parents = ",".join(file.get("parents", []))

    drive_service.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=prev_parents,
        fields="id, parents"
    ).execute()


# ------------------------------------------------------------
# 3. LOAD BASE FORM TEMPLATE
# ------------------------------------------------------------

def load_base_form(json_path="./forms/base_reannotation_form.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# 4. LANGUAGE CONFIGURATION
# ------------------------------------------------------------

LANGUAGES = {
    "ZH": "Mandarin",
    "ES": "Spanish",
    "HI": "Hindi",
    "FR": "French",
    "DE": "German",
    "IT": "Italian",
    "CS": "Czech",
    "AR": "Arabic",
}


# ------------------------------------------------------------
# 5. REANNOTATION ITEM BUILDER
# ------------------------------------------------------------

def make_reannotation_item(en_text, lang_text, item_number, target_language, ID):
    return {
        "title": f"[{ID}] Annotation {item_number}",
        "description": (
            f"English (reference — notice the _underscore_ markers):\n"
            f"{en_text}\n\n"
            f"---\n\n"
            f"{target_language} text (copy this into the box below and add _ markers):\n"
            f"{lang_text}"
        ),
        "questionItem": {
            "question": {
                "required": True,
                "textQuestion": {
                    "paragraph": True
                }
            }
        }
    }


# ------------------------------------------------------------
# 6. BULK CREATION PIPELINE
# ------------------------------------------------------------

def bulk_create_reannotation(
    forms_service,
    drive_service=None,
    folder_id=None,
):
    results = []
    item_mappings = []

    base_form = load_base_form()
    df = pd.read_csv("./outputs/results/reannotation_targets.csv")

    for lang_code, lang_name in LANGUAGES.items():
        lang_df = df[df["Language"] == lang_code]

        if lang_df.empty:
            continue

        # Only split if 30+ items, then split into two roughly equal halves
        if len(lang_df) > 30:
            mid = len(lang_df) // 2
            chunks = [lang_df.iloc[:mid], lang_df.iloc[mid:]]
        else:
            chunks = [lang_df]

        print(f"\n=== Creating reannotation forms for {lang_name} ({lang_code}) — {len(lang_df)} items ===")

        for form_idx, chunk in enumerate(chunks, start=1):
            UID = f"{lang_code}_R{form_idx}"
            title = f"Reannotation Task – {lang_name} (Part {form_idx})"

            google_description = (
                base_form["description"]["google"]
                .replace("[TARGET_LANGUAGE]", lang_name)
            )

            prolific_description = (
                base_form["description"]["prolific"]
                .replace("[TARGET_LANGUAGE]", lang_name)
            )

            items = []
            items.append({
                "title": "Provide your Prolific ID in the box below.",
                "questionItem": {
                    "question": {
                        "required": False,
                        "textQuestion": {}
                    }
                }
            })

            for q_num, (row_idx, row) in enumerate(chunk.iterrows(), start=1):
                items.append(
                    make_reannotation_item(
                        row["EN_disfluent"],
                        row["Text"],
                        q_num,
                        lang_name,
                        row["ID"]
                    )
                )

                item_mappings.append({
                    "language_code": lang_code,
                    "language_name": lang_name,
                    "form_uid": UID,
                    "form_id": None,
                    "form_part": form_idx,
                    "question_number": q_num,
                    "source_id": row["ID"],
                    "reason": row["Reason"]
                })

            items.append({
                "title": "Completion Code",
                "description": (
                    "Paste the following completion code when you return to Prolific: COMPLETED021384. Thanks!\n"
                ),
                "questionItem": {
                    "question": {
                        "required": False,
                        "textQuestion": {
                            "paragraph": True
                        }
                    }
                }
            })

            # CREATE FORM
            form_id = create_form(forms_service, title)
            set_description(forms_service, form_id, google_description)
            add_items(forms_service, form_id, items)

            participant_url = f"https://docs.google.com/forms/d/{form_id}/viewform"

            for m in item_mappings:
                if m["form_uid"] == UID and m["form_id"] is None:
                    m["form_id"] = form_id

            results.append(
                (form_id, UID, lang_code, participant_url, prolific_description)
            )

            print(f"[OK] {UID} | {form_id}")

            if folder_id:
                move_to_folder(drive_service, form_id, folder_id)

    return results, item_mappings


# ------------------------------------------------------------
# 7. MAIN ENTRY POINT
# ------------------------------------------------------------

if __name__ == "__main__":
    creds = authorize()
    forms_service = build("forms", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

    results, item_mappings = bulk_create_reannotation(
        forms_service,
        drive_service,
        DRIVE_FOLDER_ID,
    )

    print("\nDONE — Reannotation Forms Created\n")

    with open("./data/reannotation_forms.txt", "w", encoding="utf-8") as f:
        for form_id, UID, lang_code, participant_url, description in results:
            safe_description = description.replace("\n", "\\n")
            line = (
                f"{UID} | {lang_code} | {form_id} | "
                f"{participant_url} | {safe_description}\n"
            )
            print(line.strip())
            f.write(line)

    mapping_df = pd.DataFrame(item_mappings)
    mapping_df.to_csv(
        "./data/reannotation_form_mapping.csv",
        index=False,
        encoding="utf-8"
    )

    print("\nSaved reannotation_forms.txt")
    print("Saved reannotation_form_mapping.csv\n")
