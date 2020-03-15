import requests
import config

GITHUB_API_URL = "https://api.github.com/user/repository_invitations"


def accept_invitation(accountName, repositoryName):
    res = requests.get(GITHUB_API_URL, auth=(config.GITHUB_ACCOUNT, config.GITHUB_TOKEN))
    if(res.status_code == 200):
        result = res.json()
    else:
        return 1
    for n in result:
        if(n.get("repository").get("name") == repositoryName):
            if(n.get("repository").get("owner").get("login") == accountName):
                acc_res = requests.patch(GITHUB_API_URL + '/' + str(n.get("id")), auth=(config.GITHUB_ACCOUNT, config.GITHUB_TOKEN))
                if(acc_res.status_code == 204):
                    return 0
                else:
                    return 3
            else:
                return 4
    return 2
