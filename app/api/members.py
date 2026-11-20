from fastapi import APIRouter, status

from app.api.dependencies import MemberRepoDep
from app.api.schemas import MemberCreate, MemberOut
from app.domain.exceptions import MemberNotFoundError
from app.domain.models import Member

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, members: MemberRepoDep) -> MemberOut:
    member = members.add(Member(name=payload.name, email=payload.email))
    return MemberOut.model_validate(member)


@router.get("/{member_id}")
def get_member(member_id: int, members: MemberRepoDep) -> MemberOut:
    member = members.get(member_id)
    if member is None:
        raise MemberNotFoundError(f"Member {member_id} not found")
    return MemberOut.model_validate(member)
