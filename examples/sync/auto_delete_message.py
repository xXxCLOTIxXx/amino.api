import amino

client = amino.FullClient()
client.login("email@gmail.com", "password")
@client.event("on_reslove")
def on_event(data):
	client.delete_message(comId=data.comId, chatId=data.message.chatId, asStaff=True, reason="auto delete :)", messageId=data.message.messageId)