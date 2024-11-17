import pytest
import datetime
from demo.database.models.application import Application
from demo.database.models.owner import Owner
from actual_orm.query_builder.query_builder import OrderByDirection
from actual_orm import get_connection

pytestmark = pytest.mark.asyncio(loop_scope="module")


async def test_create(db):

    app = await Application.create({"external_id": "external", "title": "title"})
    assert app.id != None
    assert app.external_id == "external"
    assert app.title == "title"
    assert app.created_at != None
    assert app.updated_at != None


async def test_get(db):
    created_app = await Application.create({"external_id": "external", "title": "asdf"})
    app = await Application.get(Application.columns.id == created_app.id)
    assert app != None
    assert app.id == created_app.id
    assert app.external_id == "external"


async def test_update(db):
    app = await Application.get(Application.columns.id == 1)
    assert app != None
    apps = await Application.update(
        {"title": "New Title"}, Application.columns.id == app.id
    )
    assert apps[0].title == "New Title"


async def test_update_self(db):
    app = await Application.create(
        {"external_id": "test_update_self", "title": "title"}
    )
    app.title = "new title"
    await app.update_self()
    app = await Application.get(Application.columns.id == app.id)
    assert app != None
    assert app.title == "new title"


async def test_delete(db):
    app = await Application.create({"external_id": "id", "title": "title"})
    await Application.delete(Application.columns.id == app.id)
    app = await Application.get(Application.columns.id == app.id)
    assert app == None


# async def test_upsert(db):
#     app = Application(
#         id=None, external_id="external", title="title", created_at=None, updated_at=None
#     )
#     app = await Application.create(app)
#     owner = Owner(
#         id=None,
#         application_id=app.id,
#         external_id="external",
#         created_at=datetime.datetime.fromisoformat("2024-11-13"),
#         updated_at=datetime.datetime.fromisoformat("2024-11-13"),
#     )
#     owner = await Owner.upsert(owner)
#     assert owner.id != None
#     id = owner.id
#     old_updated_time = owner.updated_at
#     new_created_time = datetime.datetime.now(datetime.timezone.utc)
#     new_created_time = new_created_time.replace(
#         microsecond=(new_created_time.microsecond // 1000) * 1000
#     )
#     owner.created_at = new_created_time
#     owner.id = None
#     owner = await Owner.upsert(owner)
#     assert owner.id == id
#     assert owner.updated_at > old_updated_time
#     assert owner.created_at == new_created_time


async def test_select(db):
    app = await Application.create({"external_id": "asdf", "title": "asdf"})
    [selected_app] = (
        await Application.builder()
        .select()
        .where(Application.columns.id == app.id)
        .run()
    )
    assert app.id == selected_app.id


async def test_order_by(db):
    app_one = await Application.create(
        {
            "external_id": "external",
            "title": "title",
            "created_at": datetime.datetime.fromisoformat("2024-11-13"),
        }
    )
    app_two = await Application.create(
        {
            "external_id": "external",
            "title": "title",
            "created_at": datetime.datetime.fromisoformat("2024-11-14"),
        }
    )

    apps = await Application.query(
        condition=Application.columns.id.in_([app_one.id, app_two.id]),
        order_by=[(Application.columns.created_at, OrderByDirection.ASC)],
    )
    assert apps[0].id == app_one.id
    assert apps[1].id == app_two.id

    apps = await Application.query(
        condition=Application.columns.id.in_([app_one.id, app_two.id]),
        order_by=[(Application.columns.created_at, OrderByDirection.DESC)],
    )
    assert apps[0].id == app_two.id
    assert apps[1].id == app_one.id


async def test_join(db):
    app = await Application.create({"external_id": "external", "title": "title"})
    assert app != None
    owner = await Owner.create({"external_id": "external", "application_id": app.id})

    owners = (
        await Owner.builder()
        .select(Owner.__table_name__)
        .distinct()
        .inner_join(
            Application.__table_name__,
            Application.columns.id == Owner.columns.application_id,
        )
        .where(Application.columns.id == app.id)
        .run()
    )
    assert len(owners) == 1
    assert owners[0].id == owner.id


async def test_upsert(db):
    external_id = "test_upsert"
    created_app = await Application.upsert(
        where=Application.columns.external_id == external_id,
        create={"external_id": external_id, "title": "Created"},
        update={"title": "Updated"},
    )
    assert created_app.title == "Created"

    updated_app = await Application.upsert(
        where=Application.columns.external_id == external_id,
        create={"external_id": external_id, "title": "Create"},
        update={"title": "Updated"},
    )

    assert updated_app.id == created_app.id
    assert updated_app.title == "Updated"
