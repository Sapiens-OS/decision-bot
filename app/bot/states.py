from aiogram.fsm.state import State, StatesGroup


class NewDecisionStates(StatesGroup):
    """States for creating a new decision"""

    waiting_for_problem = State()
    waiting_for_context = State()
    waiting_for_selection = State()
    waiting_for_confirmation = State()


class OutcomeStates(StatesGroup):
    """States for adding outcome"""

    waiting_for_feedback = State()
    waiting_for_score = State()
