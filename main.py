
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
PUSHIN_API_KEY = os.getenv("PUSHINPAY_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await context.bot.send_photo(chat_id=chat_id, photo='https://via.placeholder.com/500')

    texto = "🔥 Bem-vindo! Escolha seu plano:"

    keyboard = [
        [InlineKeyboardButton("💎 SEMANAL - R$2", callback_data="semanal")],
        [InlineKeyboardButton("💎 MENSAL - R$5", callback_data="mensal")],
        [InlineKeyboardButton("💎 VITALÍCIO - R$20", callback_data="vitalicio")],
        [InlineKeyboardButton("💎 TESTE 1 DIA - R$1", callback_data="teste")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text=texto, reply_markup=reply_markup)

    asyncio.create_task(sequencia_mensagens(chat_id, context))

def gerar_pix(plano, valor):
    data = {
        "name": plano,
        "value": float(valor),
        "expires_in": 600
    }
    headers = {
        "Authorization": f"Bearer {PUSHIN_API_KEY}"
    }
    response = requests.post("https://api.pushinpay.com/charge", json=data, headers=headers)
    if response.status_code == 201:
        r = response.json()
        return r['payload'], r['id']
    else:
        print(response.text)
        return None, None

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plano = query.data

    valores = {
        "semanal": 2,
        "mensal": 5,
        "vitalicio": 20,
        "teste": 1
    }
    valor = valores.get(plano, 5)

    pix, charge_id = gerar_pix(plano, valor)

    if pix is None:
        await query.message.reply_text("❌ Erro ao gerar o código Pix. Tente novamente.")
        return

    texto = (
        f"✅ Pagamento gerado com sucesso!\n\n"
        f"👉 Plano: {plano.upper()}\n"
        f"👉 Valor: R$ {valor}\n\n"
        "O código Pix expira em 10 minutos.\n\n"
        f"Código Pix:\n{pix}\n\n"
        "Após realizar o pagamento, clique no botão abaixo."
    )

    keyboard = [
        [InlineKeyboardButton("✅ JÁ PAGUEI", callback_data=f"pago_{charge_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(texto, reply_markup=reply_markup)

async def confirmou(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    charge_id = query.data.split("_")[1]

    headers = {
        "Authorization": f"Bearer {PUSHIN_API_KEY}"
    }
    check_url = f"https://api.pushinpay.com/charge/{charge_id}"

    response = requests.get(check_url, headers=headers)

    if response.status_code == 200:
        r = response.json()
        if r['status'] == "paid":
            await query.message.reply_text("🔓 Pagamento confirmado! Aqui está seu acesso: [LINK DE ACESSO]")
        else:
            await query.message.reply_text("⏳ Pagamento ainda não identificado. Aguarde alguns segundos e clique novamente.")
    else:
        await query.message.reply_text("❌ Erro ao verificar pagamento.")

async def sequencia_mensagens(chat_id, context):
    mensagens = [
        ("🔥 Lembre-se, nosso melhor plano é o VITALÍCIO! Não perca!", 180),
        ("🚀 Ainda está na dúvida? Aproveite nosso plano MENSAL com super desconto!", 600),
        ("⚡ Última chance de pegar o VITALÍCIO com preço promocional!", 1800),
        ("🎯 Está esperando o quê? Acesso vitalício, suporte total e segurança garantida!", 3600),
        ("💎 Última mensagem! Vem garantir sua vaga agora antes de fechar!", 10800)
    ]

    for texto, atraso in mensagens:
        await asyncio.sleep(atraso)
        keyboard = [
            [InlineKeyboardButton("💎 VITALÍCIO - R$20", callback_data="vitalicio")],
            [InlineKeyboardButton("💎 MENSAL - R$5", callback_data="mensal")],
            [InlineKeyboardButton("💎 TESTE - R$1", callback_data="teste")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=texto, reply_markup=reply_markup)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern="^(semanal|mensal|vitalicio|teste)$"))
    app.add_handler(CallbackQueryHandler(confirmou, pattern="^pago_"))

    print("BOT RODANDO...")
    app.run_polling()

if __name__ == "__main__":
    main()
