from typing import Self
from flask import session
from dataclasses import dataclass
import time


class AuthnStateCache:

    def get(self, key: str):
        try:
            return session["tickets"].get(key)
        except KeyError:
            return None

    def set(self, key, value):
        if "tickets" not in session:
            session["tickets"] = {}

        session["tickets"][key] = value

    def delete(self, key):
        try:
            del session["tickets"][key]
        except KeyError:
            pass

    def clear(self):
        session["tickets"] = {}


type binding = str


def is_authenticated():
    return "authenticated" in session


def set_authenticated():
    session["authenticated"] = time.time()


@dataclass
class AuthnState:

    tickets = AuthnStateCache()
    ticket: str
    message: str
    entity_id: str
    relay_state: str

    @staticmethod
    def load(ticket: str) -> Self:
        state = AuthnState.tickets.get(ticket)
        if state:
            return AuthnState.tickets.get(ticket)

    def save(self):
        AuthnState.tickets.set(self.ticket, self)
