CREATE OR REPLACE FUNCTION ingest_change() RETURNS TRIGGER AS $new_change$
    DECLARE
        adjustment          integer;
        churn               integer;
        churn_constant      float;
        new_knowledge       float;
    BEGIN
        --
        -- Only runs on insert
        -- TODO: handle UPDATE and DELETE
        -- result is ignored since this is an AFTER trigger
        --
        churn_constant = 0.1;
        adjustment = NEW.added - NEW.deleted;
        IF adjustment > 0 THEN
            -- Add unique knowledge for the contributor
            UPDATE knol SET knowledge = knowledge + adjustment
                WHERE committer = NEW.committer
                AND changed_file = NEW.changed_file
                AND repo = NEW.repo
                AND individual = TRUE;
            if found THEN
                -- The update worked, do nothing
            ELSE
                -- Update didn't work, insert new node
                INSERT INTO knol(committer, repo, changed_file, knowledge, individual) VALUES (
                    NEW.committer,
                    NEW.repo,
                    NEW.changed_file,
                    adjustment,
                    TRUE
                );
            END IF;
            UPDATE file SET total_knowledge = total_knowledge + adjustment
                WHERE id = NEW.changed_file
                AND repo = NEW.repo;
        END IF;
        IF adjustment < 0 THEN
            -- Destroy knowledge for developers who have worked on the file by destroying 
            UPDATE knol SET knowledge = knowledge * (1.0 - adjustment/knowledge)
                WHERE changed_file = NEW.changed_file
                AND repo = NEW.repo
                AND knowledge > 0;
            UPDATE file SET total_knowledge = total_knowledge - adjustment
                WHERE id = NEW.changed_file
                AND repo = NEW.repo;
        END IF;


        -- Now for the fun part, to share knowledge with other developers
        churn = LEAST(NEW.added, NEW.deleted);
        if churn = 0 THEN
            RETURN NULL;
        END IF;
        -- There was no churn, so we bail.
        new_knowledge = churn * churn_constant;
        UPDATE knol SET knowledge = knowledge - new_knowledge
            WHERE changed_file = NEW.changed_file
            AND committer != NEW.committer
            AND repo = NEW.repo
            AND individual = TRUE;
        UPDATE knol SET knowledge = knowledge + new_knowledge
            WHERE changed_file = NEW.changed_file
            AND repo = NEW.repo
            AND committer = NEW.committer;
        RETURN NULL;
    END;
$new_change$ LANGUAGE plpgsql;


CREATE TRIGGER new_change
AFTER INSERT ON change
    FOR EACH ROW EXECUTE PROCEDURE ingest_change();
