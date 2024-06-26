from typing import Optional, Any
import uuid
from datetime import datetime

import config


class Database:
    def __init__(self):
        self.user_collection = []
        self.dialog_collection = []

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        for user in self.user_collection:
            if user["_id"] == user_id:
                return True

        if raise_exception:
            raise ValueError(f"User {user_id} does not exist")
        else:
            return False

    def add_new_user(
        self,
        user_id: int,
        chat_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
    ):
        user_dict = {
            "_id": user_id,
            "chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "last_interaction": datetime.now(),
            "first_seen": datetime.now(),
            "current_dialog_id": None,
            "current_chat_mode": "assistant",
            "current_model": config.models["available_text_models"][0],
            "n_used_tokens": {},
            "n_generated_images": 0,
            "n_transcribed_seconds": 0.0  # voice message transcription
        }

        if not self.check_if_user_exists(user_id):
            self.user_collection.append(user_dict)

    def start_new_dialog(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)

        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "user_id": user_id,
            "chat_mode": self.get_user_attribute(user_id, "current_chat_mode"),
            "start_time": datetime.now(),
            "model": self.get_user_attribute(user_id, "current_model"),
            "messages": []
        }

        # add new dialog
        self.dialog_collection.append(dialog_dict)

        # update user's current dialog
        for user in self.user_collection:
            if user["_id"] == user_id:
                user["current_dialog_id"] = dialog_id
                break

        return dialog_id

    def get_user_attribute(self, user_id: int, key: str):
        self.check_if_user_exists(user_id, raise_exception=True)
        for user in self.user_collection:
            if user["_id"] == user_id:
                if key in user:
                    return user[key]

        return None

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.check_if_user_exists(user_id, raise_exception=True)
        for user in self.user_collection:
            if user["_id"] == user_id:
                user[key] = value
                break

    def update_n_used_tokens(self, user_id: int, model: str, n_input_tokens: int, n_output_tokens: int):
        n_used_tokens_dict = self.get_user_attribute(user_id, "n_used_tokens")

        if model in n_used_tokens_dict:
            n_used_tokens_dict[model]["n_input_tokens"] += n_input_tokens
            n_used_tokens_dict[model]["n_output_tokens"] += n_output_tokens
        else:
            n_used_tokens_dict[model] = {
                "n_input_tokens": n_input_tokens,
                "n_output_tokens": n_output_tokens
            }

        self.set_user_attribute(user_id, "n_used_tokens", n_used_tokens_dict)

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        for dialog in self.dialog_collection:
            if dialog["_id"] == dialog_id and dialog["user_id"] == user_id:
                return dialog["messages"]

        return []

    def set_dialog_messages(self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        self.check_if_user_exists


    def set_dialog_messages(self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        for dialog in self.dialog_collection:
            if dialog["_id"] == dialog_id and dialog["user_id"] == user_id:
                dialog["messages"] = dialog_messages

