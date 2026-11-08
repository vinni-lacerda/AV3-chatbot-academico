"""Caso de uso: Registrar novo usuário com perfis de acesso (RF01)."""

from application.dtos.auth_dtos import RegisterUserInput, UserOutput
from domain.entities.user import User, UserRole
from domain.exceptions.domain_exceptions import UserAlreadyExistsError, ValidationError
from domain.repositories.user_repository import IUserRepository
from domain.services.password_hasher import IPasswordHasher


class RegisterUserUseCase:
    """Responsabilidade única (SRP): Orquestrar o cadastro de um integrante."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(self, data: RegisterUserInput) -> UserOutput:
        if len(data.password) < 8:
            raise ValidationError("A senha deve possuir no mínimo 8 caracteres.")

        normalized_email = data.email.strip().lower()
        existing_user = self._user_repository.find_by_email(normalized_email)
        if existing_user is not None:
            raise UserAlreadyExistsError(normalized_email)

        roles_set = set(data.roles) if data.roles else {UserRole.NOVO_INTEGRANTE}
        password_hash = self._password_hasher.hash(data.password)

        user = User(
            name=data.name,
            email=normalized_email,
            password_hash=password_hash,
            roles=roles_set,
            academic_id=data.academic_id,
        )

        saved_user = self._user_repository.create(user)
        return UserOutput.from_entity(saved_user)
