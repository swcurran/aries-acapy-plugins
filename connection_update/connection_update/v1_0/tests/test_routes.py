from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.connections.models.conn_record import ConnRecord
from aries_cloudagent.core.in_memory.profile import InMemoryProfile

from .. import routes as test_module


class TestRoutes(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.session_inject = {}
        self.profile = InMemoryProfile.test_profile(
            settings={
                "admin.admin_api_key": "admin_api_key",
                "admin.admin_insecure_mode": False,
            }
        )
        self.context = AdminRequestContext.test_context(self.session_inject, self.profile)
        self.request_dict = {
            "context": self.context,
            "outbound_message_router": AsyncMock(),
        }
        self.request = MagicMock(
            app={},
            match_info={},
            query={},
            __getitem__=lambda _, k: self.request_dict[k],
            headers={"x-api-key": "admin_api_key"}
        )
        self.test_conn_id = "connection-id"

    @patch.object(ConnRecord, "retrieve_by_id")
    async def test_connections_update_saves_with_alias_from_body(self, mock_retrieve):
        self.request.json = AsyncMock()
        self.request.json.return_value = {"alias": "test-alias"}
        self.request.match_info = {"conn_id": self.test_conn_id}

        mock_retrieve.return_value = AsyncMock(
            save=AsyncMock(), alias="", serialize=lambda: {}
        )

        await test_module.connections_update(self.request)

        mock_retrieve.return_value.save.assert_called
        assert mock_retrieve.return_value.alias == "test-alias"

    async def test_register(self):
        mock_app = MagicMock()
        mock_app.add_routes = MagicMock()

        await test_module.register(mock_app)
        mock_app.add_routes.assert_called()
