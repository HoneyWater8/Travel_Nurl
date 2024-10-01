import httpx
import pytest


@pytest.mark.asyncio
async def test_upload_file():
    user_id = "test_user"
    file_path = "app/AI/test2.jfif"  # 테스트할 이미지 파일 경로
    url = "http://localhost:8000/upload/"

    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            response = await client.post(
                url, data={"user_id": user_id}, files={"file": f}
            )

    print(response.json())  # 응답 출력
    assert response.status_code == 200  # 응답 상태 코드 확인
    assert "img_url" in response.json()  # 응답 JSON에 'img_url'이 포함되어 있는지 확인
