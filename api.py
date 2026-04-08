import requests


class ArenaAPIError(RuntimeError):
    def __init__(self, message, *, status_code=None, error_code=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class ArenaAPI:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.request_timeout = 15

    def _handle_json_response(self, response):
        try:
            payload = response.json()
        except ValueError as exc:
            response.raise_for_status()
            raise ArenaAPIError("Server did not return valid JSON.") from exc

        if response.status_code >= 400 or payload.get("error"):
            error_data = payload.get("data", {}) if isinstance(payload, dict) else {}
            error_code = error_data.get("error_code") if isinstance(error_data, dict) else None
            message = error_data.get("msg") if isinstance(error_data, dict) else None
            if not message:
                message = f"HTTP {response.status_code}"
            raise ArenaAPIError(message, status_code=response.status_code, error_code=error_code)

        return payload.get("data")

    def login(self, api_key):
        url = f"{self.base_url}/api/auth/login"
        payload = {"provider": "api_key", "api_key": api_key}
        response = self.session.post(url, json=payload, timeout=self.request_timeout)
        return self._handle_json_response(response)

    def get_stream_response(self, room_id, presence_id):
        url = f"{self.base_url}/api/rooms/{room_id}/stream?presence_id={presence_id}"
        response = self.session.get(
            url,
            stream=True,
            headers={"Accept": "text/event-stream"},
            timeout=(10, 20),
        )
        response.raise_for_status()
        return response

    def send_heartbeat(self, room_id, presence_id):
        url = f"{self.base_url}/api/rooms/{room_id}/heartbeat?presence_id={presence_id}"
        response = self.session.post(url, timeout=self.request_timeout)
        return self._handle_json_response(response)

    def take_seat(self, room_id, seat_color):
        url = f"{self.base_url}/api/rooms/{room_id}/seat"
        response = self.session.post(
            url,
            json={"seat": seat_color},
            timeout=self.request_timeout,
        )
        return self._handle_json_response(response)

    def ready(self, room_id):
        url = f"{self.base_url}/api/rooms/{room_id}/ready"
        response = self.session.post(url, timeout=self.request_timeout)
        return self._handle_json_response(response)

    def make_move(self, room_id, row, col, use_strong):
        url = f"{self.base_url}/api/rooms/{room_id}/move"
        response = self.session.post(
            url,
            json={"row": row, "col": col, "strong": use_strong},
            timeout=self.request_timeout,
        )
        return self._handle_json_response(response)

    def submit_bid(self, room_id, bid_seconds, color_choice):
        url = f"{self.base_url}/api/rooms/{room_id}/human-bid"
        response = self.session.post(
            url,
            json={"bid": bid_seconds, "color": color_choice},
            timeout=self.request_timeout,
        )
        return self._handle_json_response(response)

    def leave_room(self, room_id, presence_id):
        url = f"{self.base_url}/api/rooms/{room_id}/leave?presence_id={presence_id}"
        response = self.session.post(url, timeout=self.request_timeout)
        return self._handle_json_response(response)
