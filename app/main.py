
from fastapi import FastAPI, Request
from random import randint
import logging

from opentelemetry import trace, metrics

# Setup tracer and meter
tracer = trace.get_tracer("diceroller.tracer")
meter = metrics.get_meter("diceroller.meter")

# Create a counter for roll values
roll_counter = meter.create_counter(
    "dice.rolls",
    description="The number of rolls by roll value",
)

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/rolldice")
async def roll_dice(player: str = None):
    with tracer.start_as_current_span("roll") as roll_span:
        result = randint(1, 6)
        roll_span.set_attribute("roll.value", result)
        roll_counter.add(1, {"roll.value": str(result)})
        if player:
            logger.warning("%s is rolling the dice: %s", player, result)
        else:
            logger.warning("Anonymous player is rolling the dice: %s", result)
        return {"result": result}
