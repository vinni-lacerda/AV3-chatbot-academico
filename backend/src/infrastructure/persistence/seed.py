"""Seed idempotente de usuários fictícios de demonstração utilizando os casos de uso da aplicação."""

from application.dtos.auth_dtos import RegisterUserInput, UserOutput
from application.use_cases.register_user import RegisterUserUseCase
from domain.entities.user import UserRole
from domain.exceptions.domain_exceptions import UserAlreadyExistsError
from infrastructure.container.composition_root import DependencyContainer
from infrastructure.persistence.demo import DEMO_PASSWORD, seed_demo

DEFAULT_SEED_PASSWORD = DEMO_PASSWORD

INITIAL_USERS_SEED: list[RegisterUserInput] = [
    RegisterUserInput(
        name="Lia Monteiro · Demo",
        email="lia@demo.example",
        password=DEFAULT_SEED_PASSWORD,
        roles=[UserRole.INTEGRANTE],
        academic_id="DEMO-0001",
    ),
    RegisterUserInput(
        name="Beto Alves · Demo",
        email="beto@demo.example",
        password=DEFAULT_SEED_PASSWORD,
        roles=[UserRole.RESPONSAVEL],
        academic_id="DEMO-0002",
    ),
    RegisterUserInput(
        name="Ada Wong - Demo",
        email="ada@demo.example",
        password=DEFAULT_SEED_PASSWORD,
        roles=[UserRole.NOVO_INTEGRANTE],
        academic_id="DEMO-0003",
    ),
]


def seed_initial_users(register_use_case: RegisterUserUseCase) -> list[UserOutput]:
    """Insere os integrantes fictícios de demonstração de forma idempotente (ignora se já existirem)."""
    created_users: list[UserOutput] = []
    for seed_input in INITIAL_USERS_SEED:
        try:
            created = register_use_case.execute(seed_input)
            created_users.append(created)
        except UserAlreadyExistsError:
            continue
    return created_users


if __name__ == "__main__":
    container = DependencyContainer()
    seed_demo(container)
    print("Seed de demonstração fictícia concluído.")
