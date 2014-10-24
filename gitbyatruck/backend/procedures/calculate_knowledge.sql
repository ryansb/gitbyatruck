CREATE OR REPLACE FUNCTION ingest_change() RETURNS TRIGGER AS $new_change$
    DECLARE
        adjustment          integer;
        changed_fid         integer;
    BEGIN
        --
        -- Only runs on insert
        -- TODO: handle UPDATE and DELETE
        -- result is ignored since this is an AFTER trigger
        --
        INSERT INTO files (repo, name) (
            -- see also file_id.sql. By not having it a separate
            -- function call it shaves ~15% off the call time.
            SELECT NEW.repo AS repo, NEW.changed_file AS name
            WHERE NOT EXISTS (
                SELECT 1 FROM files
                WHERE repo = NEW.repo AND name = NEW.changed_file
            )
        ) RETURNING id INTO changed_fid;

        adjustment = NEW.added - NEW.deleted;
        IF adjustment > 0 THEN
            -- Add unique knowledge for the contributor
            UPDATE knol SET knowledge = knowledge + adjustment
                WHERE committer = NEW.committer
                AND changed_file = changed_fid
                AND repo = NEW.repo;
            if found THEN
                -- The update worked, do nothing
            ELSE
                -- Update didn't work, insert new node
                INSERT INTO knol (committer, repo, changed_file, knowledge) VALUES (
                    NEW.committer,
                    NEW.repo,
                    changed_fid,
                    adjustment
                );
            END IF;
            UPDATE files SET total_knowledge = total_knowledge + adjustment
                WHERE id = changed_fid
                AND repo = NEW.repo;
        END IF;
        IF adjustment < 0 THEN
            -- Destroy knowledge for developers who have worked on the file by destroying 
            UPDATE knol SET knowledge = knowledge * (1.0 - adjustment/knowledge)
                WHERE changed_file = changed_fid
                AND repo = NEW.repo
                AND knowledge > 0;
            UPDATE files SET total_knowledge = total_knowledge - adjustment
                WHERE id = changed_fid
                AND repo = NEW.repo;
        END IF;

        -- Now for the fun part, to share knowledge with other developers
        PERFORM churn_knowledge(
            NEW.added,
            NEW.deleted,
            changed_fid,
            NEW.repo,
            NEW.committer);

        RETURN NULL;
    END;
$new_change$ LANGUAGE plpgsql;


CREATE TRIGGER new_change
AFTER INSERT ON change
    FOR EACH ROW EXECUTE PROCEDURE ingest_change();
