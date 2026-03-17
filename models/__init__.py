from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

from .user import User
from .poem import Poem
from .learning_record import LearningRecord
from .exercise import Exercise, UserExerciseRecord
from .qa_record import QARecord
from .attention_tracking import AttentionTracking
from .learning_session import LearningSession, InteractionEvent
