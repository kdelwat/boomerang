from boomerang import Messenger

VERIFY_TOKEN = 'secret_code'
PAGE_TOKEN = 'EAADJEe1tgFsBAJeckF94txRTMdB8RbETaGzSuchPYk8PBL78ZA0renQBHJNEFoTS1LwM4ukcnW0n8cMi9ZBxZADtUbCzcAEenzXojzCJLvHdqZB1m9BTYdAncqA4uHvca4VhZBcC2Aq54Nh3viJxpJxrYOUeZCsisZD'

app = Messenger(VERIFY_TOKEN, PAGE_TOKEN)
app.run(hostname='0.0.0.0', debug=True)
