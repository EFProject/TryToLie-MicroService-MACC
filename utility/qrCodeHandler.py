
def buildQRCodeUrl(room_id):
	pixels = 100
	#qrCodeUrl = 'https://api.qrserver.com/v1/create-qr-code/?data=[URL-encoded-text]&size=[pixels]x[pixels]'
	qrCodeUrl = f'https://api.qrserver.com/v1/create-qr-code/?data={room_id}&amp;size={pixels}x{pixels}'
	return qrCodeUrl