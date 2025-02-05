# Initial code taken from Flet example: https://github.com/flet-dev/examples/blob/main/python/tutorials/chat/chat.py

from encryptions import decrypt, encrypt
from passwords import check_new_password, check_password, hash_password
from hazina_config import load_hazina_config, save_hazina_config
from chatbot import get_agent_response, initialize_agent
from langchain_core.messages import HumanMessage
import flet as ft


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
                    ft.Text(message.text, selectable=True),
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


def get_plain_password(page: ft.Page):
    return page.session.get("plain_password")


def set_plain_password(page: ft.Page, plain_password: str):
    page.session.set("plain_password", plain_password)
    return plain_password


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Hazina - Smart Crypto Wallet with AI Agents"

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
            plain_password = set_plain_password(page, auth_user.value)
            if not (
                hazina_config.cdp_api_key_name is None
                or hazina_config.cdp_api_key_private_key is None
                or hazina_config.openai_api_key is None
            ):
                print(
                    "Encrypted cdp_api_key_name: {}".format(
                        hazina_config.cdp_api_key_name
                    )
                )
                print(
                    "Encrypted cdp_api_key_private_key: {}".format(
                        hazina_config.cdp_api_key_private_key
                    )
                )
                print(
                    "Encrypted openai_api_key: {}".format(hazina_config.openai_api_key)
                )
                cdpkn = decrypt(plain_password, hazina_config.cdp_api_key_name)
                cdppk = decrypt(plain_password, hazina_config.cdp_api_key_private_key)
                oaik = decrypt(plain_password, hazina_config.openai_api_key)
                print("Decypted cdp_api_key_name: {}".format(cdpkn))
                print("Decypted cdp_api_key_private_key: {}".format(cdppk))
                print("Decypted openai_api_key: {}".format(oaik))
                initialize_agent(
                    cdp_api_key_name=cdpkn,
                    cdp_api_key_private_key=cdppk,
                    openai_api_key=oaik,
                )
                responses = get_agent_response("Hi!")
                for response in responses:
                    msg = Message(
                        "Agent {}".format(agent_name),
                        response,
                        message_type="chat_message",
                    )
                    page.pubsub.send_all(msg)
            else:
                keys_dlg.open = True
            welcome_dlg.open = False
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

    def send_message_click(e):
        if new_message.value != "":
            page.pubsub.send_all(
                Message(
                    user_name,
                    new_message.value,
                    message_type="chat_message",
                )
            )

            responses = get_agent_response(new_message.value)
            for response in responses:
                msg = Message(
                    "Agent {}".format(agent_name),
                    response,
                    message_type="chat_message",
                )
                page.pubsub.send_all(msg)

            new_message.value = ""
            new_message.focus()
            page.update()

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.Colors.BLACK45, size=12)
        chat.controls.append(m)
        page.update()

    page.pubsub.subscribe(on_message)

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
            on_submit=click_auth,
            password=True,
            can_reveal_password=True,
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

    # Add everything to the page
    page.add(
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
