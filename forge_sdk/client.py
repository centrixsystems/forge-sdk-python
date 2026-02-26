"""Forge client implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Union

import httpx

from forge_sdk.error import ForgeConnectionError, ForgeServerError
from forge_sdk.types import DitherMethod, Flow, Orientation, OutputFormat, Palette

if TYPE_CHECKING:
    pass


class ForgeClient:
    """Client for a Forge rendering server.

    Usage::

        client = ForgeClient("http://localhost:3000")

        # Async
        pdf = await client.render_html("<h1>Hello</h1>").format(OutputFormat.PDF).send()

        # Sync
        pdf = client.render_html("<h1>Hello</h1>").format(OutputFormat.PDF).send_sync()
    """

    def __init__(self, base_url: str, *, timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def render_html(self, html: str) -> RenderRequestBuilder:
        """Start a render request from an HTML string."""
        return RenderRequestBuilder(self, html=html)

    def render_url(self, url: str) -> RenderRequestBuilder:
        """Start a render request from a URL."""
        return RenderRequestBuilder(self, url=url)

    async def health(self) -> bool:
        """Check if the server is healthy (async)."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(f"{self._base_url}/health")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    def health_sync(self) -> bool:
        """Check if the server is healthy (sync)."""
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(f"{self._base_url}/health")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False


class RenderRequestBuilder:
    """Builder for a render request.

    Created via :meth:`ForgeClient.render_html` or :meth:`ForgeClient.render_url`.
    """

    def __init__(
        self,
        client: ForgeClient,
        *,
        html: str | None = None,
        url: str | None = None,
    ) -> None:
        self._client = client
        self._html = html
        self._url = url
        self._format: OutputFormat = OutputFormat.PDF
        self._width: int | None = None
        self._height: int | None = None
        self._paper: str | None = None
        self._orientation: Orientation | None = None
        self._margins: str | None = None
        self._flow: Flow | None = None
        self._density: float | None = None
        self._background: str | None = None
        self._timeout: int | None = None
        self._colors: int | None = None
        self._palette: Union[Palette, list[str], None] = None
        self._dither: DitherMethod | None = None

    def format(self, fmt: OutputFormat) -> RenderRequestBuilder:
        """Output format (default: PDF)."""
        self._format = fmt
        return self

    def width(self, px: int) -> RenderRequestBuilder:
        """Viewport width in CSS pixels."""
        self._width = px
        return self

    def height(self, px: int) -> RenderRequestBuilder:
        """Viewport height in CSS pixels."""
        self._height = px
        return self

    def paper(self, size: str) -> RenderRequestBuilder:
        """Paper size: a3, a4, a5, b4, b5, letter, legal, ledger."""
        self._paper = size
        return self

    def orientation(self, o: Orientation) -> RenderRequestBuilder:
        """Page orientation."""
        self._orientation = o
        return self

    def margins(self, m: str) -> RenderRequestBuilder:
        """Margins preset or 'T,R,B,L' in mm."""
        self._margins = m
        return self

    def flow(self, f: Flow) -> RenderRequestBuilder:
        """Document flow mode."""
        self._flow = f
        return self

    def density(self, dpi: float) -> RenderRequestBuilder:
        """Output DPI (default: 96)."""
        self._density = dpi
        return self

    def background(self, color: str) -> RenderRequestBuilder:
        """Background CSS color."""
        self._background = color
        return self

    def timeout(self, seconds: int) -> RenderRequestBuilder:
        """Page load timeout in seconds."""
        self._timeout = seconds
        return self

    def colors(self, n: int) -> RenderRequestBuilder:
        """Number of colors for quantization (2-256)."""
        self._colors = n
        return self

    def palette(self, p: Union[Palette, Sequence[str]]) -> RenderRequestBuilder:
        """Color palette preset or list of hex color strings."""
        if isinstance(p, Palette):
            self._palette = p
        else:
            self._palette = list(p)
        return self

    def dither(self, method: DitherMethod) -> RenderRequestBuilder:
        """Dithering algorithm."""
        self._dither = method
        return self

    def _build_payload(self) -> dict:
        payload: dict = {"format": self._format.value}

        if self._html is not None:
            payload["html"] = self._html
        if self._url is not None:
            payload["url"] = self._url
        if self._width is not None:
            payload["width"] = self._width
        if self._height is not None:
            payload["height"] = self._height
        if self._paper is not None:
            payload["paper"] = self._paper
        if self._orientation is not None:
            payload["orientation"] = self._orientation.value
        if self._margins is not None:
            payload["margins"] = self._margins
        if self._flow is not None:
            payload["flow"] = self._flow.value
        if self._density is not None:
            payload["density"] = self._density
        if self._background is not None:
            payload["background"] = self._background
        if self._timeout is not None:
            payload["timeout"] = self._timeout

        has_quantize = (
            self._colors is not None
            or self._palette is not None
            or self._dither is not None
        )
        if has_quantize:
            q: dict = {}
            if self._colors is not None:
                q["colors"] = self._colors
            if self._palette is not None:
                if isinstance(self._palette, Palette):
                    q["palette"] = self._palette.value
                else:
                    q["palette"] = self._palette
            if self._dither is not None:
                q["dither"] = self._dither.value
            payload["quantize"] = q

        return payload

    async def send(self) -> bytes:
        """Send the render request and return raw output bytes (async)."""
        payload = self._build_payload()
        try:
            async with httpx.AsyncClient(timeout=self._client._timeout) as client:
                resp = await client.post(
                    f"{self._client._base_url}/render", json=payload
                )
        except httpx.HTTPError as e:
            raise ForgeConnectionError(e) from e

        if resp.status_code != 200:
            try:
                body = resp.json()
                message = body.get("error", f"HTTP {resp.status_code}")
            except Exception:
                message = f"HTTP {resp.status_code}"
            raise ForgeServerError(resp.status_code, message)

        return resp.content

    def send_sync(self) -> bytes:
        """Send the render request and return raw output bytes (sync)."""
        payload = self._build_payload()
        try:
            with httpx.Client(timeout=self._client._timeout) as client:
                resp = client.post(
                    f"{self._client._base_url}/render", json=payload
                )
        except httpx.HTTPError as e:
            raise ForgeConnectionError(e) from e

        if resp.status_code != 200:
            try:
                body = resp.json()
                message = body.get("error", f"HTTP {resp.status_code}")
            except Exception:
                message = f"HTTP {resp.status_code}"
            raise ForgeServerError(resp.status_code, message)

        return resp.content
