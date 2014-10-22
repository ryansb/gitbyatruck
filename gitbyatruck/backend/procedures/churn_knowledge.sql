CREATE OR REPLACE FUNCTION churn_knowledge(
    added integer,
    deleted integer,
    changed_fid integer,
    repo_id integer,
    committer_id integer
) RETURNS void AS $$
DECLARE
    churn               integer;
    churn_constant      float;
    new_knowledge       float;
BEGIN
    -- Now for the fun part, to share knowledge with other developers
    churn = LEAST(added, deleted);
    if churn = 0 THEN
        RETURN;
    END IF;

    churn_constant = 0.1;

    -- There was no churn, so we bail.
    new_knowledge = churn * churn_constant;
    UPDATE knol SET knowledge = knowledge - new_knowledge
        WHERE changed_file = changed_fid
        AND committer != committer_id
        AND repo = repo_id
        AND individual = TRUE;
    UPDATE knol SET knowledge = knowledge + new_knowledge
        WHERE changed_file = changed_fid
        AND repo = repo_id
        AND committer = committer_id;
END;

$$ LANGUAGE plpgsql;
