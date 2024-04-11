from sqlalchemy import BigInteger, ForeignKey, Text, String, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config_reader import config

database_url = f'postgresql+asyncpg://{config.postgres_user.get_secret_value()}:{config.postgres_password.get_secret_value()}@'
database_url+= f'{config.postgres_host.get_secret_value()}:{config.postgres_port.get_secret_value()}/{config.postgres_db.get_secret_value()}'

engine = create_async_engine(database_url, echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    subcategories: Mapped[list["Subcategory"]] = relationship(backref="category")

    def __repr__(self):
        return self.name


class Subcategory(Base):
    __tablename__ = "subcategories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'))

    def __repr__(self):
        return self.name


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    photo: Mapped[str] = mapped_column()  # Assuming you'll store the path to the image
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(default=1)
    subcategory_id: Mapped[int] = mapped_column(ForeignKey('subcategories.id'))
    subcategory: Mapped["Subcategory"] = relationship(backref="products")

    def __repr__(self):
        return self.name


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    username: Mapped[str] = mapped_column()

    def __repr__(self):
        return self.name


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(String(32))
    cart_items: Mapped["CartItem"] = relationship(backref="user", uselist=True)

    def __repr__(self):
        return f"{self.id} ({self.username})"


class CartItem(Base):
    __tablename__ = "cart_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(default=1)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product: Mapped["Product"] = relationship(backref="cart_items")

    @property
    def total_price(self):
        return self.quantity * self.product.price

    def __repr__(self):
        return f"CartItem(product={self.product.name}, quantity={self.quantity})"


class QuestionAnswer(Base):
    __tablename__ = "question_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"QuestionAnswer(id={self.id}, question='{self.question}', answer='{self.answer}')"
