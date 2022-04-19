from geni.aggregate import FrameworkRegistry
from geni.aggregate.context import Context
from geni.aggregate.user import User

def buildContext ():
    print("buildContext: building the 'portal' by user s279434")
    framework = FrameworkRegistry.get("portal")()
    framework.cert = "./api/geni_utilities/geni-s279434.pem" #NOTE run from RLVNA
    framework.key = "./api/geni_utilities/geni-s279434.pem"     #Update with proper certificate

    user = User()
    user.name = "s279434"
    user.urn = "urn:publicid:IDN+ch.geni.net+user+s279434"
    user.addKey("./api/geni_utilities/id_ed25519.pub")

    context = Context()
    context.addUser(user)
    context.cf = framework
    context.project = "network-scalability-tests"

    return context