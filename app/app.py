# Initial code taken from Flet example: https://github.com/flet-dev/examples/blob/main/python/tutorials/chat/chat.py

import asyncio
import os
import random
from trader import run_trader_ollama, run_trader_openai, stop_trader
from telegram_bot import connect_to_telegram
from encryptions import decrypt, encrypt
from passwords import check_new_password, check_password, hash_password
from hazina_config import load_hazina_config, save_hazina_config
from chatbot import (
    get_agent_response,
    get_network,
    get_wallet_address,
    get_wallet_balance,
    initialize_agent,
)
from langchain_core.messages import HumanMessage
import flet as ft
import flet_audio as fta
from openai import OpenAI

openai_client = None
sound_on = True
in_auto_mode = False
use_ollama = True

class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type


class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Markdown(
                        message.text,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    ),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


def set_plain_password(page: ft.Page, plain_password: str):
    page.session.set("plain_password", plain_password)
    return plain_password


def get_plain_password(page: ft.Page):
    return page.session.get("plain_password")


def set_openai_key(page: ft.Page, openai_key: str):
    page.session.set("openai_key", openai_key)
    return openai_key


def get_openai_key(page: ft.Page):
    return page.session.get("openai_key")


def play_sound(page: ft.Page, message: str):
    pwd = os.getcwd()
    afile = "{}/.tts.mp3".format(pwd)
    if openai_client is None:
        print("OpenAI client is not initialized")
        return
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=message,
    )
    response.stream_to_file(afile)
    a1 = fta.Audio(
        src=afile, autoplay=True
    )
    page.overlay.append(a1)
    page.update()


def publish_message(page: ft.Page, message: str, name: str, with_audio: bool = True):
    msg = Message(name, message, message_type="chat_message")
    page.pubsub.send_all(msg)
    global sound_on
    if with_audio and sound_on:
        play_sound(page, message)


