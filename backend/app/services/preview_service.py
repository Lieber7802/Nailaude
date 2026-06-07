"""
Preview Service - Static file hosting for iframe previews.
"""
import asyncio
import json
import mimetypes
import os
import re
import socket
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.services.workspace_paths import resolve_workspace_path


PREVIEW_CSP = (
    "default-src 'self' data: blob: https:; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
    "style-src 'self' 'unsafe-inline' https:; "
    "img-src 'self' data: blob: https:; "
    "font-src 'self' data: https:; "
    "connect-src 'self' https: ws: wss:; "
    "frame-ancestors 'self'"
)


class PreviewService:
    """Hosts project files for preview in the frontend."""

    _vite_servers: dict[Path, tuple[int, asyncio.subprocess.Process]] = {}

    @classmethod
    async def shutdown_dev_servers(cls) -> None:
        """Stop dev servers spawned for workspace previews."""
        servers = list(cls._vite_servers.values())
        cls._vite_servers.clear()
        for _, process in servers:
            if process.returncode is not None:
                continue
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=2)
            except TimeoutError:
                process.kill()
                await process.wait()

    async def get_preview_url(self, conversation_id: str, file_path: str) -> str:
        """Generate a preview URL for a file."""
        safe_path = file_path.replace("\\", "/").lstrip("/")
        return f"/preview/{conversation_id}/{safe_path}"

    async def serve_file(self, conversation_id: str, file_path: str, work_dir: str | None = None) -> bytes:
        """Read and return file content for preview."""
        if not work_dir:
            raise FileNotFoundError(f"No preview root for conversation {conversation_id}")
        path = self._resolve_preview_path(work_dir, file_path)
        return path.read_bytes()

    async def file_response(self, db: AsyncSession, conversation_id: str, file_path: str) -> FileResponse | Response:
        """Return a raw static file response for the preview route."""
        conversation = await db.get(Conversation, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        root = resolve_workspace_path(conversation.work_dir)
        headers = {
            "Content-Security-Policy": PREVIEW_CSP,
            "X-Content-Type-Options": "nosniff",
        }

        if self._should_proxy_vite_dev_server(root, file_path):
            status_code, body, proxy_media_type = await self._proxy_vite_dev_server(root, conversation_id, file_path)
            if self._is_rewritable_media_type(proxy_media_type):
                body = self._rewrite_preview_absolute_urls(
                    body.decode("utf-8", errors="replace"),
                    conversation_id,
                ).encode("utf-8")
            return Response(body, status_code=status_code, media_type=proxy_media_type, headers=headers)

        path = self._resolve_preview_path(conversation.work_dir, file_path)
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Preview file not found")

        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if media_type == "text/html":
            html = path.read_text(encoding="utf-8", errors="replace")
            return Response(
                self._rewrite_html_asset_urls(html, conversation_id, file_path),
                media_type=media_type,
                headers=headers,
            )

        return FileResponse(
            path,
            media_type=media_type,
            headers=headers,
        )

    def _resolve_preview_path(self, work_dir: str, file_path: str) -> Path:
        root = resolve_workspace_path(work_dir)
        requested = (root / file_path.replace("\\", "/").lstrip("/")).resolve()
        if not requested.is_relative_to(root):
            raise HTTPException(status_code=403, detail="Preview path escapes the workspace")
        return requested

    def _rewrite_html_asset_urls(self, html: str, conversation_id: str, file_path: str) -> str:
        safe_file_path = file_path.replace("\\", "/").lstrip("/")
        preview_dir = str(Path(safe_file_path).parent).replace("\\", "/")
        preview_prefix = f"/preview/{conversation_id}"
        if preview_dir and preview_dir != ".":
            preview_prefix = f"{preview_prefix}/{preview_dir}"

        def replace(match: re.Match[str]) -> str:
            attr = match.group("attr")
            quote = match.group("quote")
            url = match.group("url")
            if url.startswith("/preview/"):
                return match.group(0)
            return f"{attr}{quote}{preview_prefix}{url}{quote}"

        return re.sub(
            r"(?P<attr>\b(?:src|href)=)(?P<quote>['\"])(?P<url>/(?!/)[^'\"]+)(?P=quote)",
            replace,
            html,
        )

    def _should_proxy_vite_dev_server(self, root: Path, file_path: str) -> bool:
        safe_path = file_path.replace("\\", "/").lstrip("/")
        if safe_path.split("/", 1)[0] in {"dist", "build"}:
            return False
        package_json = root / "package.json"
        if not package_json.is_file():
            return False
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False
        scripts = package.get("scripts") or {}
        dev_script = str(scripts.get("dev") or "")
        dependencies = {
            **(package.get("dependencies") or {}),
            **(package.get("devDependencies") or {}),
        }
        return "vite" in dev_script or "vite" in dependencies

    async def _proxy_vite_dev_server(
        self,
        root: Path,
        conversation_id: str,
        file_path: str,
    ) -> tuple[int, bytes, str]:
        port = await self._ensure_vite_dev_server(root)
        safe_path = file_path.replace("\\", "/").lstrip("/") or "index.html"
        url = f"http://127.0.0.1:{port}/{safe_path}"
        try:
            return await asyncio.to_thread(self._fetch_url, url)
        except HTTPError as exc:
            media_type = exc.headers.get_content_type() if exc.headers else "text/plain"
            return exc.code, exc.read(), media_type
        except URLError as exc:
            raise HTTPException(status_code=502, detail=f"Vite preview server unavailable: {exc.reason}") from exc

    async def _ensure_vite_dev_server(self, root: Path) -> int:
        cached = self._vite_servers.get(root)
        if cached:
            port, process = cached
            if process.returncode is None:
                return port
            self._vite_servers.pop(root, None)

        port = self._free_port()
        env = {**os.environ, "BROWSER": "none"}
        process = await asyncio.create_subprocess_exec(
            "npm",
            "run",
            "dev",
            "--",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            cwd=root,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self._vite_servers[root] = (port, process)
        await self._wait_for_vite_server(root, port, process)
        return port

    async def _wait_for_vite_server(self, root: Path, port: int, process: asyncio.subprocess.Process) -> None:
        url = f"http://127.0.0.1:{port}/"
        for _ in range(80):
            if process.returncode is not None:
                self._vite_servers.pop(root, None)
                output = b""
                if process.stdout:
                    output = await process.stdout.read()
                detail = output.decode("utf-8", errors="replace").strip() or "npm run dev exited"
                raise HTTPException(status_code=502, detail=f"Vite preview server failed: {detail}")
            try:
                await asyncio.to_thread(self._fetch_url, url)
                return
            except (HTTPError, URLError):
                await asyncio.sleep(0.1)
        raise HTTPException(status_code=504, detail="Timed out starting Vite preview server")

    def _fetch_url(self, url: str) -> tuple[int, bytes, str]:
        request = Request(url, headers={"Accept": "*/*"})
        with urlopen(request, timeout=3) as response:
            media_type = response.headers.get_content_type() or "application/octet-stream"
            return response.status, response.read(), media_type

    def _free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def _is_rewritable_media_type(self, media_type: str) -> bool:
        return (
            media_type.startswith("text/")
            or media_type in {"application/javascript", "application/json"}
            or media_type.endswith("+json")
        )

    def _rewrite_preview_absolute_urls(self, content: str, conversation_id: str) -> str:
        preview_prefix = f"/preview/{conversation_id}"

        def replace(match: re.Match[str]) -> str:
            prefix = match.group("prefix")
            quote = match.group("quote")
            url = match.group("url")
            if url.startswith("/preview/"):
                return match.group(0)
            return f"{prefix}{quote}{preview_prefix}{url}{quote}"

        content = re.sub(
            r"(?P<prefix>\b(?:src|href)=)(?P<quote>['\"])(?P<url>/(?!/)[^'\"]+)(?P=quote)",
            replace,
            content,
        )
        return re.sub(
            r"(?P<prefix>(?:from\s+|import\s*\(?\s*|url\(\s*))(?P<quote>['\"]?)(?P<url>/(?!/)[^'\"\)\s;]+)(?P=quote)",
            replace,
            content,
        )
