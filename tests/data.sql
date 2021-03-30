INSERT INTO clubs (name, email, points)
VALUES
  ('club1', 'name1@club1.com', 10),
  ('club2', 'name2@club2.com', 1),
  ('club3', 'name3@club3.com', 15);


INSERT INTO competitions (name, date, number_of_places)
VALUES
  ('competition1', '2022-01-01 00:00:00', 11),
  ('competition2', '2020-01-01 00:00:00', 2),
  ('competition3', '2022-02-03 00:00:00', 2),
  ('competition4', '2022-04-02 00:00:00', 5);

INSERT INTO bookings (club_id, competition_id, places_booked)
VALUES
  (2, 2, 5),
  (1, 4, 8);