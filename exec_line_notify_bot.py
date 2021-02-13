from line_notify_bot import LINENotifyBot

bot = LINENotifyBot(access_token='n8LtrFMTaSzk59BRsurzaS3ynmrj8nDQjNdCTithByi')

bot.send(
    message='Write Your Message',
    image='./Picture/cat.jpg',  # png or jpg
    sticker_package_id=1,
    sticker_id=13,
    )
