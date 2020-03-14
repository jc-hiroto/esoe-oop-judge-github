import request

GITHUB_API_URL = "https://api.github.com/user/repository_invitations"

def accept_invitation(repositoryName):
    res = requests.get(GITHUB_API_URL, auth=(config.GITHUB_ACCOUNT, config.GITHUB_TOKEN))
    result = res.json()
    for n in result:
        if( n.get("repository").get("name") == repositoryName):
            res = requests.patch(GITHUB_API_URL+str(n.get("id")), auth=(config.GITHUB_ACCOUNT, config.GITHUB_TOKEN))
            if(res.status_code == 204):
                return True
            else:
                return False
    return False

