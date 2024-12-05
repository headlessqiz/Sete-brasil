import discord
from discord.ext import tasks, commands
import requests

TOKEN = "MTMxMjk0MTEwMDQ0NDY4MDIxMw.GmzEpb.HWH0IWl7rpOyC8bwOSiINQq2glyTw4IfJW9Q_U"  # Substitua pelo seu token real
CHANNEL_ID = 1312483978027995207  # ID do canal

intents = discord.Intents.default()
intents.message_content = True  # Permite ler o conteúdo das mensagens

bot = commands.Bot(command_prefix="&", intents=intents)

# Função para obter os preços das criptomoedas
def obter_precos():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,solana,dogecoin,shiba-inu,xrp&vs_currencies=brl"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        return dados
    else:
        print("Erro ao obter dados.")
        return None

# Evento quando o bot estiver pronto
@bot.event
async def on_ready():
    print(f"Bot {bot.user} está online!")
    if not update_crypto_prices.is_running():
        update_crypto_prices.start()

# Atualiza os preços de criptomoedas a cada 10 minutos
@tasks.loop(minutes=10)
async def update_crypto_prices():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Canal não encontrado.")
        return

    dados_precos = obter_precos()
    
    if dados_precos:
        embed = discord.Embed(title="Preços de Criptomoedas", color=0x00ff00)
        
        embed.add_field(name="**Criptomoedas**", value="\u200b", inline=False)
        
        for cripto, info in dados_precos.items():
            embed.add_field(name=f"{cripto.capitalize()}", value=f"R${info['brl']}", inline=False)

        embed.set_footer(text="Atualizado automaticamente a cada 10 minutos")

        async for message in channel.history(limit=10):
            if message.author == bot.user and len(message.embeds) > 0:
                await message.edit(embed=embed)
                break
        else:
            await channel.send(embed=embed)

# Comando de banimento
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member} foi banido(a) por {reason if reason else "nenhum motivo especificado"}.')

# Comando de desbanimento
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User):
    await ctx.guild.unban(user)
    await ctx.send(f'{user} foi desbanido.')

# Comando de expulsão
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} foi expulso(a) por {reason if reason else "nenhum motivo especificado"}.')

# Comando para limpar mensagens (limitar a 100 por vez)
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount > 100:
        await ctx.send('Você não pode deletar mais de 100 mensagens de uma vez.')
        return
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'{amount} mensagens limpas.', delete_after=3)

# Comando de verificação de permissões
@bot.command()
async def perms(ctx):
    perms = ctx.author.permissions_in(ctx.channel)
    perm_list = [perm for perm, value in perms if value]
    await ctx.send(f'Você tem as seguintes permissões: {", ".join(perm_list)}')

# Iniciando o bot com seu token
bot.run(TOKEN)
