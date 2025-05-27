Passo a passo para rodar seu BOT no Render:

1. Acesse https://render.com/
2. Clique em 'New Web Service'.
3. Faça upload dos arquivos.
4. Configure:
   - Build Command: pip install -r requirements.txt
   - Start Command: python main.py
5. Configure as variáveis de ambiente:
   - BOT_TOKEN e PUSHINPAY_API_KEY (já estão no .env)
6. Clique em Deploy.
7. Pronto! Seu bot estará online 24 horas.
