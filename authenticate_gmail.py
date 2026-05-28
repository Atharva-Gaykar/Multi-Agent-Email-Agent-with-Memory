# import os
# from google_auth_oauthlib.flow import InstalledAppFlow

# # Gmail API scope
# SCOPES = [
#     "https://mail.google.com/"
# ]

# def run_authentication():
#     print("Starting Google OAuth Authentication Flow...")

#     if not os.path.exists("credentials.json"):
#         print("ERROR: Please place your 'credentials.json' file in this folder first!")
#         return

#     flow = InstalledAppFlow.from_client_secrets_file(
#         "credentials.json",
#         SCOPES
#     )

#     creds = flow.run_local_server(port=8080)

#     with open("token.json", "w") as token_file:
#         token_file.write(creds.to_json())

#     print("\nSUCCESS: 'token.json' has been created successfully!")

# if __name__ == "__main__":
#     run_authentication()