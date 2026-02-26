"""Forge client implementation."""

from __future__ import annotations

from typing import Sequence, Union

import httpx

from forge_sdk.error import ForgeConnectionError, ForgeServerError
from forge_sdk.types import DitherMethod, Flow, Orientation, OutputFormat, Palette


class ForgeClient:
    """Client for a Forge rendering server.

    Maintains a connection pool for efficient request reuse. Use as a context
    manager for proper cleanup, or call :meth:`close` when done.

    Async usage::

        async with ForgeClient("http://localhost:3000") as client:
            pdf = await client.render_html("<h1>Hello</h1>").format(OutputFormat.PDF).send()

    Sync usage::

        with ForgeClient("http://localhost:3000") as client:
            pdf = client.render_html("<h1>Hello</h1>").format(OutputFormat.PDF).send_sync()

    Without context manager::

        client = ForgeClient("http://localhost:3000")
        pdf = client.render_html("<h1>Hello</h1>").format(OutputFormat.PDF).send_sync()
        client.close()
    """

    def __init__(self, base_url: str, *, timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

    def _get_sync_client(self) -> httpx.Client:
        if self._sync_client is None or self._sync_client.is_closed:
            self._sync_client = httpx.Client(timeout=self._timeout)
        return self._sync_client

    def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(timeout=self._timeout)
        return self._async_client

    def close(self) -> None:
        """Close underlying HTTP connections."""
        if self._sync_client is not None and not self._sync_client.is_closed:
            self._sync_client.close()
        if self._async_client is not None and not self._async_client.is_closed:
            # Can't await in sync context; best-effort close.
            try:
                import asyncio
                loop = asyncio.get_running_loop()
                loop.create_task(self._async_client.aclose())
            except RuntimeError:
                pass

    async def aclose(self) -> None:
        """Close underlying HTTP connections (async)."""
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()
        if self._sync_client is not None and not self._sync_client.is_closed:
            self._sync_client.close()

    def __enter__(self) -> ForgeClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    async def __aenter__(self) -> ForgeClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    def render_html(self, html: str) -> RenderRequestBuilder:
        """Start a render request from an HTML string."""
        return RenderRequestBuilder(self, html=html)

    def render_url(self, url: str) -> RenderRequestBuilder:
        """Start a render request from a URL."""
        return RenderRequestBuilder(self, url=url)

    async def health(self) -> bool:
        """Check if the server is healthy (async)."""
        try:
            resp = await self._get_async_client().get(f"{self._base_url}/health")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    def health_sync(self) -> bool:
        """Check if the server is healthy (sync)."""
        try:
            resp = self._get_sync_client().get(f"{self._base_url}/health")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False


class RenderRequestBuilder:
    """Builder for a render request.

    Created via :meth:`ForgeClient.render_html` or :meth:`ForgeClient.render_url`.
    Call :meth:`send` (async) or :meth:`send_sync` (sync) to execute.
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
        self._pdf_title: str | None = None
        self._pdf_author: str | None = None
        self._pdf_subject: str | None = None
        self._pdf_keywords: str | None = None
        self._pdf_creator: str | None = None
        self._pdf_bookmarks: bool | None = None

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

    def pdf_title(self, t: str) -> RenderRequestBuilder:
        """PDF document title metadata."""
        self._pdf_title = t
        return self

    def pdf_author(self, a: str) -> RenderRequestBuilder:
        """PDF document author metadata."""
        self._pdf_author = a
        return self

    def pdf_subject(self, s: str) -> RenderRequestBuilder:
        """PDF document subject metadata."""
        self._pdf_subject = s
        return self

    def pdf_keywords(self, k: str) -> RenderRequestBuilder:
        """PDF document keywords (comma-separated)."""
        self._pdf_keywords = k
        return self

    def pdf_creator(self, c: str) -> RenderRequestBuilder:
        """PDF creator tool metadata."""
        self._pdf_creator = c
        return self

    def pdf_bookmarks(self, b: bool) -> RenderRequestBuilder:
        """Enable or disable PDF bookmarks/outline generation."""
        self._pdf_bookmarks = b
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

        has_pdf = (
            self._pdf_title is not None
            or self._pdf_author is not None
            or self._pdf_subject is not None
            or self._pdf_keywords is not None
            or self._pdf_creator is not None
            or self._pdf_bookmarks is not None
        )
        if has_pdf:
            p: dict = {}
            if self._pdf_title is not None:
                p["title"] = self._pdf_title
            if self._pdf_author is not None:
                p["author"] = self._pdf_author
            if self._pdf_subject is not None:
                p["subject"] = self._pdf_subject
            if self._pdf_keywords is not None:
                p["keywords"] = self._pdf_keywords
            if self._pdf_creator is not None:
                p["creator"] = self._pdf_creator
            if self._pdf_bookmarks is not None:
                p["bookmarks"] = self._pdf_bookmarks
            payload["pdf"] = p

        return payload

    async def send(self) -> bytes:
        """Send the render request and return raw output bytes (async)."""
        payload = self._build_payload()
        try:
            resp = await self._client._get_async_client().post(
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
            resp = self._client._get_sync_client().post(
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
