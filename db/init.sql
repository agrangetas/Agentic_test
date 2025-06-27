-- Script d'initialisation de la base de données pour l'agent d'investigation d'entreprises
-- Version: 1.0
-- Date: 2024

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des sources de données
CREATE TABLE sources_donnees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom TEXT NOT NULL,
    type TEXT CHECK (type IN ('inpi', 'web', 'news', 'api')),
    fiabilite_score FLOAT DEFAULT 0.5 CHECK (fiabilite_score >= 0.0 AND fiabilite_score <= 1.0),
    derniere_maj TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table principale des entreprises
CREATE TABLE entreprises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom TEXT NOT NULL,
    nom_normalise TEXT,
    variantes_nom TEXT[],
    siren TEXT UNIQUE,
    url TEXT,
    date_creation DATE,
    secteur TEXT,
    ca_estime BIGINT,
    taille_entreprise TEXT CHECK (taille_entreprise IN ('TPE', 'PME', 'ETI', 'GE')),
    resume TEXT,
    score_confiance FLOAT DEFAULT 0.5 CHECK (score_confiance >= 0.0 AND score_confiance <= 1.0),
    date_maj TIMESTAMP DEFAULT NOW(),
    source_principale UUID REFERENCES sources_donnees(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour les recherches fréquentes
CREATE INDEX idx_entreprises_nom ON entreprises(nom);
CREATE INDEX idx_entreprises_nom_normalise ON entreprises(nom_normalise);
CREATE INDEX idx_entreprises_siren ON entreprises(siren);
CREATE INDEX idx_entreprises_secteur ON entreprises(secteur);

-- Table des documents INPI
CREATE TABLE documents_inpi (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entreprise_id UUID REFERENCES entreprises(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    contenu JSONB NOT NULL,
    date_maj TIMESTAMP DEFAULT NOW(),
    score_confiance FLOAT DEFAULT 0.8 CHECK (score_confiance >= 0.0 AND score_confiance <= 1.0),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour recherches JSONB
CREATE INDEX idx_documents_inpi_contenu ON documents_inpi USING GIN (contenu);
CREATE INDEX idx_documents_inpi_entreprise ON documents_inpi(entreprise_id);

-- Table des liens capitalistiques
CREATE TABLE liens_capitaux (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entreprise_source UUID REFERENCES entreprises(id) ON DELETE CASCADE,
    entreprise_cible UUID REFERENCES entreprises(id) ON DELETE CASCADE,
    type_lien TEXT CHECK (type_lien IN ('filiale', 'participation', 'partenariat', 'acquisition')),
    pourcentage FLOAT CHECK (pourcentage >= 0.0 AND pourcentage <= 100.0),
    montant BIGINT,
    date_lien DATE,
    source_id UUID REFERENCES sources_donnees(id),
    score_confiance FLOAT DEFAULT 0.5 CHECK (score_confiance >= 0.0 AND score_confiance <= 1.0),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(entreprise_source, entreprise_cible, type_lien)
);

-- Index pour les requêtes de liens
CREATE INDEX idx_liens_source ON liens_capitaux(entreprise_source);
CREATE INDEX idx_liens_cible ON liens_capitaux(entreprise_cible);
CREATE INDEX idx_liens_type ON liens_capitaux(type_lien);

-- Table des actualités
CREATE TABLE actualites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entreprise_id UUID REFERENCES entreprises(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    type TEXT,
    titre TEXT,
    resume TEXT,
    impact_estime TEXT CHECK (impact_estime IN ('positif', 'negatif', 'neutre')),
    source TEXT,
    url_source TEXT,
    score_confiance FLOAT DEFAULT 0.3 CHECK (score_confiance >= 0.0 AND score_confiance <= 1.0),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour les actualités
CREATE INDEX idx_actualites_entreprise ON actualites(entreprise_id);
CREATE INDEX idx_actualites_date ON actualites(date DESC);
CREATE INDEX idx_actualites_type ON actualites(type);

-- Table des conflits de données
CREATE TABLE conflits_donnees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entreprise_id UUID REFERENCES entreprises(id) ON DELETE CASCADE,
    champ_conflit TEXT NOT NULL,
    valeur_source1 TEXT,
    valeur_source2 TEXT,
    source1_id UUID REFERENCES sources_donnees(id),
    source2_id UUID REFERENCES sources_donnees(id),
    statut TEXT DEFAULT 'non_resolu' CHECK (statut IN ('non_resolu', 'resolu', 'ignore')),
    resolution TEXT,
    date_detection TIMESTAMP DEFAULT NOW(),
    date_resolution TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour gestion des conflits
CREATE INDEX idx_conflits_entreprise ON conflits_donnees(entreprise_id);
CREATE INDEX idx_conflits_statut ON conflits_donnees(statut);

-- Table des sessions d'exploration
CREATE TABLE sessions_exploration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entreprise_initiale TEXT NOT NULL,
    parametres JSONB,
    statut TEXT DEFAULT 'en_cours' CHECK (statut IN ('en_cours', 'termine', 'erreur', 'annule')),
    nb_entreprises_trouvees INTEGER DEFAULT 0,
    date_debut TIMESTAMP DEFAULT NOW(),
    date_fin TIMESTAMP,
    resume_final TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour les sessions
CREATE INDEX idx_sessions_statut ON sessions_exploration(statut);
CREATE INDEX idx_sessions_date_debut ON sessions_exploration(date_debut DESC);

-- Table des logs d'exploration
CREATE TABLE exploration_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions_exploration(id) ON DELETE CASCADE,
    entreprise_id UUID REFERENCES entreprises(id) ON DELETE SET NULL,
    agent TEXT NOT NULL,
    input JSONB,
    output JSONB,
    duree_execution INTEGER, -- en secondes
    statut TEXT CHECK (statut IN ('success', 'error', 'timeout')),
    error_message TEXT,
    date_executed TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour les logs
CREATE INDEX idx_logs_session ON exploration_logs(session_id);
CREATE INDEX idx_logs_agent ON exploration_logs(agent);
CREATE INDEX idx_logs_statut ON exploration_logs(statut);
CREATE INDEX idx_logs_date ON exploration_logs(date_executed DESC);

-- Table des métriques d'agents
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,
    session_id UUID REFERENCES sessions_exploration(id) ON DELETE CASCADE,
    execution_time FLOAT NOT NULL,
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    success BOOLEAN NOT NULL,
    error_count INTEGER DEFAULT 0,
    cache_hit BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Index pour métriques
CREATE INDEX idx_metrics_agent ON agent_metrics(agent_name);
CREATE INDEX idx_metrics_session ON agent_metrics(session_id);
CREATE INDEX idx_metrics_timestamp ON agent_metrics(timestamp DESC);

-- Table des entités temporaires (pour le graph)
CREATE TABLE temp_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions_exploration(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL,
    entity_data JSONB NOT NULL,
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    created_by TEXT, -- agent qui a créé l'entité
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '24 hours')
);

-- Index pour entités temporaires
CREATE INDEX idx_temp_entities_session ON temp_entities(session_id);
CREATE INDEX idx_temp_entities_expires ON temp_entities(expires_at);

-- Fonction pour nettoyer les entités expirées
CREATE OR REPLACE FUNCTION cleanup_expired_entities()
RETURNS void AS $$
BEGIN
    DELETE FROM temp_entities WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Fonction pour mettre à jour les timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers pour updated_at
CREATE TRIGGER update_sources_donnees_updated_at BEFORE UPDATE ON sources_donnees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entreprises_updated_at BEFORE UPDATE ON entreprises FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_inpi_updated_at BEFORE UPDATE ON documents_inpi FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_liens_capitaux_updated_at BEFORE UPDATE ON liens_capitaux FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_actualites_updated_at BEFORE UPDATE ON actualites FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conflits_donnees_updated_at BEFORE UPDATE ON conflits_donnees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sessions_exploration_updated_at BEFORE UPDATE ON sessions_exploration FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Vue pour statistiques rapides
CREATE VIEW stats_entreprises AS
SELECT 
    COUNT(*) as total_entreprises,
    COUNT(DISTINCT secteur) as nb_secteurs,
    AVG(score_confiance) as score_confiance_moyen,
    COUNT(CASE WHEN ca_estime IS NOT NULL THEN 1 END) as entreprises_avec_ca
FROM entreprises;

-- Vue pour les liens entre entreprises
CREATE VIEW vue_liens_entreprises AS
SELECT 
    l.id,
    l.type_lien,
    l.pourcentage,
    l.montant,
    e1.nom as entreprise_source_nom,
    e1.siren as entreprise_source_siren,
    e2.nom as entreprise_cible_nom,
    e2.siren as entreprise_cible_siren,
    l.score_confiance,
    l.created_at
FROM liens_capitaux l
JOIN entreprises e1 ON l.entreprise_source = e1.id
JOIN entreprises e2 ON l.entreprise_cible = e2.id;

-- Insertion des sources de données par défaut
INSERT INTO sources_donnees (nom, type, fiabilite_score) VALUES
('INPI Registry', 'inpi', 0.95),
('Web Scraping', 'web', 0.7),
('News API', 'news', 0.6),
('Internal API', 'api', 0.85),
('Manual Entry', 'api', 0.8);

-- Fonction pour créer une nouvelle session
CREATE OR REPLACE FUNCTION create_exploration_session(
    p_entreprise_initiale TEXT,
    p_parametres JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    session_id UUID;
BEGIN
    INSERT INTO sessions_exploration (entreprise_initiale, parametres)
    VALUES (p_entreprise_initiale, p_parametres)
    RETURNING id INTO session_id;
    
    RETURN session_id;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour finaliser une session
CREATE OR REPLACE FUNCTION finalize_exploration_session(
    p_session_id UUID,
    p_statut TEXT,
    p_resume_final TEXT DEFAULT NULL
) RETURNS void AS $$
BEGIN
    UPDATE sessions_exploration 
    SET 
        statut = p_statut,
        date_fin = NOW(),
        resume_final = p_resume_final
    WHERE id = p_session_id;
END;
$$ LANGUAGE plpgsql;

-- Commentaires pour documentation
COMMENT ON TABLE sources_donnees IS 'Sources de données avec scoring de fiabilité';
COMMENT ON TABLE entreprises IS 'Table principale des entreprises avec données normalisées';
COMMENT ON TABLE documents_inpi IS 'Documents INPI stockés en JSONB';
COMMENT ON TABLE liens_capitaux IS 'Relations capitalistiques entre entreprises';
COMMENT ON TABLE actualites IS 'Actualités des entreprises avec impact estimé';
COMMENT ON TABLE conflits_donnees IS 'Conflits détectés entre sources de données';
COMMENT ON TABLE sessions_exploration IS 'Sessions d''exploration avec paramètres';
COMMENT ON TABLE exploration_logs IS 'Logs détaillés des exécutions d''agents';

-- Affichage des statistiques de création
SELECT 'Base de données initialisée avec succès' as status;
SELECT schemaname, tablename, tableowner 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename; 