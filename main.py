from social_media_server import MultiSocialMediaServer

VALID_SOCIAL_MEDIA = set(['instagram','whatsapp','twitter','telegram'])

IP = 'localhost'
PORT = 8080

if __name__ == '__main__':
    server = MultiSocialMediaServer(VALID_SOCIAL_MEDIA)

    try:
        server.open(IP, PORT)
        server.run()

    except KeyboardInterrupt:
        print('server shut down by keyboard interrupt.')

    finally:
        server.close()