def run_trader(callback, page: ft.Page, agent_name: str):
    if use_ollama:
        publish_message(page, "Starting Autonomous Mode with Ollama", agent_name)
        asyncio.run(run_trader_ollama(callback))
    else:
        publish_message(page, "Starting Autonomous Mode with OpenAI", agent_name)
        asyncio.run(run_trader_openai(callback, get_openai_key(page)))


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Hazina - Smart Crypto Wallet with AI Agents"
    page.window.width = 1400

    hazina_config = load_hazina_config()

    user_name = "Me (human)"
    agent_name = "Hazina (AI)"

    def click_auth(e):
        if not auth_user.value:
            auth_user.error_text = "Password cannot be blank!"
            auth_user.update()
        elif not check_password(auth_user.value, hazina_config.passhash):
            auth_user.error_text = "Incorrect password!"
            auth_user.update()
        else:
            auth_user.disabled = True
            welcome_dlg.open = False
            page.update()

            plain_password = set_plain_password(page, auth_user.value)
            # if we have the API keys, initialize the agent
            if not (
                hazina_config.cdp_api_key_name is None
                or hazina_config.cdp_api_key_private_key is None
                or hazina_config.openai_api_key is None
            ):
                cdpkn = decrypt(plain_password, hazina_config.cdp_api_key_name)
                cdppk = decrypt(plain_password, hazina_config.cdp_api_key_private_key)
                oaik = decrypt(plain_password, hazina_config.openai_api_key)
                set_openai_key(page, oaik)
                initialize_agent(
                    cdp_api_key_name=cdpkn,
                    cdp_api_key_private_key=cdppk,
                    openai_api_key=oaik,
                )
                global openai_client
                openai_client = OpenAI(api_key=oaik)
                responses = get_agent_response("Hi!")
                for response in responses:
                    publish_message(page, response, agent_name)
                txt_wallet_address.value = get_wallet_address()
                txt_network.value = get_network()
                txt_wallet_balance.value = (
                    get_wallet_balance(txt_wallet_address.value, "eth") + " ETH"
                )
            else:
                # otherwise, open the API keys dialog
                keys_dlg.open = True
            page.update()

    def click_set_pass(e):
        if not pass1.value:
            pass1.error_text = "Password cannot be blank!"
            pass1.update()
        elif not pass2.value:
            pass2.error_text = "Password cannot be blank!"
            pass2.update()
        elif pass1.value != pass2.value:
            pass2.error_text = "Passwords do not match!"
            pass2.update()
        elif not check_new_password(pass1.value):
            pass1.error_text = "Password is not strong enough!"
            pass1.update()
        else:
            # save the password hash on disk, and plain password in session
            plain_password = set_plain_password(page, pass1.value)
            hazina_config.passhash = hash_password(plain_password)
            save_hazina_config(hazina_config)
            welcome_dlg.open = False
            keys_dlg.open = True
            page.update()

    def click_set_keys(e):
        if not cdp_key_name.value:
            cdp_key_name.error_text = "CDP_API_KEY_NAME cannot be blank!"
            cdp_key_name.update()
        elif not cdp_key_pk.value:
            cdp_key_pk.error_text = "CDP_API_KEY_PRIVATE_KEY cannot be blank!"
            cdp_key_pk.update()
        elif not openai_key.value:
            openai_key.error_text = "OPENAI_API_KEY cannot be blank!"
            openai_key.update()
        else:
            plain_password = get_plain_password(page)
            hazina_config.cdp_api_key_name = encrypt(plain_password, cdp_key_name.value)
            hazina_config.cdp_api_key_private_key = encrypt(
                plain_password, cdp_key_pk.value
            )
            hazina_config.openai_api_key = encrypt(plain_password, openai_key.value)
            save_hazina_config(hazina_config)
            initialize_agent(
                cdp_api_key_name=cdp_key_name.value,
                cdp_api_key_private_key=cdp_key_pk.value,
                openai_api_key=openai_key.value,
            )
            keys_dlg.open = False
            page.update()

    def show_trader_message(message):
        publish_message(page, message, agent_name, with_audio=False)
        page.update()

    def send_message_click(e):
        if new_message.value != "":
            message = new_message.value
            page.pubsub.send_all(
                Message(
                    user_name,
                    message,
                    message_type="chat_message",
                )
            )
            new_message.value = ""
            new_message.focus()
            page.update()

            if message == "run in autonomous mode":
                run_trader(show_trader_message, page, agent_name)
            else:
                responses = get_agent_response(message)
                for response in responses:
                    publish_message(page, response, agent_name)

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.Colors.BLACK45, size=12)
        chat.controls.append(m)
        page.update()

    page.pubsub.subscribe(on_message)

    def on_connect_telegram(username, userid):
        txt_telegram.value = "Connected with Telegram as {}".format(username)
        publish_message(page, "Connected with Telegram as {}".format(username), agent_name)
        page.update()

    def connect_telegram(e):
        token = str(random.choice(range(1000000000, 9999999999)))
        publish_message(page, "To connect with Telegram, please paste the following code in the Telegram chat: **{}**".format(token), agent_name)
        asyncio.run(connect_to_telegram(token, on_connect_telegram))

    if hazina_config is None or hazina_config.passhash is None:
        # A dialog to set user password
        pass1 = ft.TextField(
            label="Set a password",
            autofocus=True,
            password=True,
            can_reveal_password=True,
        )
        pass2 = ft.TextField(
            label="Enter the same password again",
            autofocus=True,
            password=True,
            can_reveal_password=True,
        )
        welcome_dlg = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Welcome!"),
            content=ft.Column([pass1, pass2], width=300, height=120, tight=True),
            actions=[ft.ElevatedButton(text="Set Password", on_click=click_set_pass)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(welcome_dlg)
    else:
        # A dialog asking for user password
        auth_user = ft.TextField(
            label="Enter your password",
            autofocus=True,
            password=True,
            can_reveal_password=True,
            on_submit=click_auth,
        )
        welcome_dlg = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Welcome!"),
            content=ft.Column([auth_user], width=300, height=70, tight=True),
            actions=[ft.ElevatedButton(text="Authenticate", on_click=click_auth)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(welcome_dlg)

    # A dialog to set user keys
    cdp_key_name = ft.TextField(
        label="CDP_API_KEY_NAME",
        autofocus=True,
    )
    cdp_key_pk = ft.TextField(
        label="CDP_API_KEY_PRIVATE_KEY",
        autofocus=True,
    )
    openai_key = ft.TextField(
        label="OPENAI_API_KEY",
        autofocus=True,
    )
    keys_dlg = ft.AlertDialog(
        open=False,
        modal=True,
        title=ft.Text("Keys Settings"),
        content=ft.Column(
            [cdp_key_name, cdp_key_pk, openai_key], width=300, height=160, tight=True
        ),
        actions=[ft.ElevatedButton(text="Save", on_click=click_set_keys)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(keys_dlg)

    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A new message entry form
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    def change_sound_option(e):
        global sound_on
        if sound_on:
            sound_on = False
            txt_sound.value = "Without Sound"
            btn_sound.icon = ft.Icons.VOLUME_OFF
        else:
            sound_on = True
            txt_sound.value = "With Sound"
            btn_sound.icon = ft.Icons.VOLUME_UP
        page.update()

    def change_mode_option(e):
        global in_auto_mode
        if in_auto_mode:
            in_auto_mode = False
            txt_mode.value = "User Mode"
            btn_mode.icon = ft.Icons.PERSON
            stop_trader()
        else:
            in_auto_mode = True
            txt_mode.value = "Autonomous Mode"
            btn_mode.icon = ft.Icons.AUTO_MODE
            run_trader(show_trader_message, page, agent_name)
        page.update()

    page.theme_mode = ft.ThemeMode.LIGHT
    def change_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            txt_theme.value = "Dark Theme"
            btn_theme.icon = ft.Icons.LIGHT_MODE
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            txt_theme.value = "Light Theme"
            btn_theme.icon = ft.Icons.DARK_MODE
        page.update()

    txt_wallet_address = ft.Text(value="Wallet Address")
    txt_wallet_balance = ft.Text(value="Wallet Balance")
    txt_network = ft.Text(value="Current Network")
    txt_telegram = ft.Text(value="Not Connected with Telegram")
    txt_theme = ft.Text(value="Light Theme")
    txt_sound = ft.Text(value="With Sound")
    txt_mode = ft.Text(value="User Mode")

    btn_telegram = ft.IconButton(
        icon=ft.Icons.TELEGRAM,
        icon_size=40,
        url="https://t.me/hazina_app_bot",
        on_click=connect_telegram,
    )
    btn_sound = ft.IconButton(
        icon=ft.Icons.VOLUME_UP,
        icon_size=40,
        on_click=change_sound_option,
    )
    btn_theme = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        icon_size=40,
        on_click=change_theme,
    )
    btn_mode = ft.IconButton(
        icon=ft.Icons.PERSON,
        icon_size=40,
        on_click=change_mode_option
    )

    global use_ollama
    def change_model_option(e):
        global use_ollama
        if dd_models.value == "OpenAI":
            use_ollama = False
        else:
            use_ollama = True

    dd_models = ft.Dropdown(
        width=100,
        options=[
            ft.dropdown.Option("Ollama"),
            ft.dropdown.Option("OpenAI"),
            ft.dropdown.Option("Autonome"),
        ],
        value="Ollama" if use_ollama else "OpenAI",
        on_change=change_model_option,
    )

    
    bg_image = ft.Image(
        image_src=f"/home/ubuntu/git/ct/hazina/assets/banner.png",
        image_opacity=0.3,      # Opacity value should be between 0.0 (completely transparent) and 1.0 (not transparent).
    )

    # Add everything to the page
    page.add(
        ft.Row(
            [
                ft.Icon(ft.Icons.WALLET, size=40),
                txt_wallet_address,
                ft.Icon(ft.Icons.BALANCE, size=40),
                txt_wallet_balance,
                ft.Icon(ft.Icons.NETWORK_CHECK, size=40),
                txt_network,
                btn_mode,
                txt_mode,
                ft.Icon(ft.Icons.MODEL_TRAINING, size=40),
                dd_models,
                btn_telegram,
                txt_telegram,
                btn_sound,
                txt_sound,
                btn_theme,
                txt_theme
            ]
        ),
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,

        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )


ft.app(target=main)
