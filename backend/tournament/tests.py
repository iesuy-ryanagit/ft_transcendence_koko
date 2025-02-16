from django.test import TestCase
from django.contrib.auth import get_user_model
from tournament.models import Tournament, Match
from tournament.services import create_tournament_schedule, process_match_result

User = get_user_model()

class TournamentServicesTest(TestCase):
    def setUp(self):
        # Create some test users
        self.users = [
            User.objects.create(username=f"user{i}", password="password")
            for i in range(1, 5)
        ]

        # Create two tournaments:
        # * tournament_double will have 4 participants (yielding 2 matches in round 1)
        #   to test creation of the next round.
        # * tournament_small will have 2 participants (yielding 1 match) that completes the tournament.
        self.tournament_double = Tournament.objects.create(name="Double Round Tournament", status="pending", max_players=4)
        self.tournament_small = Tournament.objects.create(name="Small Tournament", status="pending", max_players=2)

        # Assume Tournament has a ManyToMany field named 'participants'
        self.tournament_double.participants.add(*self.users)
        self.tournament_small.participants.add(self.users[0], self.users[1])

    def test_create_tournament_schedule(self):
        """
        Test that create_tournament_schedule() shuffles and pairs participants,
        creates matches with round 1, and updates the tournament status.
        """
        matches = create_tournament_schedule(self.tournament_double)
        # With 4 participants, we expect 2 matches.
        self.assertEqual(len(matches), 2)
        self.tournament_double.refresh_from_db()
        self.assertEqual(self.tournament_double.status, "ongoing")
        for match in matches:
            self.assertEqual(match.tournament, self.tournament_double)
            self.assertEqual(match.round, 1)
            self.assertIn(match.player1, self.users)
            self.assertIn(match.player2, self.users)

    def test_process_match_result_next_round_creates_new_match(self):
        """
        Test that process_match_result(), when called on all matches in the round,
        generates a new round match pairing the winners from round 1.
        """
        # Create the schedule for a tournament with 4 participants (2 matches in round 1).
        matches = create_tournament_schedule(self.tournament_double)

        # Process the result for the first match.
        result1 = process_match_result(matches[0], winner=matches[0].player1, score="1-0")
        # Since the other match is still pending, we expect a "Next round pending" message.
        self.assertEqual(result1, "Next round pending")

        # Process the result for the second match.
        result2 = process_match_result(matches[1], winner=matches[1].player1, score="1-0")
        # Now that both matches are completed, process_match_result should create the next round.
        # It will return a list of newly created match(es).
        self.assertIsInstance(result2, list)
        # For 2 winners, we expect 1 new match.
        self.assertEqual(len(result2), 1)

        new_match = result2[0]
        self.assertEqual(new_match.tournament, self.tournament_double)
        self.assertEqual(new_match.round, 2)
        # The new match players should be exactly the winners of the round 1 matches.
        expected_players = {matches[0].player1, matches[1].player1}
        actual_players = {new_match.player1, new_match.player2}
        self.assertEqual(expected_players, actual_players)

    def test_process_match_result_completes_tournament(self):
        """
        Test that process_match_result() completes the tournament when the round has one match.
        In this case, processing the match result should mark the tournament as completed,
        assign the winner, and return the message "Tournament completed".
        """
        # Create schedule for a tournament with 2 participants (1 match)
        matches = create_tournament_schedule(self.tournament_small)
        self.assertEqual(len(matches), 1)

        # Process the match result. With only one match completed in the round,
        # the tournament should be completed.
        result = process_match_result(matches[0], winner=matches[0].player1, score="2-1")
        self.assertEqual(result, "Tournament completed")

        self.tournament_small.refresh_from_db()
        self.assertEqual(self.tournament_small.status, "completed")
        self.assertEqual(self.tournament_small.winner, matches[0].player1)