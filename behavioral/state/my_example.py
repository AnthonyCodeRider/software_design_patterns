from __future__ import annotations

from typing import Protocol


class NodeState(Protocol):
    """State interface: the operations whose behaviour varies per role."""

    context: Node

    def on_enter(self) -> None:
        """Entry action, run by Node.transition_to right after the state is installed."""
        ...

    def tick(self) -> None: ...

    def receive_append_entries(self, term: int, leader_id: str, entries: list) -> None: ...

    def receive_request_vote(self, term: int, candidate_id: str) -> None: ...

    def receive_vote_response(self, term: int, voter_id: str, granted: bool) -> None: ...


class FollowerState:
    def __init__(self) -> None:
        self.context: Node = None  # type: ignore[assignment]
        self._election_timeout = 5  # Example timeout value
        self._time_since_last_heartbeat = 0

    def on_enter(self) -> None:
        self._time_since_last_heartbeat = 0

    def tick(self) -> None:
        """Handle clock tick for follower state."""
        self._time_since_last_heartbeat += 1
        if self._time_since_last_heartbeat >= self._election_timeout:
            print(f"Node {self.context.node_id}: Election timeout reached. Transitioning to Candidate state.")
            self.context.transition_to(CandidateState())

    def receive_append_entries(self, term: int, leader_id: str, entries: list) -> None:
        """Handle AppendEntries RPC from the leader.

        The context has already vetted the term, so this only does follower work.
        """
        print(f"Node {self.context.node_id}: Received AppendEntries from leader {leader_id}. Resetting election timeout.")
        self._time_since_last_heartbeat = 0
        # Process entries (not implemented for simplicity)

    def receive_request_vote(self, term: int, candidate_id: str) -> None:
        """Handle RequestVote RPC from a candidate."""
        # Granting is idempotent: a retried RequestVote from the candidate we
        # already backed must be granted again, or a lost response costs it a vote.
        if self.context.voted_for in (None, candidate_id):
            print(f"Node {self.context.node_id}: Granting vote to candidate {candidate_id} for term {term}.")
            self.context.voted_for = candidate_id
            self._time_since_last_heartbeat = 0  # don't challenge the candidate we just endorsed
            # Send vote granted response (not implemented for simplicity)
        else:
            print(f"Node {self.context.node_id}: Already voted for {self.context.voted_for} in term {term}. Rejecting {candidate_id}.")

    def receive_vote_response(self, term: int, voter_id: str, granted: bool) -> None:
        """Not running an election, so there is nothing to count.

        Reached either by a late reply to an election we already left, or by a
        reply whose higher term just stepped us down in Node._observe_term - so
        don't call it stale here, because in the second case it is the newest
        thing we have seen.
        """
        print(f"Node {self.context.node_id}: Not a candidate; ignoring vote response from {voter_id}.")


