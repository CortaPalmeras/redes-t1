from src.social_media_server import SocialMediaServer

IP = 'localhost'
PORT = 8080

if __name__ == '__main__':
    server = SocialMediaServer(IP, PORT, 'data/whatsapp.db', 'whatsapp')

    try:
        server.run()

    except KeyboardInterrupt:
        print('server shut down by keyboard interrupt.')

