from enum import Enum
import msal
import webbrowser

from emailicious.config import Config
from emailicious.utils import bail, ExitCode


class MS_CONSTANTS(Enum):
    MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'
    REFRESH_TOKEN_PATH = Config.config_path.parent / 'ms_refresh_token.txt'
    SCOPES = ['User.Read', 'Mail.ReadWrite', 'Mail.Send']


def get_access_token(application_id: str, client_secret: str, scopes: list[str]) -> str:
    client = msal.ConfidentialClientApplication(
        client_id=application_id,
        client_credential=client_secret,
        authority='https://login.microsoftonline.com/consumers',
    )

    refresh_token = None
    if MS_CONSTANTS.REFRESH_TOKEN_PATH.value.exists():
        with open(MS_CONSTANTS.REFRESH_TOKEN_PATH.value, 'r') as f:
            refresh_token = f.read().strip()

    if refresh_token:
        token_response = client.acquire_token_by_refresh_token(refresh_token, scopes)
    else:
        auth_request_url = client.get_authorization_request_url(scopes)
        webbrowser.open(auth_request_url)
        authorization_code = input('Enter the authorization code: ')

        if not authorization_code:
            bail('Authorization code is empty', ExitCode.AUTH_CODE_NOT_ENTERED)

        token_response = client.acquire_token_by_authorization_code(
            authorization_code, scopes
        )

    if 'access_token' in token_response:
        with open(MS_CONSTANTS.REFRESH_TOKEN_PATH.value, 'w') as f:
            f.write(token_response['refresh_token'])

        return token_response['access_token']
    else:
        bail(
            f'Could not get access token from response: {token_response}',
            ExitCode.ACCESS_TOKEN_NOT_FOUND,
        )


def ms_graph_main() -> int:
    config = Config()
    outlook_config = config.config['outlook']
    try:
        access_token = get_access_token(
            outlook_config['application_id'],
            outlook_config['client_secret'],
            MS_CONSTANTS.SCOPES.value,
        )
        headers = {'Authorization': f'Bearer {access_token}'}
        print(headers)
    except Exception as e:
        bail(f'Could not get access token: {e}', ExitCode.ACCESS_TOKEN_NOT_FOUND)

    return 0


if __name__ == "__main__":
    ms_graph_main()
