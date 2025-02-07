import flet as ft
import flet_audio as fta
import os

def main(page: ft.Page):
    pwd = os.getcwd()
    print(pwd)
    audio1 = fta.Audio(
        src="{}/output.mp3".format(pwd),
        autoplay=True,
        volume=1,
        on_loaded=lambda _: print("Loaded"),
        on_duration_changed=lambda e: print("Duration changed:", e.data),
        on_position_changed=lambda e: print("Position changed:", e.data),
        on_state_changed=lambda e: print("State changed:", e.data),
        on_seek_complete=lambda _: print("Seek complete"),
    )
    page.overlay.append(audio1)
    page.add(
        ft.Text("This is an app with background audio."),
        ft.ElevatedButton("Play", on_click=lambda _: audio1.play()),
        ft.ElevatedButton("Pause", on_click=lambda _: audio1.pause()),
        ft.ElevatedButton("Resume", on_click=lambda _: audio1.resume()),
    )

ft.app(main)