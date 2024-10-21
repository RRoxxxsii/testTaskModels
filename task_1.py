import datetime
from typing import Annotated

from sqlalchemy import (
    BigInteger,
    Identity,
    func,
    DateTime,
    String,
    Integer,
    ForeignKey
)
from sqlalchemy.orm import (
    mapped_column,
    DeclarativeBase,
    Mapped
)

intpk = Annotated[  # noqa
    int,
    mapped_column(BigInteger, Identity(start=1, cycle=True), primary_key=True),
]


class AbstractModel(DeclarativeBase):
    _repr_cols_num: int = 3
    _repr_cols: tuple = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self._repr_cols or idx < self._repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class Player(AbstractModel):
    __tablename__ = "players"

    username: Mapped[str] = mapped_column(
        String(50), unique=True, doc="Имя пользователя"
    )
    points: Mapped[int] = mapped_column(
        Integer, default=0
    )
    first_login: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    last_login: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=None
    )

# отследить момент первого входа можно через поле first_login модели Player,
# если во время процедуры входа в аккаунт у пользователя значение этого поля как None,
# в таком случае вход расценивается как первый


class Boost(AbstractModel):
    __tablename__ = "boosters"

    name: Mapped[str] = mapped_column(String(50), doc="Название буста")
    description: Mapped[str] = mapped_column(String)
    boost_type: Mapped[str] = mapped_column(String(50), doc="Тип буста")


class PlayerBoost(AbstractModel):
    __tablename__ = "player_boosts"

    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"))
    boost_id: Mapped[int] = mapped_column(Integer, ForeignKey("boosts.id"))

    obtained_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    expires_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
