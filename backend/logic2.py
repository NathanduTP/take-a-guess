from json import dumps
from typing import Dict
from uuid import uuid4

import socketio
from gevent import pywsgi

sio = socketio.Server(
    # TODO: Replace later on production
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
    async_mode="gevent",
)
app = socketio.WSGIApp(sio)


class Player:
    def __init__(self, name: str, sid: str, hearts: int) -> None:
        """a class which represent a player

        Args:
            name (str): the player's name
            sid (str): The socket id associated to the user
        """
        self.sid = sid
        self.name = name
        self.points = 0
        self.past_points = 0
        self.answer = None
        self.hearts = hearts

    def add_points(self, points):
        """Add points to the player. Keep the amount of points added to cancel the answer if needed

        Args:
            points (int): the amount of points earned
        """
        self.points += points
        self.past_points = points

    def cancel_current_turn(self):
        """Cancel the amount of point earned during this turn"""
        self.points -= self.past_points
        self.hearts += 1
        self.past_points = 0

    def to_dict(self) -> dict:
        return {
            "id": self.sid,
            "name": self.name,
            "points": self.points,
            "past-points": self.past_points,
            "answer": self.answer,
            "hearts": self.hearts,
        }


class Setting:
    def __init__(self, lives: int = None, timer: int = None) -> None:
        self.lives = lives
        self.timer = timer

    def to_dict(self):
        return {"lives": self.lives, "timer": self.timer}


class Room:
    def __init__(
        self,
        players: Dict[str, Player],
        admin_id: str,
        settings: Setting = Setting(),
        locked: bool = False,
        answer: str = None,
    ) -> None:
        """A class which represent a room

        Args:
            players (Dict[str, Player]): Players in the room
            admin_id (str): The admin socket id
            settings (Setting, optional): game settings for the room. Defaults to Setting().
            locked (bool, optional): Whether or not new players are allowed to enter the room. Defaults to False.
            answer (str, optional): The correct answer for this turn. Defaults to None.
        """
        self.players = players
        self.admin_id = admin_id
        self.settings = settings
        self.locked = locked
        self.answer = answer
        self.questions = 0

    def is_name_already_used(self, name) -> bool:
        """Check whether or not a name is taken by someone else

        Args:
            name (str): the name to take

        Returns:
            bool: True if the name is already taken, False otherwise
        """
        return name in [p.name for _, p in self.players.items()]

    def add_player(self, name: str, sid: str):
        """Add a player to the room object

        Args:
            name (str): the player's name
            sid (str): the socket id with which the player logged in
        """
        self.players[sid] = Player(name, sid, int(self.settings.lives))

    def get_players(self):
        """Return a json object with players in the room

        Returns:
            list: The list of players in the room
        """
        return [p.to_dict() for _, p in self.players.items()]

    def get_settings(self) -> dict:
        return self.settings.to_dict()

    def next_question(self):
        """Increase total question by 1"""
        self.questions += 1

    def to_dict(self):
        return {
            "admin": self.admin_id,
            "players": self.get_players(),
            "settings": self.settings.to_dict(),
            "locked": self.locked,
            "correct-answer": self.answer,
            "questions": self.questions,
        }


ROOMS: Dict[str, Room] = {}
ROOM = None
ROOM_ID = uuid4()


def make_response(status: str, message: str, **extra):
    # TODO: Remove print
    # for _, room in ROOMS.items():
    #     print(dumps(room.to_dict(), indent=2))
    if ROOM:
        print(dumps(ROOM.to_dict(), indent=2))

    return {"status": status, "reason": message, **extra}


