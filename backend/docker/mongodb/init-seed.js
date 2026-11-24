const dbName = process.env.MONGO_INITDB_DATABASE || "passa_o_bastao_demo";
const targetDb = db.getSiblingDB(dbName);

targetDb.users.createIndex({ email: 1 }, { unique: true });
targetDb.users.createIndex({ id: 1 }, { unique: true });
