from typing import Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domains.identity.models import Role, Permission, UserRole, RolePermission


class RBACService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_or_create_permission(self, name: str, description: str = "") -> Permission:
        q = await self.db.execute(select(Permission).where(Permission.name == name))
        perm = q.scalars().first()
        if perm: return perm
        perm = Permission(name=name, description=description)
        self.db.add(perm)
        await self.db.flush()
        return perm

    async def _get_or_create_role(self, name: str, description: str = "") -> Role:
        q = await self.db.execute(select(Role).where(Role.name == name))
        role = q.scalars().first()
        if role: return role
        role = Role(name=name, description=description)
        self.db.add(role)
        await self.db.flush()
        return role

    async def seed_roles_and_permissions(self) -> None:
        perms = {
            "questions.read": "Read questions", "questions.create": "Create questions",
            "questions.update": "Update questions", "questions.delete": "Delete questions",
            "questions.publish": "Publish questions", "tests.read": "Read tests",
            "tests.create": "Create tests", "profile.read": "Read profile",
            "profile.update": "Update profile", "analytics.read": "Read analytics",
            "recovery.read": "Read recovery", "taxonomy.read": "Read taxonomy",
            "subject.read": "Read subjects", "subject.create": "Create subjects",
            "subject.update": "Update subjects", "subject.delete": "Delete subjects",
        }

        role_perms = {
            "student": ["questions.read", "tests.read", "tests.create", "profile.read", "profile.update", "analytics.read", "recovery.read", "subject.read"],
            "teacher": ["questions.read", "tests.read", "tests.create", "profile.read", "profile.update", "analytics.read", "recovery.read", "questions.create", "questions.update", "questions.publish", "taxonomy.read", "subject.read", "subject.create", "subject.update", "subject.delete"],
            "admin": list(perms.keys()),
        }

        perm_objs = {name: await self._get_or_create_permission(name, desc) for name, desc in perms.items()}

        for role_name, perm_names in role_perms.items():
            role = await self._get_or_create_role(role_name)
            for pname in perm_names:
                p = perm_objs[pname]
                q = await self.db.execute(select(RolePermission).where(RolePermission.role_id == role.id, RolePermission.permission_id == p.id))
                if not q.scalars().first():
                    rp = RolePermission(role_id=role.id, permission_id=p.id)
                    self.db.add(rp)
        await self.db.flush()

    async def assign_role(self, user_id, role_name: str) -> None:
        role_q = await self.db.execute(select(Role).where(Role.name == role_name))
        role = role_q.scalars().first()
        if not role:
            role = Role(name=role_name)
            self.db.add(role)
            await self.db.flush()

        q = await self.db.execute(select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role.id))
        if q.scalars().first(): return
        ur = UserRole(user_id=user_id, role_id=role.id)
        self.db.add(ur)
        await self.db.flush()

    async def has_permission(self, user_id, resource: str, action: str) -> bool:
        """Evaluate permissions efficiently in a single DB query."""
        perm_name = f"{resource}.{action}"
        
        stmt = (
            select(Role.id)
            .join(UserRole, UserRole.role_id == Role.id)
            .outerjoin(RolePermission, RolePermission.role_id == Role.id)
            .outerjoin(Permission, Permission.id == RolePermission.permission_id)
            .where(
                UserRole.user_id == user_id,
                (Role.name == "admin") | (Permission.name == perm_name)
            )
            .limit(1)
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None