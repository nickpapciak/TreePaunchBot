from pkg_resources import working_set
import os

def load_cogs(self): 
  for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename != '__init__.py':
      self.load_extension(f'cogs.{filename[:-3]}')

def load_menu(): 
  if 'discord-ext-menus' not in sorted({f"{i.key}" for i in working_set}):
    os.system('pip install -U git+https://github.com/Rapptz/discord-ext-menus')
    print("Menus module was re-installed")



# async def on_command_error(self, ctx, error):
#     print(error)
#     return True