@sio.on("create-room")
def onCreateRoom(sid, data: dict):
    """Whenever the admin creates a new room

    Args:
        sid (Any): the client's socket io who emitted the event
        data (Dict): data passed alongside the event
    """
    global ROOM

    lifes = data.get("lifes", None)

    if lifes:
        if ROOM:
            sio.emit(
                "create-room",
                data=make_response("error", "Room is already taken"),
                to=sid,
            )
        else:
            ROOM = Room(players={}, settings=Setting(int(lifes)), admin_id=sid)
            sio.emit(
                "create-room",
                data=make_response("success", "Successfully created the room"),
            )

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("join-room")
def onJoinRoom(sid, data: dict):
    """Whenever a new player tries to join the room

    Args:
        sid (string): the user's socket iod
        data (dict): Data passed alongside the event
    """
    global ROOM

    print("ROOMID: ", ROOM_ID)

    username = data.get("username", None)

    if not username:
        sio.emit(
            "join-room",
            data=make_response("error", "Unspecified username"),
            to=sid,
        )
    elif ROOM and ROOM.locked:
        sio.emit(
            "join-room",
            data=make_response("error", "Game has already started"),
        )
    else:
        ROOM.add_player(username, sid)
        # Let the player join the room
        sio.enter_room(sid, room=ROOM_ID)
        sio.emit(
            "join-room",
            data=make_response("success", "Successfully entered the lobby"),
            to=sid,
        )

        # Tell the admin a new player joined the room
        sio.emit("user-joined", data={"players": ROOM.get_players()}, to=ROOM.admin_id)
        # Tell the players someone joined the room too
        sio.emit("user-joined", data={"players": ROOM.get_players()}, room=ROOM_ID)

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("get-game-info")
def get_game_info(sid):
    """Send various info to the players once they joined the waiting room

    Args:
        sid (str): the user's socket id
    """
    sio.emit(
        "get-game-info",
        data={
            "players": ROOM.get_players(),
            "settings": ROOM.get_settings(),
            "question": ROOM.questions,
        },
        to=sid,
    )

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("lock-room")
def lock_room(sid):
    """When the admin starts the game which means all the players joined the room

    Args:
        sid (string): the emitter socket id
    """

    # Prevent new user from joining the room
    ROOM.locked = True

    # Send a response to the admin
    sio.emit("lock-room-response", to=sid)

    # Tell the players to be ready
    ROOM.next_question()
    sio.emit("be-ready", data={"question": ROOM.questions}, room=ROOM_ID)

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("get-player-info")
def get_player_info(sid):
    currentPlayer = [p for _, p in ROOM.players.items() if p.sid == sid][0]
    sio.emit(
        "get-player-info",
        data={
            "hearts": ROOM.settings.lives,
            "left": currentPlayer.hearts,
            "timer": ROOM.settings.timer,
            "question": ROOM.questions,
        },
        to=sid,
    )

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("set-question-settings")
def set_question_settings(sid, data: dict):
    """Whenver the admin finish settings up the nex question

    Args:
        sid (str): the emitter's socket id
        data (dict): Data passed alongside the event
    """
    timer = data.get("timer", None)
    answer = data.get("answer", None)

    if not timer:
        sio.emit(
            "set-question-settings-response",
            data=make_response("error", "Unspecified timer value"),
            to=sid,
        )
    elif int(timer) <= 0:
        sio.emit(
            "set-question-settings-response",
            data=make_response("error", "Timer value must be a positive number"),
            to=sid,
        )
    elif answer not in ["A", "B", "C", "D"]:
        sio.emit(
            "set-question-settings-response",
            data=make_response("error", "This answer is not valid"),
            to=sid,
        )
    else:
        ROOM.answer = answer
        ROOM.settings.timer = int(timer)
        # Send the response to the admin
        sio.emit(
            "set-question-settings-response",
            data=make_response("success", "Successfully set settings"),
            to=sid,
        )
        # Send a response the entire room
        sio.emit("question-start", data={"timer": timer}, room=ROOM_ID)

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("user-answer")
def user_answer(sid, data: dict):
    """Whenever a player just answered the question

    Args:
        sid (str): the player's ocket io
        data (dict): Data passed alongside the event
    """
    answer = data.get("answer", None)

    if answer:
        print(f"Someone gave an answer: {answer}")

        # Get the player who just answered
        currentPlayer = [p for _, p in ROOM.players.items() if p.sid == sid][0]
        currentPlayer.answer = answer

        # If the answer is incorrect remove a life if he is still alive
        if answer != ROOM.answer:
            if currentPlayer.hearts > 0:
                currentPlayer.hearts -= 1
        else:
            currentPlayer.add_points(1)

        # Reset the answer given by the player
        # currentPlayer.answer = None

        # Send the answers to the admin
        sio.emit(
            "update-answers",
            data={
                "players": len(ROOM.players),
                "alive": [
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts > 0 and p.answer == "A"
                        ]
                    ),
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts > 0 and p.answer == "B"
                        ]
                    ),
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts > 0 and p.answer == "C"
                        ]
                    ),
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts > 0 and p.answer == "D"
                        ]
                    ),
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts > 0 and p.answer == "X"
                        ]
                    ),
                ],
                "dead": [
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts == 0 and p.answer == "A"
                        ]
                    ),
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts == 0 and p.answer == "B"
                        ]
                    ),
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts == 0 and p.answer == "C"
                        ]
                    ),
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts == 0 and p.answer == "D"
                        ]
                    ),
                    len(
                        [
                            p
                            for _, p in ROOM.players.items()
                            if p.hearts == 0 and p.answer == "X"
                        ]
                    ),
                ],
            },
            to=ROOM.admin_id,
        )

        # Send a response to the player
        sio.emit(
            "user-answer",
            data={
                "correct": answer == ROOM.answer,
                "answer": ROOM.answer,
                "hearts": ROOM.settings.lives,
                "left": currentPlayer.hearts,
            },
            to=sid,
        )
    else:
        print(f"An error occured while answering: '{answer}'")

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("get-user-answer")
def user_answer(sid, data: dict):
    sio.emit(
        "get-update-answers-response",
        data={
            "alive": [
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        if p.hearts > 0 and p.answer == "A"
                    ]
                ),
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        if p.hearts > 0 and p.answer == "B"
                    ]
                ),
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        if p.hearts > 0 and p.answer == "C"
                    ]
                ),
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        if p.hearts > 0 and p.answer == "D"
                    ]
                ),
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        # TODO: Maybe change to None ?
                        if p.hearts > 0 and p.answer == ""
                    ]
                ),
            ],
            "dead": [
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        if p.hearts == 0 and p.answer == "A"
                    ]
                ),
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        if p.hearts == 0 and p.answer == "B"
                    ]
                ),
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        if p.hearts == 0 and p.answer == "C"
                    ]
                ),
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        if p.hearts == 0 and p.answer == "D"
                    ]
                ),
                len(
                    [
                        p
                        for _, p in ROOM.players.items()
                        if p.hearts == 0 and p.answer == None
                    ]
                ),
            ],
        },
        to=ROOM.admin_id,
    )

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("next-question")
def next_question(sid):
    ROOM.next_question()
    sio.emit("next-question", room=ROOM_ID)