class CandidateState:
    def __init__(self) -> None:
        self.context: Node = None  # type: ignore[assignment]
        self._votes_received: set[str] = set()
        self._election_timeout = 5  # Example timeout value
        self._time_since_election_start = 0

    def on_enter(self) -> None:
        self.start_election()

    def start_election(self) -> None:
        """Start a new election."""
        self.context.current_term += 1
        self.context.voted_for = self.context.node_id
        self._votes_received = {self.context.node_id}  # Vote for self
        self._time_since_election_start = 0
        print(f"Node {self.context.node_id}: Starting election for term {self.context.current_term}.")
        # Send RequestVote RPCs to other nodes (not implemented for simplicity)
        # In a single-node cluster the self-vote is already a majority, so check
        # now rather than waiting for a response that will never arrive.
        self._check_quorum()

    def _check_quorum(self) -> None:
        if len(self._votes_received) >= self.context.quorum:
            print(f"Node {self.context.node_id}: Quorum reached. Transitioning to Leader state.")
            self.context.transition_to(LeaderState())

    def tick(self) -> None:
        """Handle clock tick for candidate state."""
        self._time_since_election_start += 1
        if self._time_since_election_start >= self._election_timeout:
            print(f"Node {self.context.node_id}: Election timeout reached with no winner. Starting new election.")
            # Go through transition_to so the split-vote self-edge is actually
            # walked, validated and logged, instead of mutating this instance.
            self.context.transition_to(CandidateState())

    def receive_append_entries(self, term: int, leader_id: str, entries: list) -> None:
        """A leader already exists for this term, so concede.

        A *higher* term never reaches here: the context steps us down to Follower
        first and dispatches to that state instead.
        """
        print(f"Node {self.context.node_id}: Leader {leader_id} won term {term}. Transitioning to Follower state.")
        self.context.transition_to(FollowerState())
        # Process entries (not implemented for simplicity)

    def receive_request_vote(self, term: int, candidate_id: str) -> None:
        """Handle RequestVote RPC from another candidate."""
        print(f"Node {self.context.node_id}: Already voted for self in term {term}. Rejecting {candidate_id}.")

    def receive_vote_response(self, term: int, voter_id: str, granted: bool) -> None:
        """Count a vote; a majority makes us leader.

        The context has already dropped stale terms and stepped us down on higher
        ones, so this reply belongs to the election we are currently running.
        """
        if not granted:
            return
        self._votes_received.add(voter_id)
        print(f"Node {self.context.node_id}: Vote granted by {voter_id} ({len(self._votes_received)}/{self.context.quorum} needed).")
        self._check_quorum()


class LeaderState:
    def __init__(self) -> None:
        self.context: Node = None  # type: ignore[assignment]
        self._heartbeat_interval = 2  # Example heartbeat interval
        self._time_since_last_heartbeat = 0

    def on_enter(self) -> None:
        # Assert leadership straight away rather than waiting for the first tick.
        self.send_heartbeats()
        self._time_since_last_heartbeat = 0

    def tick(self) -> None:
        """Handle clock tick for leader state."""
        self._time_since_last_heartbeat += 1
        if self._time_since_last_heartbeat >= self._heartbeat_interval:
            self.send_heartbeats()
            self._time_since_last_heartbeat = 0

    def send_heartbeats(self) -> None:
        """Send heartbeats to followers (not implemented for simplicity)."""
        print(f"Node {self.context.node_id}: Sending heartbeat to followers.")

    def receive_append_entries(self, term: int, leader_id: str, entries: list) -> None:
        """Two leaders cannot be elected in one term, so an equal term is
        impossible here - and a higher one already stepped us down in the context.
        """
        print(f"Node {self.context.node_id}: Ignoring AppendEntries from {leader_id} at term {term}; we lead that term.")

    def receive_request_vote(self, term: int, candidate_id: str) -> None:
        """Handle RequestVote RPC from a candidate."""
        print(f"Node {self.context.node_id}: Rejecting RequestVote from {candidate_id} at term {term}; we lead that term.")

    def receive_vote_response(self, term: int, voter_id: str, granted: bool) -> None:
        """The election is already won. Late votes change nothing."""
        print(f"Node {self.context.node_id}: Received late vote response from {voter_id}. Ignoring.")


