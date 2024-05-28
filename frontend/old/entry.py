from frontend.frontend import FileExplorer

from nicegui import ui


async def pick_file() -> None:
    result = FileExplorer('C:\\Users\Felix\Desktop\Camera\\videos')
    ui.notify(f'You chose {result}')


# ui.button('Choose file', on_click=pick_file, icon='folder')

ui.run()
