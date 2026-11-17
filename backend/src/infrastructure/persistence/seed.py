"""Seed idempotente de usuários iniciais utilizando os casos de uso da aplicação."""

from application.dtos.auth_dtos import RegisterUserInput, UserOutput
from application.use_cases.register_user import RegisterUserUseCase
from domain.entities.user import UserRole
from domain.exceptions.domain_exceptions import UserAlreadyExistsError
from infrastructure.container.composition_root import DependencyContainer

DEFAULT_SEED_PASSWORD = "PassaOBastao123!"

INITIAL_USERS_SEED: list[RegisterUserInput] = [
    RegisterUserInput(
        name="Vinicius Lacerda Santos",
        email="vinicius@universidade.edu.br",
        password=DEFAULT_SEED_PASSWORD,
        roles=[UserRole.INTEGRANTE, UserRole.RESPONSAVEL],
        academic_id="12725210686",
    ),
    RegisterUserInput(
        name="Hiago da Silva Lins Goncalves",
        email="hiago@universidade.edu.br",
        password=DEFAULT_SEED_PASSWORD,
        roles=[UserRole.INTEGRANTE],
        academic_id="12525163385",
    ),
    RegisterUserInput(
        name="Leoni Lucas Mascarenhas Silva",
        email="leoni@universidade.edu.br",
        password=DEFAULT_SEED_PASSWORD,
        roles=[UserRole.INTEGRANTE, UserRole.RESPONSAVEL],
        academic_id="12725156424",
    ),
    RegisterUserInput(
        name="Rafael Stolf Silva",
        email="rafael@universidade.edu.br",
        password=DEFAULT_SEED_PASSWORD,
        roles=[UserRole.NOVO_INTEGRANTE],
        academic_id="122515186",
    ),
    RegisterUserInput(
        name="Pedro Murilo Pereira",
        email="pedro@universidade.edu.br",
        password=DEFAULT_SEED_PASSWORD,
        roles=[UserRole.NOVO_INTEGRANTE],
        academic_id="122519964",
    ),
]


def seed_initial_users(register_use_case: RegisterUserUseCase) -> list[UserOutput]:
    """Insere os integrantes iniciais de forma idempotente (ignora se já existirem)."""
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
    inserted = seed_initial_users(container.register_user_use_case)
    print(f"Seed concluído. Novos usuários inseridos: {len(inserted)}.")
