import struct


class GPTMessage:
    def __init__(self, db, chat_id, message_id: int):
        if not isinstance(message_id, int):
            raise TypeError(f"message_id must be int, not {message_id.__class__.__name__} ({message_id})")
        self._id = message_id
        self._chat_id = chat_id
        self._db = db
        self._text = None

    @property
    def id(self):
        return self._id

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def role(self):
        self._db.cursor.execute(f"""SELECT role from Messages{self.chat_id} WHERE id = {self._id}""")
        role = self._db.cursor.fetchone()[0]
        return role

    @property
    def content(self):
        self._db.cursor.execute(f"""SELECT content from Messages{self.chat_id} WHERE id = {self._id}""")
        content = self._db.cursor.fetchone()[0]
        return content

    def add_text(self, text):
        text = self.content + text
        self._db.cursor.execute(f"""UPDATE Messages{self.chat_id} SET content = ? WHERE id = {self._id}""", (text,))
        self._db.commit()

    @property
    def ctime(self):
        self._db.cursor.execute(f"""SELECT ctime from Messages{self.chat_id} WHERE id = {self._id}""")
        ctime = self._db.cursor.fetchone()[0]
        return ctime

    @property
    def replys(self):
        self._db.cursor.execute(f"""SELECT replys from Messages{self.chat_id} WHERE id = {self._id}""")
        messages = self._db.cursor.fetchone()[0]
        if messages is None:
            return
        for el in struct.unpack(f"{len(messages) // 8}q", messages):
            yield GPTMessage(self._db, self.chat_id, el)

    @property
    def replied_count(self):
        self._db.cursor.execute(f"""SELECT replied_count from Messages{self.chat_id} WHERE id = {self._id}""")
        replied_count = self._db.cursor.fetchone()[0]
        return replied_count

    @replied_count.setter
    def replied_count(self, replied_count):
        self._db.cursor.execute(f"""UPDATE Messages{self.chat_id} SET replied_count = 
                                    {replied_count} WHERE id = {self._id}""")
        if replied_count <= 0 and self.deleted:
            self._delete()

    @property
    def remote_id(self):
        self._db.cursor.execute(f"""SELECT remote_id from Messages{self.chat_id} WHERE id = {self._id}""")
        remote_id = self._db.cursor.fetchone()[0]
        return remote_id

    @remote_id.setter
    def remote_id(self, remote_id):
        self._db.cursor.execute(f"""UPDATE Messages{self.chat_id} SET remote_id = ? WHERE id = {self._id}""",
                                (remote_id,))

    @property
    def deleted(self):
        self._db.cursor.execute(f"""SELECT deleted from Messages{self.chat_id} WHERE id = {self._id}""")
        deleted = bool(self._db.cursor.fetchone()[0])
        return deleted

    @deleted.setter
    def deleted(self, deleted):
        self._db.cursor.execute(f"""UPDATE Messages{self.chat_id} SET deleted = 
                                    {1 if deleted else 0} WHERE id = {self._id}""")
        if deleted and self.replied_count <= 0:
            self._delete()

    def _delete(self):
        self._db.cursor.execute(f"""DELETE FROM Messages{self.chat_id} WHERE id = {self._id}""")

    def to_json(self):
        return {'role': self.role, 'content': self.content}

    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'ctime': self.ctime,
            'id': self.remote_id,
            'reply': [m.remote_id for m in self.replys],
        }
