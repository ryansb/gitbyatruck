CREATE OR REPLACE FUNCTION churn_knowledge(
    added integer,
    deleted integer,
    changed_fid integer,
    repo integer,
    committer integer,
) RETURNS NULL AS $$
    DECLARE
        adjustment          integer;
        churn               integer;
        churn_constant      float;
        new_knowledge       float;
    BEGIN
        -- Now for the fun part, to share knowledge with other developers
        churn = LEAST(added, deleted);
        if churn = 0 THEN
            RETURN NULL;
        END IF;

        churn_constant = 0.1;

        -- There was no churn, so we bail.
        new_knowledge = churn * churn_constant;
        UPDATE knol SET knowledge = knowledge - new_knowledge
            WHERE changed_file = changed_fid
            AND committer != committer
            AND repo = repo
            AND individual = TRUE;
        UPDATE knol SET knowledge = knowledge + new_knowledge
            WHERE changed_file = changed_fid
            AND repo = repo
            AND committer = committer;
        RETURN NULL;
    END;
$new_change$ LANGUAGE plpgsql;