@sio.on("invalidate")
def invalidate(sid):
    # Cancel current turn
    for _, p in ROOM.players.items():
        print(f"R: '{ROOM.answer}' & P: '{p.answer}'")
        if p.hearts < ROOM.settings.lives:
            p.cancel_current_turn()

    for _, p in ROOM.players.items():
        print(p.to_dict())

    # Update question progress
    ROOM.next_question()

    # The the admin the invalidation is done
    sio.emit("invalidate", to=sid)

    # Let the players waiting in the waiting room
    sio.emit("next-question", room=ROOM_ID)

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("end-game")
def endgame(sid):
    sio.emit("end-game-response", room=ROOM_ID)

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("get-players")
def get_players(sid):
    sio.emit("get-players-response", data={"players": ROOM.get_players()}, to=sid)

    print(dumps(ROOM.to_dict(), indent=2))


@sio.on("show-leaderboard")
def show_leaderboard(sid):
    """Show the leaderboard to the entire room

    Args:
        sid (str): the emitter's socket id
    """
    sio.emit("show-leaderboard")

    print(dumps(ROOM.to_dict(), indent=2))


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.event
def disconnect(sid):
    print("disconnect ", sid)
    # TODO: Remove disconnected player from the ROOM and emit events


print("Socket server running: 'localhost:3001'")
pywsgi.WSGIServer(("", 3001), app).serve_forever()
