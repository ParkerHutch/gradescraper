from gradescraper.util.messenger import GradescopeMessenger
import pytest

@pytest.mark.dependency(name='auth_token')
@pytest.mark.asyncio
async def test_get_auth_token():
    async with GradescopeMessenger() as messenger:
        response_obj = await messenger.get_auth_token()
        assert response_obj is not ''


@pytest.mark.dependency(depends=['auth_token'])
@pytest.mark.asyncio
async def test_bad_login():
    async with GradescopeMessenger('invalid-address@email.com', 'badPassword') as messenger:
        with pytest.raises(Exception):
            await messenger.login()


