from worlds.LauncherComponents import Component, Type, components, launch as launch_component, icon_paths
from Utils import local_path

def run_client(*args: str) -> None:
    from .client.Client import launch
    launch_component(launch, name="Dicey Dungeons Client", args=args)

components.append(
    Component(
        "Dicey Dungeons Client",
        func=run_client,
        game_name="Dicey Dungeons",
        component_type=Type.CLIENT,
        supports_uri=True,
        icon='diceydungeons'
    )
)

icon_paths['diceydungeons'] = local_path('worlds', 'diceydungeons', 'data', 'warrior.ico')