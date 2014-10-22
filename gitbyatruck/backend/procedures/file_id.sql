CREATE OR REPLACE FUNCTION maybe_file(
    fpath text,
    repo_id integer
) RETURNS integer AS $$
DECLARE
    fid integer;
BEGIN
    -- either creates a file or returns the existing ID
    INSERT INTO files (repo, name) (
    SELECT repo_id AS repo, fpath AS name
        WHERE NOT EXISTS (
            SELECT 1 FROM files
                WHERE repo = repo_id AND name = fpath
            )
    ) RETURNING id INTO fid;
    return fid;
END;

$$ LANGUAGE plpgsql;