class Node:
    """Context class"""

    # Encoding the state graph makes the illegal edges fail loudly.
    # A leader never becomes a candidate directly; it must step down first.
    _LEGAL_TRANSITIONS: dict[str, set[str]] = {
        "FollowerState": {"CandidateState"},
        "CandidateState": {"FollowerState", "CandidateState", "LeaderState"},
        "LeaderState": {"FollowerState"},
    }

    def __init__(self, node_id: str, state: NodeState, cluster_size: int = 3) -> None:
        self._id = node_id
        self._cluster_size = cluster_size
        # Data that must survive every role change lives on the context, never on
        # a state object: the term and the vote outlive the role that recorded them.
        self._current_term = 0
        self._voted_for: str | None = None
        self._log: list = []
        self._commit_index = 0
        self._state: NodeState | None = None
        self.transition_to(state)

    @property
    def node_id(self) -> str:
        return self._id

    @property
    def role(self) -> str:
        return type(self._state).__name__

    @property
    def quorum(self) -> int:
        return self._cluster_size // 2 + 1

    @property
    def current_term(self) -> int:
        return self._current_term

    @current_term.setter
    def current_term(self, term: int) -> None:
        self._current_term = term

    @property
    def voted_for(self) -> str | None:
        return self._voted_for

    @voted_for.setter
    def voted_for(self, candidate_id: str | None) -> None:
        self._voted_for = candidate_id

    @property
    def log(self) -> list:
        return self._log

    def transition_to(self, state: NodeState) -> None:
        """Transition to a new state, then run its entry action."""
        old = type(self._state).__name__ if self._state is not None else None
        new = type(state).__name__
        if new not in self._LEGAL_TRANSITIONS:
            raise RuntimeError(f"Node {self._id}: unknown state {new}")
        if old is None:
            # A node boots as a follower and has to win an election like anyone
            # else, so the initial state is validated rather than trusted.
            if new != "FollowerState":
                raise RuntimeError(f"Node {self._id}: a node must start as FollowerState, not {new}")
        elif new not in self._LEGAL_TRANSITIONS.get(old, set()):
            raise RuntimeError(f"Node {self._id}: illegal transition {old} -> {new}")
        print(f"Node {self._id}: Transitioning to {new}.")
        # A fresh state instance per transition means role-scoped data (vote
        # tallies, timers) cannot leak into the next role, so no on_exit is needed.
        self._state = state
        self._state.context = self
        self._state.on_enter()

    def _observe_term(self, term: int) -> bool:
        """Apply the cross-cutting term rule before any state sees the message.

        This is the one thing the State pattern does not organise for you: the
        rule holds in every role, so duplicating it across the three states is
        how they drift apart. Keeping it on the context is what etcd's raft does
        in Step(), which normalises the term before delegating to the role.

        Returns False if the message is stale and should be dropped.
        """
        if term < self._current_term:
            return False
        if term > self._current_term:
            self._current_term = term
            self._voted_for = None  # a new term unbinds any vote cast in the old one
            if not isinstance(self._state, FollowerState):
                print(f"Node {self._id}: Observed higher term {term}. Stepping down.")
                self.transition_to(FollowerState())
        return True

    def tick(self) -> None:
        """Simulate a clock tick, which may trigger state transitions."""
        self._state.tick()

    def receive_append_entries(self, term: int, leader_id: str, entries: list) -> None:
        """Handle AppendEntries RPC from the leader."""
        if not self._observe_term(term):
            print(f"Node {self._id}: Received AppendEntries with stale term {term}. Ignoring.")
            return
        # Re-read self._state: _observe_term may have just replaced it.
        self._state.receive_append_entries(term, leader_id, entries)

    def receive_request_vote(self, term: int, candidate_id: str) -> None:
        """Handle RequestVote RPC from a candidate."""
        if not self._observe_term(term):
            print(f"Node {self._id}: Received RequestVote with stale term {term}. Ignoring.")
            return
        self._state.receive_request_vote(term, candidate_id)

    def receive_vote_response(self, term: int, voter_id: str, granted: bool) -> None:
        """Handle a reply to a RequestVote RPC we sent."""
        if not self._observe_term(term):
            print(f"Node {self._id}: Received vote response for stale term {term}. Ignoring.")
            return
        self._state.receive_vote_response(term, voter_id, granted)


if __name__ == "__main__":
    # Create a node in the Follower state, in a 3-node cluster (quorum = 2).
    node = Node("n1", FollowerState(), cluster_size=3)

    print("\n-- No heartbeats arrive: the follower times out and stands for election --")
    for _ in range(5):
        node.tick()

    print("\n-- A peer grants its vote: quorum reached --")
    node.receive_vote_response(term=node.current_term, voter_id="n2", granted=True)

    print("\n-- The same tick now means 'send heartbeats' instead of 'count down' --")
    for _ in range(4):
        node.tick()

    print("\n-- A leader at a higher term appears: step down --")
    node.receive_append_entries(term=node.current_term + 1, leader_id="n3", entries=["entry1"])

    print(f"\nFinal: role={node.role} term={node.current_term} voted_for={node.voted_for}")
