import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_block import DocumentBlock
from app.models.section_comment import SectionComment
from app.schemas.document import (
    CommentCreate,
    CommentRead,
    DocumentAutosaveRequest,
    DocumentBlockRead,
)


async def get_blocks(db: AsyncSession, project_id: str) -> list[DocumentBlockRead]:
    result = await db.execute(
        select(DocumentBlock)
        .where(DocumentBlock.project_id == project_id)
        .order_by(DocumentBlock.order_index.asc(), DocumentBlock.created_at.asc())
    )
    return [_block_read(block) for block in result.scalars().all()]


async def autosave_blocks(db: AsyncSession, project_id: str, body: DocumentAutosaveRequest) -> list[DocumentBlockRead]:
    await db.execute(delete(DocumentBlock).where(DocumentBlock.project_id == project_id))
    blocks = []
    for index, item in enumerate(body.blocks):
        block = DocumentBlock(
            id=str(uuid.uuid4()),
            project_id=project_id,
            section_key=item.section_key,
            heading=item.heading,
            block_type=item.block_type,
            content=item.content,
            order_index=item.order_index if item.order_index is not None else index,
            metadata_json=item.metadata_json,
        )
        db.add(block)
        blocks.append(block)
    await db.flush()
    for block in blocks:
        await db.refresh(block)
    return [_block_read(block) for block in blocks]


async def sync_blocks_from_sections(db: AsyncSession, project_id: str, sections: list[dict]) -> list[DocumentBlockRead]:
    body = DocumentAutosaveRequest(
        blocks=[
            {
                "section_key": section.get("key", ""),
                "heading": section.get("heading", ""),
                "block_type": "finance" if section.get("key") == "financial_forecast" else "text",
                "content": section.get("content", ""),
                "order_index": index,
                "metadata_json": {},
            }
            for index, section in enumerate(sections)
        ]
    )
    return await autosave_blocks(db, project_id, body)


async def create_comment(db: AsyncSession, project_id: str, section_id: str, body: CommentCreate) -> CommentRead:
    comment = SectionComment(
        id=str(uuid.uuid4()),
        project_id=project_id,
        section_id=section_id,
        author=body.author,
        body=body.body,
        mention=body.mention,
        status="open",
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return _comment_read(comment)


async def list_comments(db: AsyncSession, project_id: str, section_id: str | None = None) -> list[CommentRead]:
    stmt = select(SectionComment).where(SectionComment.project_id == project_id)
    if section_id:
        stmt = stmt.where(SectionComment.section_id == section_id)
    stmt = stmt.order_by(SectionComment.created_at.asc())
    result = await db.execute(stmt)
    return [_comment_read(comment) for comment in result.scalars().all()]


async def resolve_comment(db: AsyncSession, project_id: str, comment_id: str, status: str) -> CommentRead | None:
    result = await db.execute(
        select(SectionComment).where(SectionComment.project_id == project_id, SectionComment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        return None
    comment.status = status
    await db.flush()
    await db.refresh(comment)
    return _comment_read(comment)


def _block_read(block: DocumentBlock) -> DocumentBlockRead:
    return DocumentBlockRead(
        id=block.id,
        project_id=block.project_id,
        section_key=block.section_key,
        heading=block.heading,
        block_type=block.block_type,
        content=block.content,
        order_index=block.order_index,
        metadata_json=block.metadata_json,
        created_at=block.created_at,
        updated_at=block.updated_at,
    )


def _comment_read(comment: SectionComment) -> CommentRead:
    return CommentRead(
        id=comment.id,
        project_id=comment.project_id,
        section_id=comment.section_id,
        author=comment.author,
        body=comment.body,
        status=comment.status,
        mention=comment.mention,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )
