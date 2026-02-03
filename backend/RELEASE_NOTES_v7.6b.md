# RELEASE NOTES — v7.6b (PlayRAG + YouTube Queue + Drive-Mirror Ingest)

Date: 2026-02-03 (KST)

## Added
- YouTube server-side queue (tenant + client session scoped; Redis-backed)
  - sidecar commands: youtube.queue.add / youtube.queue.next / youtube.queue.list / youtube.queue.clear
  - UI auto-sync: server queue becomes source-of-truth; localStorage remains as fallback.
- Folder ingest for Drive-mirror RAG (incremental, mtime-tracked; Redis-backed)
  - sidecar commands: rag.folder.ingest / rag.folder.status
  - Supports pdf/docx/pptx/xlsx/txt/md. HWP requires external conversion (auto-fallback to sibling .pdf/.txt/.md/.docx with same basename).
- Daily RAG auto-ingest scheduler (default 03:00 KST)
  - Controlled by env vars (see Settings section below).
  - Emits AgentReport + Worklog entry on completion.

## Changed
- /sidecar/command now accepts optional client_context.session_id to scope queue/state.

## Settings (env)
- RAG_AUTO_INGEST_ENABLED (default false)
- RAG_AUTO_INGEST_PATH (default /data/gdrive_mirror)
- RAG_AUTO_INGEST_EXTENSIONS (default pdf,docx,pptx,xlsx,txt,md,hwp)
- RAG_AUTO_INGEST_ORG_ID (default default)
- RAG_AUTO_INGEST_PROJECT_ID (default nexus)
- RAG_AUTO_INGEST_HOUR (default 3)
- RAG_AUTO_INGEST_MINUTE (default 0)
- RAG_AUTO_INGEST_MAX_FILES (default 5000)
- RAG_AUTO_INGEST_MAX_FILE_MB (default 50)

## Dependencies
- Added: PyPDF2, python-docx, python-pptx, openpyxl (see nexus_supervisor/requirements.txt)
