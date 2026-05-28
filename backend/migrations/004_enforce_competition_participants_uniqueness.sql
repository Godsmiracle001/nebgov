-- Ensure one participation row per (competition, user) pair.
ALTER TABLE competition_participants
DROP CONSTRAINT IF EXISTS competition_participants_competition_id_user_id_key;

ALTER TABLE competition_participants
ADD CONSTRAINT competition_participants_competition_id_user_id_key
UNIQUE (competition_id, user_id);
