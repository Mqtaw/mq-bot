import uvicorn
from fastapi import FastAPI, Request, status, Response, HTTPException
from mqbot.telegram import telebot, bot


API_TOKEN = '<api_token>'

WEBHOOK_HOST = '<ip/host where the bot is running>'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)


app = FastAPI(title='mq-bot', description='My bot', version='0.1.0')

@app.post('/webhook')
async def webhook(request: Request):
    print(request.headers)
    # if request.match_info.get('token') == bot.token:
    if request.headers['Content-type'] == 'application/json':
        request_json = await request.json()
        bot_update = telebot.types.Update.de_json(request_json)
        bot.process_new_updates([bot_update])
        return Response(status_code=status.HTTP_200_OK)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN)


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()
# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
certificate=open(WEBHOOK_SSL_CERT, 'r'))
# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)




if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)

# web.run_app(
#     app,
#     host=WEBHOOK_LISTEN,
#     port=WEBHOOK_PORT,
#     ssl_context=context,
# )