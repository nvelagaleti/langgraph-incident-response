#!/usr/bin/env python3
"""
Update .env file with fresh OAuth token
"""

import os
import re

def update_env_token():
    """Update .env file with fresh OAuth token."""
    print("🔄 Updating .env file with fresh OAuth token...")
    
    # Fresh token from our exchange
    fresh_token = "eyJraWQiOiJhdXRoLmF0bGFzc2lhbi5jb20tQUNDRVNTLTk0ZTczYTkwLTUxYWQtNGFjMS1hOWFjLWU4NGUwNDVjNDU3ZCIsImFsZyI6IlJTMjU2In0.eyJqdGkiOiJmNDIyMzFmMi04ZmRhLTQ2NjgtOGY1NS03YmIyYTc2YjI2MjIiLCJzdWIiOiI3MDEyMTpjZmQxOWQyNy1iNGM1LTQwNTMtYjFkMS02NWRkMTgyYWMyNzgiLCJuYmYiOjE3NTU3NDAxMzIsImlzcyI6Imh0dHBzOi8vYXV0aC5hdGxhc3NpYW4uY29tIiwiaWF0IjoxNzU1NzQwMTMyLCJleHAiOjE3NTU3NDM3MzIsImF1ZCI6IklScFRrU1lScVkyc1BjMkZ4aEhPSkdwaWI0a2xLcFhQIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3Nlc3Npb25faWQiOiI1ZDgzYWNkNy03NzEwLTQ5MWUtOWQwNS05OTQ5NDgzMWQ4NTIiLCJodHRwczovL2F0bGFzc2lhbi5jb20vc3lzdGVtQWNjb3VudEVtYWlsIjoiMTllNTRmOTItODA4OS00Y2JhLWE5MWUtMTkyMTg2MjMxMjUyQGNvbm5lY3QuYXRsYXNzaWFuLmNvbSIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS91anQiOiIzYjQ0MDNlYy0xMDI0LTRmY2MtOTk1NS1kNjYxZTlhZGY0ZTMiLCJodHRwczovL2F0bGFzc2lhbi5jb20vYXV0aFByb2ZpbGUiOiJvYXV0aC5lY29zeXN0ZW0ub2F1dGhJbnRlZ3JhdGlvbiIsImNsaWVudF9pZCI6IklScFRrU1lScVkyc1BjMkZ4aEhPSkdwaWI0a2xLcFhQIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL2F0bF90b2tlbl90eXBlIjoiQUNDRVNTIiwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL2ZpcnN0UGFydHkiOmZhbHNlLCJodHRwczovL2F0bGFzc2lhbi5jb20vdmVyaWZpZWQiOnRydWUsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9wcm9jZXNzUmVnaW9uIjoidXMtd2VzdC0yIiwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL2VtYWlsRG9tYWluIjoiZ21haWwuY29tIiwic2NvcGUiOiJtYW5hZ2U6amlyYS1jb25maWd1cmF0aW9uIG1hbmFnZTpqaXJhLWRhdGEtcHJvdmlkZXIgbWFuYWdlOmppcmEtcHJvamVjdCBtYW5hZ2U6amlyYS13ZWJob29rIHJlYWQ6amlyYS11c2VyIHJlYWQ6amlyYS13b3JrIHdyaXRlOmppcmEtd29yayIsImh0dHBzOi8vYXRsYXNzaWFuLmNvbS8zbG8iOnRydWUsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS92ZXJpZmllZCI6dHJ1ZSwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL3N5c3RlbUFjY291bnRJZCI6IjcxMjAyMDoxYzk3ZGNmNS05YTA1LTQ5YTEtYTliMC1iMTVkMzUxYzhiNTQiLCJodHRwczovL2F0bGFzc2lhbi5jb20vc3lzdGVtQWNjb3VudEVtYWlsRG9tYWluIjoiY29ubmVjdC5hdGxhc3NpYW4uY29tIiwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL29hdXRoQ2xpZW50SWQiOiJJUnBUa1NZUnFZMnNQYzJGeGhIT0pHcGliNGtsS3BYUCJ9.wOegj4rfo3yKLlodajhyaWVw-uiwNL5gAVdgre4epsOzXmUw6_EHfFWhQrHGW_M_fNoDcSkY2ymwZrwkHWWSVu9b9VhL4CaP3QTS8xpXSp9RHr_qBX0IG9AHaYEQk1SPLAxsglf7kzxIShlkooytvadbdt2JN1xwlcOKvw_kr4WAc5Mr4ao7avPCI4gXYcLfHeIhky8I6zNTEtxhG0dh8J39FCjE0LdieuYtXEpc9SEKmbIy3xfGo1gdxsAwNm8Y0eLl79B0eUelBVbHWdXhF3fSU8fSx5qNF7IWnLWdgcBLAHCGfJ9rGmFo3ZoCp0Du6P4Khc8JFlATwjEYb2D-jg"
    
    env_file = ".env"
    
    # Read the current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Find and replace all JIRA_OAUTH_ACCESS_TOKEN lines
    updated_lines = []
    token_updated = False
    
    for line in lines:
        if line.startswith("JIRA_OAUTH_ACCESS_TOKEN="):
            if not token_updated:
                # Keep only the first occurrence and update it
                updated_lines.append(f"JIRA_OAUTH_ACCESS_TOKEN={fresh_token}\n")
                token_updated = True
                print("✅ Updated JIRA_OAUTH_ACCESS_TOKEN")
            # Skip duplicate lines
        else:
            updated_lines.append(line)
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ .env file updated successfully!")
    print(f"🔑 Fresh token saved: {fresh_token[:50]}...")

if __name__ == "__main__":
    update_env_token()
