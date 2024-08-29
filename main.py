from social_media_server import MultiSocialMediaServer

IP = 'localhost'
PORT = 8080

if __name__ == '__main__':
    server = MultiSocialMediaServer('data/others.db')

    try:
        server.open(IP, PORT)
        server.run()

    except KeyboardInterrupt:
        print('server shut down by keyboard interrupt.')

    finally:
        server.close()
