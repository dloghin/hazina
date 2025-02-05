from chatbot import initialize_agent
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


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Hazina - Smart Crypto Wallet with AI Agents"

    agent_executor, agent_config = initialize_agent()

    page.session.set("user_name", "Me (human)")

    agent_name = "Hazina (AI)"

    def click_auth(e):
        if not auth_user.value:
            auth_user.error_text = "Password cannot be blank!"
            auth_user.update()
        else:
            welcome_dlg.open = False
            page.update()

    def send_message_click(e):
        if new_message.value != "":
            page.pubsub.send_all(
                Message(
                    page.session.get("user_name"),
                    new_message.value,
                    message_type="chat_message",
                )
            )

            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=new_message.value)]}, agent_config
            ):
                if "agent" in chunk and chunk["agent"]["messages"][0].content != "":
                    # print(chunk["agent"]["messages"][0].content)
                    msg = Message(
                        "Agent {}".format(agent_name),
                        chunk["agent"]["messages"][0].content,
                        message_type="chat_message",
                        )
                    page.pubsub.send_all(msg)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

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

    # A dialog asking for user password
    auth_user = ft.TextField(
        label="Enter your password",
        autofocus=True,
        on_submit=click_auth,
        password=True,
        can_reveal_password=True
    )
    welcome_dlg = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([auth_user], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=click_auth)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(welcome_dlg)

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
