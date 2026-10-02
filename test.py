
import sys
sys.path.append('./fg_core')

from fg_core.db.session import create_all, get_session
from fg_core.models.fluid_event import FluidEvent
from fg_core.utils.timestamps import utc_now
sys.path.append('./fg-intake-service')
from models.fluid_event import IntakeResponse, event_payload

create_all()
db = next(get_session())

event = FluidEvent(
    event_type='manual_intake',
    occurred_at=utc_now(),
    payload=event_payload('user1', {'volume_ml': 100})
)
db.add(event)
db.commit()
db.refresh(event)

try:
    resp = IntakeResponse(event=event, recognized_volume_ml=100, source='manual')
    print('SUCCESS')
except Exception as e:
    import traceback
    traceback.print_exc()

