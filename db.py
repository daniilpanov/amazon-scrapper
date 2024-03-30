import settings
from peewee import CharField, ForeignKeyField, AutoField, Model, MySQLDatabase

conn = MySQLDatabase(
    settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASS,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
)
conn.connect()


def NotIncrementingAutoField():
    field = AutoField()
    field.auto_increment = False
    return field


class BaseModel(Model):
    class Meta:
        database = conn


class Department(BaseModel):
    class Meta:
        table_name = 'departments'

    id = AutoField()
    parent_id = ForeignKeyField('self', backref='departments', null=True)
    name = CharField(255)
    url = CharField(1000)
    items: list

    def __init__(self, *args, **kwargs):
        self.items = []
        super().__init__(*args, **kwargs)
