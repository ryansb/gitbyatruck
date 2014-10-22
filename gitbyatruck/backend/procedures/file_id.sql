CREATE OR REPLACE FUNCTION maybe_file(
    fpath text,
    repo_id integer
) RETURNS integer AS $$
DECLARE
    fid integer;
BEGIN
    -- Now for the fun part, to share knowledge with other developers
    IF EXISTS(SELECT id FROM files
        WHERE repo = repo_id
        AND name = fpath)
    THEN
        SELECT id INTO fid FROM files
        WHERE repo = repo_id
        AND name = fpath;
        RETURN fid;
    ELSE
        INSERT INTO files (repo, name) VALUES (
            repo_id,
            fpath
        ) RETURNING id INTO fid;
    END IF;
    RETURN fid;
END;

$$ LANGUAGE plpgsql;
