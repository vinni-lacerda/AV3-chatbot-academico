const dbName = process.env.MONGO_INITDB_DATABASE || "passa_o_bastao";
const targetDb = db.getSiblingDB(dbName);

targetDb.users.createIndex({ email: 1 }, { unique: true });
targetDb.users.createIndex({ id: 1 }, { unique: true });

const defaultPasswordHash = "$2b$12$KQgZmq7V8Gju9je/Ert52OrXGVwJYPWOz8vkBrmpieNv3UXIy9tKq";
const now = new Date();

const initialUsers = [
  {
    id: "00000000-0000-4000-8000-000000000001",
    name: "Vinicius Lacerda Santos",
    email: "vinicius@universidade.edu.br",
    password_hash: defaultPasswordHash,
    roles: ["integrante", "responsavel"],
    academic_id: "12725210686",
    is_active: true,
    created_at: now,
    updated_at: now
  },
  {
    id: "00000000-0000-4000-8000-000000000002",
    name: "Hiago da Silva Lins Goncalves",
    email: "hiago@universidade.edu.br",
    password_hash: defaultPasswordHash,
    roles: ["integrante"],
    academic_id: "12525163385",
    is_active: true,
    created_at: now,
    updated_at: now
  },
  {
    id: "00000000-0000-4000-8000-000000000003",
    name: "Leoni Lucas Mascarenhas Silva",
    email: "leoni@universidade.edu.br",
    password_hash: defaultPasswordHash,
    roles: ["integrante", "responsavel"],
    academic_id: "12725156424",
    is_active: true,
    created_at: now,
    updated_at: now
  },
  {
    id: "00000000-0000-4000-8000-000000000004",
    name: "Rafael Stolf Silva",
    email: "rafael@universidade.edu.br",
    password_hash: defaultPasswordHash,
    roles: ["novo_integrante"],
    academic_id: "122515186",
    is_active: true,
    created_at: now,
    updated_at: now
  },
  {
    id: "00000000-0000-4000-8000-000000000005",
    name: "Pedro Murilo Pereira",
    email: "pedro@universidade.edu.br",
    password_hash: defaultPasswordHash,
    roles: ["novo_integrante"],
    academic_id: "122519964",
    is_active: true,
    created_at: now,
    updated_at: now
  }
];

initialUsers.forEach((user) => {
  targetDb.users.updateOne(
    { email: user.email },
    { $setOnInsert: user },
    { upsert: true }
  );
});
