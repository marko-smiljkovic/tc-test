import json
import urllib.request
import urllib.parse


class HunterIO:
    """
    Mini wrapper around hunterio.
    There are some existing user written wrappers, but its kinda small,
    and we do require just one call so this wrapper should be enough.
    """

    apikey = None
    service_url = None
    request_params = None

    def __init__(self, apikey, service_url, service_api_version="v2"):
        self.apikey = apikey
        self.service_url = service_url
        self.service_api_version = service_api_version

    def check_email(self, email):
        """
        Method used for checking given email for validity through hunterio api
        :param email: email to check if valid
        :return: true if email check passed, false otherwise
        :rtype: bool
        """
        params = urllib.parse.urlencode({
            "api_key": self.apikey,
            "email": email,
        })

        request_url = urllib.request.urlopen("{}/{}/email-verifier?{}".format(
            self.service_url,
            self.service_api_version,
            params
        ))
        data = request_url.read()
        encoding = request_url.info().get_content_charset('utf-8')
        response = json.loads(data.decode(encoding))

        return _check_email_verification_response(response)


def _check_email_verification_response(response):
    """
    This function is used to somewhat parse hunterio response
    :param response: hunterio response json
    :return: true if by some standards email is good, else false
    :rtype: bool
    """
    data = response["data"]
    # TODO hunterio documentation doesnt define score too well,
    # so these values that are being checked are from my own opinion (@churava)
    if data["gibberish"] is False and \
            data["regexp"] is True and \
            data["smtp_server"] is True and \
            data["smtp_check"] is True:
        return True
    return False
