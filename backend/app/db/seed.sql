-- =====================================================================
-- FRAUDSHIELD - Donnees fictives de demonstration
-- A executer APRES schema.sql :
--   sqlite3 fraudshield.db < schema.sql
--   sqlite3 fraudshield.db < seed.sql
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- 5 comptes clients
-- ---------------------------------------------------------------------
INSERT INTO comptes (numero_compte, nom_titulaire, email, pays, statut_compte, date_creation) VALUES
('FR76-1234-5678-9012', 'Jean Dupont',     'jean.dupont@email.fr',    'France',   'actif',    '2024-02-10 09:00:00'),
('FR76-2345-6789-0123', 'Marie Laurent',   'marie.laurent@email.fr',  'France',   'actif',    '2024-05-22 11:30:00'),
('BE68-3456-7890-1234', 'Ahmed Ben Ali',   'ahmed.benali@email.be',   'Belgique', 'actif',    '2023-11-03 14:15:00'),
('FR76-4567-8901-2345', 'Sophie Martin',   'sophie.martin@email.fr',  'France',   'actif',    '2025-01-18 08:45:00'),
('FR76-5678-9012-3456', 'Karim Haddad',    'karim.haddad@email.fr',   'France',   'suspendu', '2022-07-09 16:20:00');

-- ---------------------------------------------------------------------
-- 10 transactions : majorite normales, quelques-unes suspectes
-- (montant eleve, pays inhabituel, heure atypique) pour tester
-- la variete des scores une fois le modele ML branche.
-- ---------------------------------------------------------------------
INSERT INTO transactions (compte_id, montant, devise, type_transaction, canal, marchand, pays_transaction, date_transaction) VALUES
(1,   45.90, 'EUR', 'achat_en_ligne', 'web',    'Amazon',            'France',   '2026-08-10 14:23:00'),
(1,   12.50, 'EUR', 'paiement_pos',   'pos',    'Boulangerie Paul',  'France',   '2026-08-11 08:15:00'),
(2,   89.99, 'EUR', 'achat_en_ligne', 'mobile', 'Zalando',           'France',   '2026-08-11 20:05:00'),
(2,  250.00, 'EUR', 'retrait_atm',    'atm',    'DAB Gare de Lyon',  'France',   '2026-08-12 03:47:00'),
(3, 1500.00, 'EUR', 'virement',       'web',    NULL,                'Nigeria',  '2026-08-12 02:13:00'),
(3,   35.20, 'EUR', 'paiement_pos',   'pos',    'Carrefour',         'Belgique', '2026-08-10 17:30:00'),
(4,   67.00, 'EUR', 'achat_en_ligne', 'mobile', 'Fnac',              'France',   '2026-08-13 11:22:00'),
(4, 4200.00, 'EUR', 'virement',       'web',    NULL,                'Russie',   '2026-08-13 04:02:00'),
(5,   15.00, 'EUR', 'paiement_pos',   'pos',    'Cafe de Paris',     'France',   '2026-08-09 09:00:00'),
(5,  980.00, 'EUR', 'retrait_atm',    'atm',    'DAB inconnu',       'Roumanie', '2026-08-14 01:15:00');

-- ---------------------------------------------------------------------
-- Analyses de fraude correspondantes (une par transaction).
-- Ces valeurs simulent ce que le modele ML produira une fois branche :
-- elles servent uniquement a tester l'affichage du dashboard.
-- ---------------------------------------------------------------------
INSERT INTO analyses_fraude (transaction_id, score_fraude, statut, modele_version, facteurs_influents, date_analyse) VALUES
(1,  0.04, 'legitime', 'v1', '{"montant_faible":0.6,"marchand_connu":0.4}',                                    '2026-08-10 14:23:01'),
(2,  0.02, 'legitime', 'v1', '{"montant_faible":0.7,"pays_habituel":0.3}',                                     '2026-08-11 08:15:01'),
(3,  0.07, 'legitime', 'v1', '{"marchand_connu":0.5,"canal_habituel":0.5}',                                    '2026-08-11 20:05:01'),
(4,  0.55, 'suspect',  'v1', '{"heure_atypique":0.5,"type_retrait":0.3,"montant_moyen":0.2}',                  '2026-08-12 03:47:01'),
(5,  0.93, 'fraude',   'v1', '{"pays_inhabituel":0.4,"montant_eleve":0.35,"heure_atypique":0.25}',             '2026-08-12 02:13:01'),
(6,  0.11, 'legitime', 'v1', '{"montant_faible":0.6,"pays_habituel":0.4}',                                     '2026-08-10 17:30:01'),
(7,  0.05, 'legitime', 'v1', '{"marchand_connu":0.6,"montant_faible":0.4}',                                    '2026-08-13 11:22:01'),
(8,  0.97, 'fraude',   'v1', '{"montant_eleve":0.45,"pays_inhabituel":0.35,"heure_atypique":0.20}',            '2026-08-13 04:02:01'),
(9,  0.03, 'legitime', 'v1', '{"montant_faible":0.7,"marchand_connu":0.3}',                                    '2026-08-09 09:00:01'),
(10, 0.88, 'fraude',   'v1', '{"compte_suspendu":0.4,"pays_inhabituel":0.35,"heure_atypique":0.25}',           '2026-08-14 01:15:01');
