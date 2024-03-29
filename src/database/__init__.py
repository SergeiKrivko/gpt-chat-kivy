import asyncio
from uuid import uuid4

from src.commands import async_slot
from src.database.database import Database
from src.database.firebase import Firebase, FirebaseError, Stream
from src.gpt.chat import GPTChat


class ChatManager:
    def __init__(self, sm):
        super().__init__()
        self._sm = sm
        self._database = Database(self._sm)
        self._firebase = Firebase(self._sm)
        self._user_id = ""
        self._user_token = None

        self._events_stream = None
        self._chats_stream = None

        self.on_new_chat = None
        self.on_delete_chat = None
        self.on_delete_remote_chat = None
        self.on_update_chat = None
        self.on_new_message = None
        self.on_delete_message = None

    @async_slot
    async def auth(self):
        await self._firebase.auth()
        self._database.update_user()
        await self._load_chats()
        self.retry_auth()

    def retry_auth(self):
        if not self._sm.get('user_id'):
            return
        self._retry_auth()

    @async_slot
    async def _retry_auth(self):
        while True:
            if self._firebase.authorized:
                await asyncio.sleep(max(0, self._firebase.expires_in - 20))
            else:
                await asyncio.sleep(3)
            await self._firebase.auth()

    async def _load_chats(self):
        for chat in self._database.chats:
            await asyncio.sleep(0.1)
            self.on_new_chat(chat)
            if chat.remote_id and self._firebase.authorized:
                flag = await self._firebase.get(f'chats/{chat.remote_id}')
                if not flag:
                    self.on_delete_remote_chat(chat)

        if self._firebase.authorized:
            if isinstance(self._chats_stream, Stream):
                self._chats_stream.close()
            self._chats_stream = self._firebase.stream('chats', self._chats_handler)

            await asyncio.sleep(1)

            if isinstance(self._events_stream, Stream):
                self._events_stream.close()
            self._events_stream = self._firebase.stream('events', self._events_handler)

    def _on_remote_chats(self, path, data):
        if data is None:
            return
        if path == '/':
            for remote_id in data:
                self._add_remote_chat(remote_id)

        else:
            remote_id = path[1:]
            if data is None:
                chat = self._database.get_by_remote_id(remote_id)
                if chat and chat.remote_id:
                    self.on_delete_remote_chat(chat)
            else:
                self._add_remote_chat(remote_id)

    @async_slot
    async def _add_remote_chat(self, remote_id):
        chat = self._database.get_by_remote_id(remote_id)
        data = await self._firebase.get(f'chats/{remote_id}')
        if data is None:
            return
        if chat is None:
            chat = self._database.add_chat()
            chat.remote_id = remote_id
            new_chat = True
        else:
            new_chat = False

        chat.model = data.get('model')
        chat.name = data.get('name')
        chat.saved_messages = data.get('saved_messages')
        chat.used_messages = data.get('used_messages')
        chat.temperature = data.get('temperature')
        chat.type = data.get('type')

        if new_chat:
            self.on_new_chat(chat)
        else:
            self.on_update_chat(chat)

    def _on_event(self, chat_id, events):
        chat = self._database.get_by_remote_id(chat_id)
        to_add = []

        for el in sorted(events, key=lambda a: a[1]):
            type, index, data = el

            if type == 'last':
                pass
                # chat.remote_last = data
            elif index <= (chat.remote_last or -1):
                continue
            else:
                chat.remote_last = max(chat.remote_last or -1, index)
                if type == 'add':
                    to_add.append(data)
                elif type == 'delete':
                    if data in to_add:
                        to_add.remove(data)
                    else:
                        message = chat.get_message_by_remote_id(data)
                        if message is not None:
                            chat.delete_message(message.id)
                            self._database.commit()
                            self.on_delete_message(chat.id, message)

        self._on_messages_add(chat, to_add)

    @async_slot
    async def _on_messages_add(self, chat, message_remote_ids):
        for message_remote_id in message_remote_ids:
            data = await self._firebase.get(f'messages/{chat.remote_id}/{message_remote_id}')
            if data is None:
                continue

            message = chat.add_message(data['role'], data['content'])
            message.remote_id = message_remote_id
            self.on_new_message(chat.id, message)

    def new_chat(self, chat_type=GPTChat.SIMPLE):
        chat = self._database.add_chat()

        # match chat_type:
        #     case GPTChat.TRANSLATE:
        #         chat.data['language1'] = 'russian'
        #         chat.data['language2'] = 'english'
        #         chat.name = f"{chat.data['language1'].capitalize()} ↔ {chat.data['language2'].capitalize()}"
        #         chat.used_messages = 1
        #     case GPTChat.SUMMARY:
        #         chat.name = f"Краткое содержание"
        #         chat.used_messages = 1

        self.on_new_chat(chat)
        return chat

    @async_slot
    async def delete_chat(self, chat_id):
        chat = self._database.get_chat(chat_id)

        if chat.remote_id:
            try:
                await self._firebase.delete(f'chats/{chat.remote_id}')
                await self._firebase.delete(f'messages/{chat.remote_id}')
                await self._firebase.delete(f'events/{chat.remote_id}')
                await self._firebase.delete(f'events/{chat.remote_id}-last')
            except FirebaseError:
                pass

        chat.delete()
        self.on_delete_chat(chat_id)

    async def new_message(self, chat_id: int, role, content, reply=tuple()):
        chat = self._database.get_chat(chat_id)
        message = chat.add_message(role, content, reply)

        if chat.remote_id:
            try:
                message.remote_id = str(uuid4())
                chat.remote_last += 1
                await self._firebase.set(f'messages/{chat.remote_id}/{message.remote_id}', message.to_dict())
                await self._firebase.set(f'events/{chat.remote_id}/{chat.remote_last}', ['add', message.remote_id])
                await self._firebase.set(f'events/{chat.remote_id}-last', chat.remote_last)
            except FirebaseError:
                self._database.rollback()
                return False
            self._database.commit()

        self.on_new_message(chat_id, message)
        return True

    @async_slot
    async def delete_message(self, chat_id, message):
        if message is None:
            return
        chat = self._database.get_chat(chat_id)

        if chat.remote_id:
            try:
                chat.remote_last += 1
                await self._firebase.delete(f'messages/{chat.remote_id}/{message.remote_id}')
                await self._firebase.set(f'events/{chat.remote_id}/{chat.remote_last}', ['delete', message.remote_id])
                await self._firebase.set(f'events/{chat.remote_id}-last', chat.remote_last)
                chat.delete_message(message.id)
            except FirebaseError:
                self._database.rollback()
                return
            self._database.commit()

        self.on_delete_message(chat_id, message)

    async def _update_chat_info(self, chat: GPTChat):
        await self._firebase.set(f'chats/{chat.remote_id}', {
            'id': chat.remote_id,
            'type': chat.type,
            'type_data': chat.type_data,
            'name': chat.name,
            'ctime': chat.ctime,
            'utime': chat.utime,
            'used_messages': chat.used_messages,
            'saved_messages': chat.saved_messages,
            'temperature': chat.temperature,
            'model': chat.model,
        })

    @async_slot
    async def make_remote(self, chat: GPTChat, remote: bool):
        if remote == bool(chat.remote_id):
            self._database.commit()
            return
        if not self._firebase.authorized:
            self._database.commit()
            return

        if remote:
            try:
                chat.remote_id = str(uuid4())
                chat.remote_last = 0
                await self._update_chat_info(chat)
                for message in chat.messages:
                    message.remote_id = str(uuid4())
                    chat.remote_last += 1
                    await self._firebase.set(f'events/{chat.remote_id}/{chat.remote_last}', ['add', message.remote_id])
                    await self._firebase.set(f'messages/{chat.remote_id}/{message.remote_id}', message.to_dict())
                await self._firebase.set(f'events/{chat.remote_id}-last', chat.remote_last)
            except FirebaseError:
                self._database.rollback()
            else:
                self._database.commit()

        else:
            remote_id = chat.remote_id
            chat.remote_id = None
            try:
                await self._firebase.delete(f'chats/{remote_id}')
                await self._firebase.delete(f'messages/{remote_id}')
                await self._firebase.delete(f'events/{remote_id}')
                await self._firebase.delete(f'events/{remote_id}-last')
            except FirebaseError:
                pass
            self._database.commit()

    def _events_handler(self, event_dict):
        path = event_dict['path']
        data = event_dict['data']
        if data is None:
            return

        for key, item in (data.items() if path == '/' else [(path[1:], data)]):
            if key.endswith('-last'):
                key = key[:-len('-last')]
                self._on_event(key, [['last', 0, item]])
            else:
                res = []
                for i, el in enumerate(item if isinstance(item, list) and isinstance(item[0], list) or item[0] is None else [item]):
                    if el:
                        if '/' in key:
                            i = int(key.split('/')[1])
                            key = key.split('/')[0]
                        if el[0] == 'add':
                            res.append(['add', i, el[1]])
                        else:
                            res.append(['delete', i, el[1]])
                self._on_event(key, res)

    def _chats_handler(self, event_dict):
        path = event_dict['path']
        data = event_dict['data']
        self._on_remote_chats(path, data)

    def close(self):
        self._database.close()
        if isinstance(self._events_stream, Stream):
            self._events_stream.close()
        if isinstance(self._chats_stream, Stream):
            self._chats_stream.close()
