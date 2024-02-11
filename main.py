import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Set your Google Drive API credentials file path
credentials_file = 'bv100-407013-d4483d590203.json'

# Set the file to be uploaded
file_to_upload = 'Matched.txt'

# Set the destination folder ID in Google Drive
folder_id = '1eOYLs6g5GAXvx1zX5JFuK133MtRJdESR'


def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service


def upload_file(service, file_path, folder_id):
    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, resumable=True)

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    request = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f'Uploaded {int(status.progress() * 100)}%')

    print(f'File {file_name} uploaded successfully!')


def delete_all_files_in_folder(service, folder_id):
    try:
        # List files in the folder
        files = service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name)"
        ).execute()

        if 'files' in files:
            for file in files['files']:
                file_id = file['id']
                file_name = file['name']

                # Delete each file
                service.files().delete(fileId=file_id).execute()

                print(f'File "{file_name}" with ID {file_id} deleted successfully!')
        else:
            print('No files found in the folder.')
    except Exception as e:
        print(f'Error deleting files: {str(e)}')


if __name__ == '__main__':
    drive_service = get_drive_service()
    delete_all_files_in_folder(drive_service, folder_id)
    time.sleep(2)
    upload_file(drive_service, file_to_upload, folder_id)

