TelegramBot = require('node-telegram-bot-api')

// const bot = new TelegramBot(process.env.BOT_TELEGRAM_TOKEN, {
const bot = new TelegramBot(env.process.TM_TOKEN, {
  polling: false,
});

// change polling to true, so you will get chat id from bot
bot.sendMessage(process.env.CHAT, process.env.MSG)

// AU17: -1001143231884
// DD17:   -239361319