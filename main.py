import discord
import asyncio
import io
from discord.ext import commands


class bot_on(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='$', intents=discord.Intents.all())
      
    async def setup_hook(self):
        self.add_view(Viewticket())
        self.add_view(finalizar())
        self.add_view(sair())

client = bot_on()

@client.command()
async def ticket(ctx: commands.Context):
    embed = discord.Embed(
        #Coloque o nome do seu servidor em title
        title='🎫 ------ 🎫',
        description=f'Para obter Atendimento abra um ticket selecionando no menu a baixo. Escolha a opção de acordo com a necessidade.',
        colour=discord.Colour(5763719),
    )
    embed.set_thumbnail(url=ctx.guild.icon)
    view1 = Viewticket()
    await ctx.channel.purge(limit=1)
    await ctx.channel.send(embed=embed, view=view1)

#se quiser mais opções de ticket adicione um desses em os couxetes de opcoes.

#  --> discord.SelectOption(label=' COLOQUE A OPAÇÃO AQUI', value='AQUI TAMBÉM', description='AQUI A DESCRIÇÃO'), <-- 

# Não esqueça da vigula 
opcoes = [ 
    discord.SelectOption(label=' Suporte', value='suporte', description='Clique aqui para abrir um ticket de suporte'),
          
           discord.SelectOption(label='Limpar seleção', value='limpar', description='Clique aqui para limpar um opção que ja está marcada',emoji='🔁')]

class Viewticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Selecione o ticket que deseja abrir",options=opcoes, custom_id='opcoes')
    async def esolher(self, interact: discord.Interaction, select: discord.ui.Select):
        opcao = select.values[0]
        if opcao == 'limpar':
            await interact.response.defer()
            return
        guild = interact.guild
        channel_name = f"⚒ Ticket-de-{interact.user.name}"
        await interact.response.send_message(f'Ticket aberto como ``{channel_name}``', ephemeral=True)
        # Obtém a categoria específica para os canais crie uma categoria com esse nome que os tickets irão para lá.
        category = discord.utils.get(guild.categories, name='⚒ ・ TICKETS')
        # Define as permissões para o novo canal
        role = guild.get_role()# <--colocar o id do cargo de quem quer irá atender os tickets
        
        overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        interact.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await channel.send(interact.user.mention)
        # Cria um novo embed para o canal de pagamento
        content_embed = discord.Embed(
        title=f'⚒ TICKET {opcao} ⚒',
        colour=discord.Colour(5763719))
        content_embed.add_field(name='',value='``DESCREVA O MOTIVO DO CONTATO COM O MÁXIMO DE DETALHES POSSÍVEIS QUE ALGUM RESPONSÁVEL JÁ IRÁ LHE ATENDER!``', inline=False)
        view = finalizar()
        view.add_item(sair().children[0])
        await channel.send(embed=content_embed)
        await channel.send(view=view)

class finalizar(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  

    @discord.ui.button(label='Finalizar Ticket', custom_id='finalizar', style=discord.ButtonStyle.success)
    async def botao(self, interact: discord.Interaction, button: discord.ui.Button):
        source_channel = interact.channel
        guild = interact.guild
        destination_channel_id = discord.utils.get(guild.channels, name='logs_tickets')
        messages = []
        async for message in source_channel.history(limit=None):
            messages.append(message)
        messages.sort(key=lambda msg: msg.created_at)
        message_content = ""
        for message in messages:    
            timestamp = message.created_at.strftime("%d-%m|%H:%M:")
            message_content += f"{timestamp} {message.author.name}: {message.content}\n"
            for attachment in message.attachments:
                message_content += f"Attachment: {attachment.url}\n"
            for embed in message.embeds:
                message_content += "Embed:\n"
                if embed.title:
                    message_content += f"Title: {embed.title}\n"
                if embed.description:
                    message_content += f"Description: {embed.description}\n"
                if embed.fields:
                    for field in embed.fields:
                        message_content += f"{field.name}: {field.value}\n"
        file_buffer = io.StringIO(message_content)
        file_buffer.seek(0)  # Move o ponteiro de volta ao início do arquivo
        if destination_channel_id:
            discord_file = discord.File(file_buffer, filename=f"{source_channel.name}_messages.txt")
            await destination_channel_id.send(f'Transcript do canal {source_channel.name} fechado por {interact.user.name}')
            await destination_channel_id.send(file=discord_file)
            await interact.response.defer()
            await interact.channel.send('Ticket finalizado, esse canal será deletado em breve...')
            await asyncio.sleep(5)
            await interact.channel.delete()
        else:
            await interact.channel.send("Canal de destino não encontrado. Você precisa criar um canal com o nome ``logs_tickets``")

class sair(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  

    @discord.ui.button(label='Sair Ticket', custom_id='sairticket', style=discord.ButtonStyle.danger)
    async def sairticket(self, interact: discord.Interaction, button: discord.ui.Button):
        channel = interact.channel  # Obtém o canal de texto onde o comando foi executado
        user = interact.user  # Obtém o autor do comando (usuário que solicitou)
        await interact.channel.send(f"{user.mention}, resolveu sair do ticket {channel.name}.")
        await channel.set_permissions(user, overwrite=None)  # Remove todas as permissões do usuário no canal   
        await interact.response.defer()



client.run('SEUTOKEM')