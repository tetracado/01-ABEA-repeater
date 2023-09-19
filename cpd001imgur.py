import hidcpd001
from imgur_python import Imgur

imgclient=Imgur(hidcpd001.img_authdict)
#auth_url=imgclient.authorize()
#print(auth_url)


def postimg(imagepath):
    file=imagepath
    title=""
    description=""
    album=None
    disable_audio=0
    print('posting image',imagepath)
    response=imgclient.image_upload(file,title,description,album,disable_audio)
    #print(response)
    imgurid=response['response']['data']['id']
    #print(imgurid)
    imglink='https://i.imgur.com/'+imgurid
    print('posted image at',imglink)
    return(imglink)