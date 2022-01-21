import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Create new Google Drive object, create local webserver and authenticate
google_auth = GoogleAuth()
google_auth.LocalWebserverAuth()


def update_google_file(data: str, ctx):
    """
    Updates the text file with the same name as the current date, logging all
    discord commands and outputs to the file.
    :param data: The data to be written to the file.
    :param ctx: The context of the command.
    :return: None
    """
    # Get Google Drive
    drive = GoogleDrive(google_auth)

    # Get current date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = current_date + ".txt"

    # Get current time and format
    current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    section = f'[{current_date_time}] ({ctx.author.name}): ' \
              f'{ctx.message.content}\n'

    # Check if file exists
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).\
        GetList()

    for file1 in file_list:
        if file1['title'] == file_name:
            updated = file1.GetContentString() + section + data + '\n'
            file1.SetContentString(updated)
            file1.Upload()
            return

    # Create new file
    file = drive.CreateFile({'title': file_name})
    file.SetContentString(section + data + '\n')
    file.Upload()
