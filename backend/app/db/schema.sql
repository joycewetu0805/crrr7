-- =====================================================================
-- FRAUDSHIELD - Schema de base de donnees
-- Moteur : SQLite 3 (fichier local, aucun serveur a installer)
-- Compatible Windows : executable avec DB Browser for SQLite,
-- ou en ligne de commande via "sqlite3 fraudshield.db < schema.sql"
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- Table 1 : comptes
-- Represente le titulaire (client/carte) qui effectue des transactions.
-- Necessaire pour comparer une transaction au comportement habituel
-- du compte (montant moyen, pays habituel, etc.).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS comptes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_compte   TEXT NOT NULL UNIQUE,
    nom_titulaire   TEXT NOT NULL,
    email           TEXT,
    pays            TEXT NOT NULL,
    statut_compte   TEXT NOT NULL DEFAULT 'actif'
                        CHECK (statut_compte IN ('actif', 'suspendu')),
    date_creation   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- Table 2 : transactions
-- Chaque transaction brute soumise au systeme, rattachee a un compte.
-- Contient uniquement les faits (ce qui s'est passe), pas le jugement.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    compte_id           INTEGER NOT NULL,
    montant             REAL NOT NULL CHECK (montant > 0),
    devise              TEXT NOT NULL DEFAULT 'EUR',
    type_transaction    TEXT NOT NULL
                            CHECK (type_transaction IN (
                                'achat_en_ligne', 'paiement_pos',
                                'retrait_atm', 'virement'
                            )),
    canal               TEXT NOT NULL
                            CHECK (canal IN ('web', 'mobile', 'pos', 'atm')),
    marchand            TEXT,
    pays_transaction    TEXT NOT NULL,
    date_transaction    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (compte_id) REFERENCES comptes (id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Table 3 : analyses_fraude
-- Resultat produit par le modele ML pour UNE transaction donnee.
-- Separee de "transactions" pour ne jamais melanger le fait brut
-- (la transaction) et le jugement du modele (le score, le statut).
-- Relation 1-1 avec transactions (garantie par UNIQUE sur transaction_id).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analyses_fraude (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id      INTEGER NOT NULL UNIQUE,
    score_fraude        REAL NOT NULL CHECK (score_fraude BETWEEN 0 AND 1),
    statut              TEXT NOT NULL
                            CHECK (statut IN ('legitime', 'suspect', 'fraude')),
    modele_version      TEXT NOT NULL DEFAULT 'v1',
    facteurs_influents  TEXT,
    date_analyse        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Index utiles aux requetes du dashboard (historique, filtres, stats)
-- ---------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_transactions_compte_id
    ON transactions (compte_id);

CREATE INDEX IF NOT EXISTS idx_transactions_date
    ON transactions (date_transaction);

CREATE INDEX IF NOT EXISTS idx_analyses_statut
    ON analyses_fraude (statut);
